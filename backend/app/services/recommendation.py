"""
推荐服务（增强版）
集成：两级缓存、黑名单过滤、多样性控制
"""
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from typing import List, Dict, Any, Optional
import random
import json
from datetime import datetime, timedelta

from app.models.sql import Book, User, Interaction, SearchLog, RecommendationCache, RecommendationHistory
from app.services.llm_service import llm_service
from app.services.cache_service import CacheService
from app.services.blacklist_service import BlacklistService
from app.services.diversity_service import DiversityService
from app.core.config import settings
from sqlalchemy import func


class RecommendationService:
    """增强版推荐服务"""
    
    def __init__(self, db: Session, neo4j: Neo4jSession):
        self.db = db
        self.neo4j = neo4j
        
        # 初始化服务
        self.cache_service = CacheService(db)
        self.blacklist_service = BlacklistService(db, neo4j)
        self.diversity_service = DiversityService(db)

    def get_recommendations(
        self, 
        user_id: int, 
        limit: int = 10,
        enable_diversity: bool = True,
        diversity_mode: str = "quota",  # quota, mmr, none
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        混合推荐：图谱路径 + 人口统计 + 偏好 + 热门
        支持两级缓存和多样性控制
        
        Args:
            user_id: 用户ID
            limit: 推荐数量
            enable_diversity: 是否启用多样性控制
            diversity_mode: 多样性模式 (quota/mmr/none)
            force_refresh: 是否强制刷新缓存
        """
        print(f"DEBUG: Starting recommendation for user_id={user_id}")
        
        # 0. 检查缓存（先L1后L2）
        if not force_refresh:
            cached = self.cache_service.get_recommendations(user_id)
            if cached:
                print(f"DEBUG: Cache hit for user_id={user_id}")
                return self._restore_recommendations(cached, limit)
        
        # 1. 获取用户信息和黑名单
        user = self.db.query(User).filter(User.id == user_id).first()
        pref_cats = []
        if user and user.preferred_categories:
            pref_cats = [c.strip() for c in user.preferred_categories.split(",") if c.strip()]
        
        # 获取黑名单
        blacklist = self.blacklist_service.get_blacklist_for_neo4j_query(user_id)
        disliked_categories = self.blacklist_service.get_disliked_categories(user_id)
        disliked_authors = self.blacklist_service.get_disliked_authors(user_id)
        
        # 2. 获取用户历史
        recent_interactions = self.db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(Interaction.created_at.desc()).limit(10).all()
        
        history_book_ids = [i.book_id for i in recent_interactions]
        history_titles = [i.book.title for i in recent_interactions if i.book]

        recommendations = []
        seen_books = set(history_book_ids) | set(blacklist)  # 排除历史和黑名单
        
        # 3. 搜索关联推荐
        recommendations.extend(
            self._get_search_based_recommendations(user_id, seen_books, limit)
        )
        for r in recommendations:
            seen_books.add(r["book"].id)
        
        # 4. 图谱推荐
        graph_candidates = self._get_graph_candidates(
            user_id, pref_cats, blacklist, 
            list(disliked_categories), list(disliked_authors),
            seen_books, limit * 3
        )
        
        # 5. LLM重排序
        if graph_candidates:
            refined = self._llm_rerank(graph_candidates, history_titles, blacklist)
            for r in refined:
                if r["book"].id not in seen_books:
                    recommendations.append(r)
                    seen_books.add(r["book"].id)
        
        # 6. 应用多样性控制
        if enable_diversity and len(recommendations) > 0:
            recommendations = self._apply_diversity(
                user_id, recommendations, diversity_mode, limit
            )
        
        # 7. 热门书籍兜底
        if len(recommendations) < limit:
            popular = self._get_popular_fallback(seen_books, limit - len(recommendations))
            recommendations.extend(popular)
        
        # 8. 保存缓存
        self._save_to_cache(user_id, recommendations)
        
        # 9. 更新推荐历史（用于滑动窗口）
        self._update_recommendation_history(user_id, recommendations)
        
        return recommendations[:limit]

    def _restore_recommendations(self, cached: List[Dict], limit: int) -> List[Dict[str, Any]]:
        """从缓存恢复推荐结果"""
        recommendations = []
        for item in cached:
            book = self.db.query(Book).filter(Book.id == item["book_id"]).first()
            if book:
                recommendations.append({
                    "book": book,
                    "score": item["score"],
                    "reason": item["reason"],
                    "tags": item.get("tags", [])
                })
        return recommendations[:limit]

    def _get_search_based_recommendations(
        self, user_id: int, seen_books: set, limit: int
    ) -> List[Dict[str, Any]]:
        """基于搜索历史的推荐"""
        recommendations = []
        
        recent_searches = self.db.query(SearchLog).filter(
            SearchLog.user_id == user_id
        ).order_by(SearchLog.created_at.desc()).limit(3).all()
        
        for search in recent_searches:
            if len(recommendations) >= limit // 3:  # 搜索推荐占比最多1/3
                break
            
            query_str = f"%{search.query}%"
            matched_books = self.db.query(Book).filter(
                (Book.title.like(query_str)) |
                (Book.author.like(query_str))
            ).limit(2).all()
            
            for book in matched_books:
                if book.id in seen_books:
                    continue
                
                recommendations.append({
                    "book": book,
                    "score": 0.9,
                    "reason": f"基于您最近搜索关键词【{search.query}】的精准推荐。",
                    "tags": ["搜索关联"],
                    "category_name": book.category.name if book.category else "Unknown",
                    "author": book.author
                })
                seen_books.add(book.id)
        
        return recommendations

    def _get_graph_candidates(
        self, 
        user_id: int, 
        pref_cats: List[str],
        blacklist: List[int],
        disliked_categories: List[str],
        disliked_authors: List[str],
        seen_books: set,
        limit: int
    ) -> List[Dict[str, Any]]:
        """从知识图谱获取候选书籍"""
        candidates = []
        
        # 增强的Cypher查询，包含负反馈过滤
        cypher_query = """
        MATCH (u:User {id: $user_id})
        
        // 1. 内容推荐路径
        OPTIONAL MATCH (u)-[:CLICKED|RATED|COLLECTED]->(b:Book)-[:BELONGS_TO|WRITTEN_BY]->(node)<-[:BELONGS_TO|WRITTEN_BY]-(rec_content:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_content)
          AND NOT (u)-[:DISLIKES]->(rec_content)
          AND NOT rec_content.id IN $blacklist
        
        // 2. 协同过滤路径
        OPTIONAL MATCH (u)-[:CLICKED|RATED|COLLECTED]->(b2:Book)<-[:CLICKED|RATED|COLLECTED]-(peer:User)-[:CLICKED|RATED|COLLECTED]->(rec_collab:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_collab) 
          AND NOT (u)-[:DISLIKES]->(rec_collab)
          AND peer.id <> u.id
          AND NOT rec_collab.id IN $blacklist
        
        // 3. 偏好类别路径
        OPTIONAL MATCH (rec_pref:Book)-[:BELONGS_TO]->(c_pref:Category)
        WHERE c_pref.name IN $pref_cats 
          AND NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_pref)
          AND NOT (u)-[:DISLIKES]->(rec_pref)
          AND NOT rec_pref.id IN $blacklist
        
        // 4. 人口统计路径
        OPTIONAL MATCH (peer_demog:User)
        WHERE peer_demog.id <> u.id 
          AND peer_demog.gender = u.gender 
          AND abs(peer_demog.age - u.age) <= 5
        OPTIONAL MATCH (peer_demog)-[:CLICKED|RATED|COLLECTED]->(rec_demog:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_demog)
          AND NOT (u)-[:DISLIKES]->(rec_demog)
          AND NOT rec_demog.id IN $blacklist
        
        // 合并结果
        WITH rec_content, rec_collab, rec_pref, rec_demog, node, count(peer) as peer_strength, count(peer_demog) as demog_strength, c_pref
        
        WITH 
            CASE 
                WHEN rec_collab IS NOT NULL THEN rec_collab 
                WHEN rec_demog IS NOT NULL THEN rec_demog
                WHEN rec_pref IS NOT NULL THEN rec_pref
                ELSE rec_content 
            END AS final_rec,
            CASE 
                WHEN rec_collab IS NOT NULL THEN 'collab'
                WHEN rec_demog IS NOT NULL THEN 'demog'
                WHEN rec_pref IS NOT NULL THEN 'pref'
                ELSE 'content'
            END AS source_type,
            node, peer_strength, demog_strength, c_pref
        
        WHERE final_rec IS NOT NULL
        
        // 计算评分
        OPTIONAL MATCH (final_rec)<-[r:RATED]-()
        WITH final_rec, source_type, node, peer_strength, demog_strength, c_pref, avg(r.score) as avg_rating
        
        // 检查是否有负反馈关系需要降权
        OPTIONAL MATCH (final_rec)-[:BELONGS_TO]->(cat:Category)
        OPTIONAL MATCH (final_rec)-[:WRITTEN_BY]->(author:Author)
        
        RETURN DISTINCT final_rec.id AS book_id, 
               final_rec.title AS title,
               source_type,
               CASE 
                 WHEN source_type = 'content' AND node IS NOT NULL THEN node.name 
                 WHEN source_type = 'pref' AND c_pref IS NOT NULL THEN c_pref.name
                 WHEN source_type = 'demog' THEN toString(demog_strength)
                 ELSE toString(peer_strength)
               END AS reason_val,
               1.0 + 
               (CASE WHEN avg_rating IS NOT NULL THEN avg_rating * 0.5 ELSE 0 END) +
               (CASE WHEN source_type = 'collab' THEN 3 + (peer_strength * 0.5) ELSE 0 END) +
               (CASE WHEN source_type = 'demog' THEN 2.5 + (demog_strength * 0.3) ELSE 0 END) +
               (CASE WHEN source_type = 'pref' THEN 3.5 ELSE 0 END)
               AS score,
               cat.name AS category_name,
               author.name AS author_name
        ORDER BY score DESC
        LIMIT $limit
        """
        
        try:
            results = self.neo4j.run(
                cypher_query, 
                user_id=user_id, 
                pref_cats=pref_cats,
                blacklist=blacklist,
                limit=limit
            )
            
            for record in results:
                b_id = record["book_id"]
                if b_id in seen_books:
                    continue
                
                book_obj = self.db.query(Book).filter(Book.id == b_id).first()
                if not book_obj:
                    continue
                
                cat_name = record["category_name"] or (book_obj.category.name if book_obj.category else "Unknown")
                author_name = record["author_name"] or book_obj.author or "Unknown"
                
                # 应用类别/作者降权
                score = record["score"]
                if cat_name in disliked_categories:
                    score *= 0.5
                if author_name in disliked_authors:
                    score *= 0.5
                
                candidates.append({
                    "book": book_obj,
                    "book_id": book_obj.id,
                    "title": book_obj.title,
                    "author": author_name,
                    "category_name": cat_name,
                    "score": score,
                    "source_type": record["source_type"],
                    "reason_val": record["reason_val"]
                })
                
        except Exception as e:
            print(f"DEBUG: Neo4j Query failed: {e}")
        
        return candidates

    def _llm_rerank(
        self, 
        candidates: List[Dict], 
        history_titles: List[str],
        blacklist: List[int]
    ) -> List[Dict[str, Any]]:
        """使用LLM重排序"""
        recommendations = []
        
        # 准备LLM输入
        candidates_for_llm = []
        candidate_map = {}
        
        for c in candidates[:15]:  # 只考虑前15个
            cand_info = {
                "title": c["title"],
                "author": c.get("author", "Unknown"),
                "category": c.get("category_name", "Unknown"),
                "reason_val": str(c.get("reason_val", "")),
                "source_type": c.get("source_type", "content")
            }
            candidates_for_llm.append(cand_info)
            candidate_map[c["title"]] = c
        
        if not candidates_for_llm:
            return recommendations
        
        try:
            print(f"DEBUG: Calling LLM refinement with {len(candidates_for_llm)} candidates...")
            refined_list = llm_service.refine_recommendations(history_titles, candidates_for_llm)
            print(f"DEBUG: LLM refinement complete, got {len(refined_list)} items")
            
            for item in refined_list:
                title = item.get("book_title", "")
                matched_key = next((k for k in candidate_map if k in title or title in k), None)
                
                if matched_key:
                    orig = candidate_map[matched_key]
                    recommendations.append({
                        "book": orig["book"],
                        "score": item.get("score", orig["score"]),
                        "reason": item.get("reason", f"为您推荐 {orig['title']}"),
                        "tags": ["AI 推荐", orig.get("source_type", "")],
                        "category_name": orig.get("category_name"),
                        "author": orig.get("author")
                    })
                    
        except Exception as e:
            print(f"DEBUG: LLM refinement failed: {e}")
            # 回退：直接使用候选
            for c in candidates[:10]:
                recommendations.append({
                    "book": c["book"],
                    "score": c["score"],
                    "reason": f"根据您的兴趣为您推荐。",
                    "tags": [c.get("source_type", "推荐")],
                    "category_name": c.get("category_name"),
                    "author": c.get("author")
                })
        
        return recommendations

    def _apply_diversity(
        self, 
        user_id: int,
        recommendations: List[Dict],
        mode: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """应用多样性控制"""
        
        if mode == "none":
            return recommendations
        
        # 分析用户兴趣
        user_profile = self.diversity_service.analyze_user_categories(user_id)
        
        # 转换为多样性服务需要的格式
        candidates = []
        for r in recommendations:
            candidates.append({
                "book": r["book"],
                "book_id": r["book"].id,
                "score": r["score"],
                "reason": r["reason"],
                "tags": r.get("tags", []),
                "category_name": r.get("category_name") or (r["book"].category.name if r["book"].category else "Unknown"),
                "author": r.get("author") or r["book"].author or "Unknown"
            })
        
        if mode == "quota":
            # 类别配额
            result = self.diversity_service.apply_category_quota(
                candidates, user_profile, limit
            )
        elif mode == "mmr":
            # MMR算法
            result = self.diversity_service.mmr_rerank(
                candidates, [], limit, settings.MMR_LAMBDA
            )
        else:
            result = candidates
        
        # 转换回原格式
        final = []
        for r in result:
            final.append({
                "book": r["book"],
                "score": r["score"],
                "reason": r["reason"],
                "tags": r.get("tags", [])
            })
        
        return final

    def _get_popular_fallback(self, seen_books: set, limit: int) -> List[Dict[str, Any]]:
        """热门书籍兜底"""
        recommendations = []
        
        # 过滤条件：排除测试数据
        # 1. 封面URL以/static/开头（真实书籍）
        # 2. 或者书籍ID小于1000（假设测试数据ID较大）
        # 3. 并且有真实评分记录
        popular_books = self.db.query(Book).filter(
            # 过滤掉明显的测试数据
            (Book.cover_url.like('/static/%')) | (Book.id < 1000)
        ).order_by(
            Book.average_rating.desc()
        ).limit(limit * 3 + len(seen_books)).all()
        
        for book in popular_books:
            if book.id not in seen_books and len(recommendations) < limit:
                # 额外检查：排除明显的假数据（标题太短或像测试数据）
                if book.title and len(book.title) > 3 and not book.title in ['Prof.', 'Mrs.', 'Miss.', 'Mr.', 'Dr.']:
                    recommendations.append({
                        "book": book,
                        "score": 0.5,
                        "reason": "为您推荐当前热门的高评分书籍。",
                        "tags": ["热门精选"]
                    })
                    seen_books.add(book.id)
        
        return recommendations

    def _save_to_cache(self, user_id: int, recommendations: List[Dict]):
        """保存到缓存"""
        try:
            cache_data = []
            for rec in recommendations:
                cache_data.append({
                    "book_id": rec["book"].id,
                    "score": rec["score"],
                    "reason": rec["reason"],
                    "tags": rec.get("tags", [])
                })
            
            self.cache_service.set_recommendations(user_id, cache_data)
            print(f"DEBUG: Saved {len(cache_data)} recommendations to cache for user_id={user_id}")
            
        except Exception as e:
            print(f"DEBUG: Failed to save cache: {e}")

    def _update_recommendation_history(self, user_id: int, recommendations: List[Dict]):
        """更新推荐历史（用于滑动窗口去重）"""
        try:
            book_ids = [r["book"].id for r in recommendations]
            
            history = self.db.query(RecommendationHistory).filter(
                RecommendationHistory.user_id == user_id
            ).first()
            
            if history:
                existing = json.loads(history.recommended_books)
                # 保持窗口大小
                combined = existing + book_ids
                history.recommended_books = json.dumps(combined[-history.window_size:])
                history.updated_at = datetime.now()
            else:
                history = RecommendationHistory(
                    user_id=user_id,
                    recommended_books=json.dumps(book_ids),
                    window_size=50
                )
                self.db.add(history)
            
            self.db.commit()
            
        except Exception as e:
            print(f"DEBUG: Failed to update recommendation history: {e}")

    def get_cold_start_recommendations(
        self, 
        categories: List[str], 
        moods: List[str], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        冷启动推荐（基于问卷）
        """
        recommendations = []
        seen_books = set()
        
        cypher_query = """
        MATCH (b:Book)-[:BELONGS_TO]->(c:Category)
        WHERE c.name IN $categories
        RETURN b.id AS book_id, c.name AS category_name
        LIMIT $limit_candidate
        """
        
        try:
            results = list(self.neo4j.run(
                cypher_query, 
                categories=categories, 
                limit_candidate=limit * 4
            ))
            random.shuffle(results)
            
            for record in results:
                b_id = record["book_id"]
                category_name = record["category_name"]
                
                if b_id in seen_books:
                    continue
                
                book_obj = self.db.query(Book).filter(Book.id == b_id).first()
                if not book_obj:
                    continue
                
                mood_text = moods[0] if moods else "探索"
                explanation = f"根据您对【{category_name}】的兴趣以及【{mood_text}】的偏好，为您特别推荐。"
                
                recommendations.append({
                    "book": book_obj,
                    "score": 0.8,
                    "reason": explanation,
                    "tags": [category_name] + moods
                })
                seen_books.add(b_id)
                
                if len(recommendations) >= limit:
                    break
                    
        except Exception as e:
            print(f"Cold start Neo4j query failed: {e}")
        
        # 热门兜底（排除测试数据）
        if len(recommendations) < limit:
            popular_books = self.db.query(Book).filter(
                (Book.cover_url.like('/static/%')) | (Book.id < 1000)
            ).order_by(
                Book.average_rating.desc()
            ).limit((limit - len(recommendations)) * 3).all()
            
            for book in popular_books:
                if book.id in seen_books:
                    continue
                # 排除明显的假数据
                if book.title and len(book.title) > 3 and not book.title in ['Prof.', 'Mrs.', 'Miss.', 'Mr.', 'Dr.']:
                    recommendations.append({
                        "book": book,
                        "score": 0.5,
                        "reason": "新用户必读的高分经典。",
                        "tags": ["热门推荐"]
                    })
                    seen_books.add(book.id)
                    if len(recommendations) >= limit:
                        break
        
        return recommendations
