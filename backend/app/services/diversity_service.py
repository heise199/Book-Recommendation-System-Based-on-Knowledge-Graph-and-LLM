"""
多样性控制服务
实现类别配额、MMR算法等多样性控制策略
"""
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.sql import Interaction, Book, Category


class DiversityService:
    """多样性控制服务"""
    
    def __init__(self, db: Session = None):
        self.db = db
    
    def set_db(self, db: Session):
        """设置数据库会话"""
        self.db = db
    
    # ==================== 用户兴趣分析 ====================
    
    def analyze_user_categories(self, user_id: int) -> Dict[str, Any]:
        """
        分析用户历史交互的类别分布
        
        Returns:
            {
                "primary_categories": ["科幻", "历史"],  # 主类别（40%）
                "secondary_categories": ["悬疑"],        # 次类别（30%）
                "explore_categories": ["心理学"],        # 探索类别（20%）
                "category_distribution": [
                    {"category_name": "科幻", "count": 10, "ratio": 0.5},
                    ...
                ],
                "total_interactions": 20
            }
        """
        if not self.db:
            return self._empty_profile(user_id)
        
        try:
            # 查询用户交互的书籍类别分布
            results = self.db.query(
                Category.name,
                func.count(Interaction.id).label("count")
            ).join(
                Book, Book.category_id == Category.id
            ).join(
                Interaction, Interaction.book_id == Book.id
            ).filter(
                Interaction.user_id == user_id
            ).group_by(
                Category.name
            ).order_by(
                func.count(Interaction.id).desc()
            ).all()
            
            if not results:
                return self._empty_profile(user_id)
            
            # 计算总交互数
            total = sum(r.count for r in results)
            
            # 构建分布
            distribution = []
            for r in results:
                distribution.append({
                    "category_name": r.name,
                    "count": r.count,
                    "ratio": r.count / total if total > 0 else 0
                })
            
            # 分类：主类别、次类别、探索类别
            primary = []
            secondary = []
            explore = []
            
            cumulative_ratio = 0
            for d in distribution:
                if cumulative_ratio < settings.DIVERSITY_PRIMARY_RATIO:
                    primary.append(d["category_name"])
                elif cumulative_ratio < settings.DIVERSITY_PRIMARY_RATIO + settings.DIVERSITY_SECONDARY_RATIO:
                    secondary.append(d["category_name"])
                cumulative_ratio += d["ratio"]
            
            # 探索类别：用户没有交互过但相关的类别
            all_categories = self.db.query(Category.name).all()
            interacted_categories = set(d["category_name"] for d in distribution)
            explore = [c.name for c in all_categories if c.name not in interacted_categories][:3]
            
            return {
                "user_id": user_id,
                "primary_categories": primary,
                "secondary_categories": secondary,
                "explore_categories": explore,
                "category_distribution": distribution,
                "total_interactions": total
            }
            
        except Exception as e:
            print(f"User category analysis error: {e}")
            return self._empty_profile(user_id)
    
    def _empty_profile(self, user_id: int) -> Dict[str, Any]:
        """返回空的用户画像"""
        return {
            "user_id": user_id,
            "primary_categories": [],
            "secondary_categories": [],
            "explore_categories": [],
            "category_distribution": [],
            "total_interactions": 0
        }
    
    # ==================== 类别配额算法 ====================
    
    def apply_category_quota(
        self, 
        candidates: List[Dict[str, Any]], 
        user_profile: Dict[str, Any],
        total_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        按类别配额分配推荐书籍
        
        配额分配：
        - 主类别：40% (4本)
        - 次类别：30% (3本)
        - 探索类别：20% (2本)
        - 热门类别：10% (1本)
        
        Args:
            candidates: 候选书籍列表，每个元素需要包含 category_name 和 score
            user_profile: 用户兴趣画像
            total_limit: 总推荐数量
            
        Returns:
            按配额分配后的推荐列表
        """
        primary_cats = set(user_profile.get("primary_categories", []))
        secondary_cats = set(user_profile.get("secondary_categories", []))
        explore_cats = set(user_profile.get("explore_categories", []))
        
        # 计算各类别配额
        primary_quota = max(1, int(total_limit * settings.DIVERSITY_PRIMARY_RATIO))
        secondary_quota = max(1, int(total_limit * settings.DIVERSITY_SECONDARY_RATIO))
        explore_quota = max(1, int(total_limit * settings.DIVERSITY_EXPLORE_RATIO))
        popular_quota = total_limit - primary_quota - secondary_quota - explore_quota
        
        # 按类别分组候选
        primary_candidates = []
        secondary_candidates = []
        explore_candidates = []
        popular_candidates = []
        
        for c in candidates:
            cat = c.get("category_name") or c.get("category", "")
            if cat in primary_cats:
                primary_candidates.append(c)
            elif cat in secondary_cats:
                secondary_candidates.append(c)
            elif cat in explore_cats:
                explore_candidates.append(c)
            else:
                popular_candidates.append(c)
        
        # 按分数排序
        for group in [primary_candidates, secondary_candidates, explore_candidates, popular_candidates]:
            group.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 按配额选择
        result = []
        result.extend(primary_candidates[:primary_quota])
        result.extend(secondary_candidates[:secondary_quota])
        result.extend(explore_candidates[:explore_quota])
        result.extend(popular_candidates[:popular_quota])
        
        # 如果配额未满，从其他组补充
        selected_ids = {c.get("book_id") or c.get("id") for c in result}
        remaining = total_limit - len(result)
        
        if remaining > 0:
            all_remaining = [c for c in candidates 
                          if (c.get("book_id") or c.get("id")) not in selected_ids]
            all_remaining.sort(key=lambda x: x.get("score", 0), reverse=True)
            result.extend(all_remaining[:remaining])
        
        return result[:total_limit]
    
    # ==================== MMR算法 ====================
    
    def mmr_rerank(
        self,
        candidates: List[Dict[str, Any]],
        selected: List[Dict[str, Any]] = None,
        limit: int = 10,
        lambda_param: float = None
    ) -> List[Dict[str, Any]]:
        """
        使用MMR算法重排序
        
        MMR(b) = λ × Relevance(b) - (1-λ) × max[Similarity(b, s) for s in S]
        
        Args:
            candidates: 候选书籍列表
            selected: 已选择的书籍列表
            limit: 选择数量
            lambda_param: 权衡参数（0-1），越大越重视相关性
            
        Returns:
            MMR重排序后的推荐列表
        """
        if lambda_param is None:
            lambda_param = settings.MMR_LAMBDA
        
        if not candidates:
            return []
        
        selected = selected or []
        result = list(selected)
        remaining = [c for c in candidates if c not in selected]
        
        while len(result) < limit and remaining:
            best_score = float("-inf")
            best_candidate = None
            
            for candidate in remaining:
                relevance = candidate.get("score", 0)
                
                # 计算与已选书籍的最大相似度
                max_sim = 0
                for s in result:
                    sim = self._calculate_similarity(candidate, s)
                    max_sim = max(max_sim, sim)
                
                # MMR分数
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_candidate = candidate
            
            if best_candidate:
                result.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break
        
        return result[:limit]
    
    def _calculate_similarity(self, book1: Dict, book2: Dict) -> float:
        """
        计算两本书的相似度
        
        综合相似度 = 0.5 × 类别相似度 + 0.3 × 作者相似度 + 0.2 × 标签相似度
        """
        cat_sim = self._category_similarity(book1, book2)
        author_sim = self._author_similarity(book1, book2)
        tag_sim = self._tag_similarity(book1, book2)
        
        return 0.5 * cat_sim + 0.3 * author_sim + 0.2 * tag_sim
    
    def _category_similarity(self, book1: Dict, book2: Dict) -> float:
        """类别相似度"""
        cat1 = book1.get("category_name") or book1.get("category", "")
        cat2 = book2.get("category_name") or book2.get("category", "")
        return 1.0 if cat1 and cat1 == cat2 else 0.0
    
    def _author_similarity(self, book1: Dict, book2: Dict) -> float:
        """作者相似度"""
        author1 = book1.get("author", "")
        author2 = book2.get("author", "")
        return 0.8 if author1 and author1 == author2 else 0.0
    
    def _tag_similarity(self, book1: Dict, book2: Dict) -> float:
        """标签相似度（Jaccard）"""
        tags1 = set(book1.get("tags", []))
        tags2 = set(book2.get("tags", []))
        
        if not tags1 or not tags2:
            return 0.0
        
        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)
        
        return intersection / union if union > 0 else 0.0
    
    # ==================== 滑动窗口去重 ====================
    
    def apply_sliding_window(
        self,
        user_id: int,
        candidates: List[Dict[str, Any]],
        window_size: int = 50,
        category_limit: int = 5,
        author_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        应用滑动窗口去重
        
        Args:
            user_id: 用户ID
            candidates: 候选书籍
            window_size: 窗口大小（最近N次推荐）
            category_limit: 类别频次限制
            author_limit: 作者频次限制
            
        Returns:
            过滤后的候选列表
        """
        if not self.db:
            return candidates
        
        from app.models.sql import RecommendationHistory
        import json
        
        try:
            # 获取推荐历史
            history = self.db.query(RecommendationHistory).filter(
                RecommendationHistory.user_id == user_id
            ).first()
            
            if not history:
                return candidates
            
            recent_books = json.loads(history.recommended_books)[-window_size:]
            recent_book_ids = set(recent_books)
            
            # 统计类别和作者频次
            category_counts = defaultdict(int)
            author_counts = defaultdict(int)
            
            for book_id in recent_books:
                book = self.db.query(Book).filter(Book.id == book_id).first()
                if book:
                    if book.category:
                        category_counts[book.category.name] += 1
                    if book.author:
                        author_counts[book.author] += 1
            
            # 过滤候选
            result = []
            for c in candidates:
                book_id = c.get("book_id") or c.get("id")
                category = c.get("category_name") or c.get("category", "")
                author = c.get("author", "")
                
                # 排除最近推荐过的
                if book_id in recent_book_ids:
                    continue
                
                # 检查类别频次
                if category_counts[category] >= category_limit:
                    c["score"] = c.get("score", 0) * 0.5  # 降权
                
                # 检查作者频次
                if author_counts[author] >= author_limit:
                    c["score"] = c.get("score", 0) * 0.5  # 降权
                
                result.append(c)
            
            return result
            
        except Exception as e:
            print(f"Sliding window error: {e}")
            return candidates
    
    # ==================== 多样性指标计算 ====================
    
    def calculate_diversity_metrics(
        self, 
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        计算推荐结果的多样性指标
        
        Returns:
            {
                "category_entropy": 1.5,      # 类别熵
                "author_coverage": 0.8,       # 作者覆盖率
                "year_diversity": 10.5,       # 出版年份标准差
                "overall_score": 0.75         # 综合多样性分数
            }
        """
        import math
        
        if not recommendations:
            return {"category_entropy": 0, "author_coverage": 0, "year_diversity": 0, "overall_score": 0}
        
        # 1. 类别熵
        category_counts = defaultdict(int)
        for r in recommendations:
            cat = r.get("category_name") or r.get("category", "Unknown")
            category_counts[cat] += 1
        
        total = len(recommendations)
        entropy = 0
        for count in category_counts.values():
            p = count / total
            entropy -= p * math.log2(p) if p > 0 else 0
        
        # 2. 作者覆盖率
        authors = set()
        for r in recommendations:
            author = r.get("author", "")
            if author:
                authors.add(author)
        author_coverage = len(authors) / total if total > 0 else 0
        
        # 3. 出版年份多样性
        years = []
        for r in recommendations:
            year = r.get("publication_year", 0)
            if year and year > 0:
                years.append(year)
        
        year_diversity = 0
        if len(years) > 1:
            mean_year = sum(years) / len(years)
            variance = sum((y - mean_year) ** 2 for y in years) / len(years)
            year_diversity = math.sqrt(variance)
        
        # 4. 综合分数
        max_entropy = math.log2(total) if total > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        overall = (0.4 * normalized_entropy + 
                  0.4 * author_coverage + 
                  0.2 * min(year_diversity / 20, 1))  # 标准化年份多样性
        
        return {
            "category_entropy": round(entropy, 3),
            "author_coverage": round(author_coverage, 3),
            "year_diversity": round(year_diversity, 2),
            "overall_score": round(overall, 3)
        }


# 全局多样性服务实例
diversity_service = DiversityService()


def get_diversity_service() -> DiversityService:
    """获取多样性服务实例"""
    return diversity_service
