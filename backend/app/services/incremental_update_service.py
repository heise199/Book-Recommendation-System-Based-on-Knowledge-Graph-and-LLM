"""
增量更新服务
分析行为影响范围，仅重新计算受影响的推荐
"""
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession

from app.core.config import settings


class IncrementalUpdateService:
    """增量更新服务"""
    
    def __init__(self, db: Session = None, neo4j: Neo4jSession = None):
        self.db = db
        self.neo4j = neo4j
    
    def set_db(self, db: Session):
        """设置数据库会话"""
        self.db = db
    
    def set_neo4j(self, neo4j: Neo4jSession):
        """设置Neo4j会话"""
        self.neo4j = neo4j
    
    def analyze_impact(
        self, 
        user_id: int, 
        book_id: int, 
        action_type: str
    ) -> Dict[str, Any]:
        """
        分析行为影响范围
        
        Args:
            user_id: 用户ID
            book_id: 触发行为的书籍ID
            action_type: 行为类型 (click, collect, rating, negative_feedback)
            
        Returns:
            {
                "affected_books": [book_id1, book_id2, ...],  # 受影响的书籍ID
                "affected_categories": ["科幻", "历史"],      # 受影响的类别
                "affected_authors": ["刘慈欣"],              # 受影响的作者
                "update_scope": "partial" | "full",          # 更新范围
                "priority": 1-3                              # 更新优先级
            }
        """
        if not self.neo4j:
            return self._default_impact(book_id, action_type)
        
        try:
            # 根据行为类型决定影响范围
            if action_type in ["rating", "collect", "negative_feedback"]:
                # 高价值行为：扩展影响范围
                return self._analyze_extended_impact(user_id, book_id, action_type)
            else:
                # 点击行为：局部影响
                return self._analyze_local_impact(user_id, book_id)
                
        except Exception as e:
            print(f"Impact analysis error: {e}")
            return self._default_impact(book_id, action_type)
    
    def _analyze_extended_impact(
        self, 
        user_id: int, 
        book_id: int, 
        action_type: str
    ) -> Dict[str, Any]:
        """分析扩展影响（高价值行为）"""
        
        # 查询1-2跳范围内的相关书籍
        cypher_query = """
        MATCH (b:Book {id: $book_id})
        
        // 获取书籍的类别和作者
        OPTIONAL MATCH (b)-[:BELONGS_TO]->(cat:Category)
        OPTIONAL MATCH (b)-[:WRITTEN_BY]->(author:Author)
        
        // 找到同类别的书籍
        OPTIONAL MATCH (cat)<-[:BELONGS_TO]-(same_cat_book:Book)
        WHERE same_cat_book.id <> b.id
        
        // 找到同作者的书籍
        OPTIONAL MATCH (author)<-[:WRITTEN_BY]-(same_author_book:Book)
        WHERE same_author_book.id <> b.id
        
        // 找到协同过滤相关的书籍
        OPTIONAL MATCH (b)<-[:CLICKED|RATED|COLLECTED]-(peer:User)-[:CLICKED|RATED|COLLECTED]->(collab_book:Book)
        WHERE collab_book.id <> b.id
        
        RETURN 
            collect(DISTINCT same_cat_book.id) AS same_category_books,
            collect(DISTINCT same_author_book.id) AS same_author_books,
            collect(DISTINCT collab_book.id) AS collab_books,
            cat.name AS category_name,
            author.name AS author_name
        """
        
        result = self.neo4j.run(cypher_query, book_id=book_id).single()
        
        if not result:
            return self._default_impact(book_id, action_type)
        
        # 合并受影响的书籍
        affected_books = set()
        affected_books.add(book_id)
        
        # 同类别书籍（限制数量）
        same_cat = result["same_category_books"] or []
        affected_books.update(same_cat[:20])
        
        # 同作者书籍
        same_author = result["same_author_books"] or []
        affected_books.update(same_author[:10])
        
        # 协同过滤书籍
        collab = result["collab_books"] or []
        affected_books.update(collab[:10])
        
        return {
            "affected_books": list(affected_books),
            "affected_categories": [result["category_name"]] if result["category_name"] else [],
            "affected_authors": [result["author_name"]] if result["author_name"] else [],
            "update_scope": "partial",
            "priority": 3 if action_type == "rating" else 2
        }
    
    def _analyze_local_impact(self, user_id: int, book_id: int) -> Dict[str, Any]:
        """分析局部影响（点击行为）"""
        
        # 只查询直接相关的书籍
        cypher_query = """
        MATCH (b:Book {id: $book_id})
        
        // 获取书籍的类别
        OPTIONAL MATCH (b)-[:BELONGS_TO]->(cat:Category)
        
        // 找到同类别的高评分书籍（限制数量）
        OPTIONAL MATCH (cat)<-[:BELONGS_TO]-(related:Book)
        WHERE related.id <> b.id
        
        RETURN 
            collect(DISTINCT related.id)[0..10] AS related_books,
            cat.name AS category_name
        """
        
        result = self.neo4j.run(cypher_query, book_id=book_id).single()
        
        if not result:
            return self._default_impact(book_id, "click")
        
        affected_books = [book_id]
        related = result["related_books"] or []
        affected_books.extend(related)
        
        return {
            "affected_books": affected_books,
            "affected_categories": [result["category_name"]] if result["category_name"] else [],
            "affected_authors": [],
            "update_scope": "partial",
            "priority": 1
        }
    
    def _default_impact(self, book_id: int, action_type: str) -> Dict[str, Any]:
        """默认影响（无法分析时的回退）"""
        return {
            "affected_books": [book_id],
            "affected_categories": [],
            "affected_authors": [],
            "update_scope": "full" if action_type in ["rating", "collect"] else "partial",
            "priority": 2 if action_type in ["rating", "collect"] else 1
        }
    
    def incremental_update(
        self, 
        user_id: int, 
        old_recommendations: List[Dict],
        affected_books: List[int],
        new_scores: Dict[int, float]
    ) -> List[Dict]:
        """
        增量更新推荐列表
        
        Args:
            user_id: 用户ID
            old_recommendations: 旧的推荐列表
            affected_books: 受影响的书籍ID
            new_scores: 新计算的分数 {book_id: score}
            
        Returns:
            更新后的推荐列表
        """
        affected_set = set(affected_books)
        
        # 分离受影响和未受影响的推荐
        updated = []
        
        for rec in old_recommendations:
            book_id = rec.get("book_id") or rec.get("book", {}).get("id")
            
            if book_id in affected_set and book_id in new_scores:
                # 应用分数融合
                old_score = rec.get("score", 0)
                new_score = new_scores[book_id]
                
                # 融合公式：新分数 = 旧分数 × 0.7 + 新计算分数 × 0.3
                fused_score = old_score * 0.7 + new_score * 0.3
                
                rec["score"] = fused_score
                rec["updated"] = True
            
            updated.append(rec)
        
        # 按分数重新排序
        updated.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return updated[:settings.RECOMMENDATION_LIMIT]
    
    def should_use_incremental(
        self, 
        action_type: str, 
        affected_count: int,
        cache_age_seconds: int
    ) -> bool:
        """
        判断是否应该使用增量更新
        
        Args:
            action_type: 行为类型
            affected_count: 受影响书籍数量
            cache_age_seconds: 缓存已存在的秒数
            
        Returns:
            是否使用增量更新
        """
        # 如果缓存太旧，使用全量更新
        if cache_age_seconds > 3600:  # 1小时
            return False
        
        # 如果受影响书籍太多，使用全量更新
        if affected_count > 30:
            return False
        
        # 负反馈总是全量更新（确保黑名单生效）
        if action_type == "negative_feedback":
            return False
        
        return True


# 全局增量更新服务实例
incremental_service = IncrementalUpdateService()


def get_incremental_service() -> IncrementalUpdateService:
    """获取增量更新服务实例"""
    return incremental_service
