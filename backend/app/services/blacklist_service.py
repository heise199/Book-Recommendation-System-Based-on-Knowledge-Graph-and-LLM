"""
黑名单服务
使用Redis Set存储用户黑名单，支持同步到Neo4j
"""
from typing import Set, List, Optional
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession

from app.core.cache import redis_cache
from app.models.sql import NegativeFeedback, Book
from app.services.sync_service import SyncService


class BlacklistService:
    """黑名单服务"""
    
    def __init__(self, db: Optional[Session] = None, neo4j: Optional[Neo4jSession] = None):
        self.cache = redis_cache
        self.db = db
        self.neo4j = neo4j
    
    def set_db(self, db: Session):
        """设置数据库会话"""
        self.db = db
    
    def set_neo4j(self, neo4j: Neo4jSession):
        """设置Neo4j会话"""
        self.neo4j = neo4j
    
    # ==================== Redis黑名单操作 ====================
    
    def add_to_blacklist(
        self, 
        user_id: int, 
        book_id: int, 
        feedback_type: str = "not_interested",
        reason: str = None
    ) -> bool:
        """
        将书籍加入用户黑名单
        
        Args:
            user_id: 用户ID
            book_id: 书籍ID
            feedback_type: 反馈类型
            reason: 原因
            
        Returns:
            是否添加成功
        """
        try:
            key = self.cache.blacklist_key(user_id)
            result = self.cache.sadd(key, str(book_id))
            
            if result > 0:
                print(f"Added book {book_id} to blacklist for user {user_id}")
                return True
            return False
            
        except Exception as e:
            print(f"Failed to add to blacklist: {e}")
            return False
    
    def remove_from_blacklist(self, user_id: int, book_id: int) -> bool:
        """
        从黑名单移除书籍
        """
        try:
            key = self.cache.blacklist_key(user_id)
            result = self.cache.srem(key, str(book_id))
            
            if result > 0:
                print(f"Removed book {book_id} from blacklist for user {user_id}")
                return True
            return False
            
        except Exception as e:
            print(f"Failed to remove from blacklist: {e}")
            return False
    
    def is_blacklisted(self, user_id: int, book_id: int) -> bool:
        """
        检查书籍是否在用户黑名单中
        """
        try:
            key = self.cache.blacklist_key(user_id)
            return self.cache.sismember(key, str(book_id))
        except Exception as e:
            print(f"Blacklist check error: {e}")
            return False
    
    def get_blacklist(self, user_id: int) -> Set[int]:
        """
        获取用户的完整黑名单
        
        Returns:
            书籍ID集合
        """
        try:
            key = self.cache.blacklist_key(user_id)
            str_ids = self.cache.smembers(key)
            return {int(id) for id in str_ids if id.isdigit()}
        except Exception as e:
            print(f"Get blacklist error: {e}")
            return set()
    
    def get_blacklist_count(self, user_id: int) -> int:
        """
        获取黑名单数量
        """
        try:
            key = self.cache.blacklist_key(user_id)
            return self.cache.scard(key)
        except Exception as e:
            print(f"Get blacklist count error: {e}")
            return 0
    
    # ==================== 类别/作者黑名单 ====================
    
    def add_category_dislike(self, user_id: int, category_name: str) -> bool:
        """
        添加不喜欢的类别
        """
        try:
            key = self.cache.category_dislike_key(user_id)
            return self.cache.sadd(key, category_name) > 0
        except Exception as e:
            print(f"Add category dislike error: {e}")
            return False
    
    def add_author_dislike(self, user_id: int, author_name: str) -> bool:
        """
        添加不喜欢的作者
        """
        try:
            key = self.cache.author_dislike_key(user_id)
            return self.cache.sadd(key, author_name) > 0
        except Exception as e:
            print(f"Add author dislike error: {e}")
            return False
    
    def get_disliked_categories(self, user_id: int) -> Set[str]:
        """
        获取不喜欢的类别列表
        """
        try:
            key = self.cache.category_dislike_key(user_id)
            return self.cache.smembers(key)
        except Exception as e:
            print(f"Get disliked categories error: {e}")
            return set()
    
    def get_disliked_authors(self, user_id: int) -> Set[str]:
        """
        获取不喜欢的作者列表
        """
        try:
            key = self.cache.author_dislike_key(user_id)
            return self.cache.smembers(key)
        except Exception as e:
            print(f"Get disliked authors error: {e}")
            return set()
    
    # ==================== MySQL同步 ====================
    
    def sync_from_mysql(self, user_id: int) -> int:
        """
        从MySQL同步黑名单到Redis
        
        Returns:
            同步的数量
        """
        if not self.db:
            return 0
        
        try:
            feedbacks = self.db.query(NegativeFeedback).filter(
                NegativeFeedback.user_id == user_id,
                NegativeFeedback.is_active == True
            ).all()
            
            count = 0
            for f in feedbacks:
                if self.add_to_blacklist(user_id, f.book_id, f.feedback_type):
                    count += 1
                
                # 同步类别/作者不喜欢
                if f.feedback_type == "wrong_category" and f.book and f.book.category:
                    self.add_category_dislike(user_id, f.book.category.name)
                elif f.feedback_type == "wrong_author" and f.book and f.book.author:
                    self.add_author_dislike(user_id, f.book.author)
            
            print(f"Synced {count} blacklist items from MySQL for user {user_id}")
            return count
            
        except Exception as e:
            print(f"Sync from MySQL error: {e}")
            return 0
    
    # ==================== Neo4j同步 ====================
    
    def sync_to_neo4j(
        self, 
        user_id: int, 
        book_id: int, 
        feedback_type: str,
        category_name: str = None,
        author_name: str = None
    ) -> bool:
        """
        同步负反馈到Neo4j
        """
        if not self.neo4j:
            return False
        
        try:
            sync = SyncService(self.neo4j)
            sync.sync_negative_feedback(
                user_id, 
                book_id, 
                feedback_type, 
                category_name, 
                author_name
            )
            return True
        except Exception as e:
            print(f"Sync to Neo4j error: {e}")
            return False
    
    # ==================== 黑名单过滤 ====================
    
    def filter_recommendations(
        self, 
        user_id: int, 
        book_ids: List[int]
    ) -> List[int]:
        """
        过滤推荐列表，移除黑名单中的书籍
        
        Args:
            user_id: 用户ID
            book_ids: 书籍ID列表
            
        Returns:
            过滤后的书籍ID列表
        """
        blacklist = self.get_blacklist(user_id)
        return [bid for bid in book_ids if bid not in blacklist]
    
    def filter_by_category_author(
        self,
        user_id: int,
        books: List[dict],
        penalty_factor: float = 0.5
    ) -> List[dict]:
        """
        根据类别/作者偏好过滤或降权
        
        Args:
            user_id: 用户ID
            books: 书籍列表（包含category和author字段）
            penalty_factor: 降权因子
            
        Returns:
            处理后的书籍列表
        """
        disliked_categories = self.get_disliked_categories(user_id)
        disliked_authors = self.get_disliked_authors(user_id)
        
        result = []
        for book in books:
            category = book.get("category") or book.get("category_name", "")
            author = book.get("author", "")
            score = book.get("score", 1.0)
            
            # 应用降权
            if category in disliked_categories:
                score *= penalty_factor
            if author in disliked_authors:
                score *= penalty_factor
            
            book["score"] = score
            result.append(book)
        
        return result
    
    def get_blacklist_for_neo4j_query(self, user_id: int) -> List[int]:
        """
        获取用于Neo4j查询的黑名单列表
        
        Returns:
            书籍ID列表（用于Cypher查询的参数）
        """
        return list(self.get_blacklist(user_id))


# 全局黑名单服务实例
blacklist_service = BlacklistService()


def get_blacklist_service() -> BlacklistService:
    """获取黑名单服务实例"""
    return blacklist_service
