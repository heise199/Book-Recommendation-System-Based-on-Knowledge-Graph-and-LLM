"""
缓存失效策略服务
处理立即失效、标记stale、判断失效条件
支持两级缓存：L1(Redis) + L2(MySQL)
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.core.cache import redis_cache
from app.core.config import settings
from app.models.sql import RecommendationCache


class CacheService:
    """缓存服务"""
    
    def __init__(self, db: Optional[Session] = None):
        self.cache = redis_cache
        self.db = db
    
    def set_db(self, db: Session):
        """设置数据库会话"""
        self.db = db
    
    # ==================== L1缓存操作（Redis） ====================
    
    def get_l1_cache(self, user_id: int) -> Optional[List[Dict]]:
        """
        获取L1缓存（Redis，5分钟有效）
        
        Returns:
            推荐列表或None
        """
        try:
            key = self.cache.recommendation_key(user_id)
            data = self.cache.get_json(key)
            if data:
                print(f"L1 cache hit for user_id={user_id}")
                return data
            return None
        except Exception as e:
            print(f"L1 cache get error: {e}")
            return None
    
    def set_l1_cache(self, user_id: int, recommendations: List[Dict], ttl: int = None) -> bool:
        """
        设置L1缓存
        
        Args:
            user_id: 用户ID
            recommendations: 推荐列表
            ttl: 过期时间（秒），默认使用配置值
        """
        try:
            key = self.cache.recommendation_key(user_id)
            ttl = ttl or settings.CACHE_L1_TTL
            return self.cache.set_json(key, recommendations, ttl)
        except Exception as e:
            print(f"L1 cache set error: {e}")
            return False
    
    def invalidate_l1_cache(self, user_id: int) -> bool:
        """
        立即删除L1缓存
        """
        try:
            key = self.cache.recommendation_key(user_id)
            result = self.cache.delete(key)
            if result:
                print(f"L1 cache invalidated for user_id={user_id}")
            return result
        except Exception as e:
            print(f"L1 cache invalidate error: {e}")
            return False
    
    # ==================== L2缓存操作（MySQL） ====================
    
    def get_l2_cache(self, user_id: int) -> Optional[List[Dict]]:
        """
        获取L2缓存（MySQL，24小时有效）
        
        Returns:
            推荐列表或None
        """
        if not self.db:
            return None
            
        try:
            cache = self.db.query(RecommendationCache).filter(
                RecommendationCache.user_id == user_id
            ).first()
            
            if not cache:
                return None
            
            # 检查是否标记为stale
            if cache.is_stale:
                print(f"L2 cache is stale for user_id={user_id}")
                return None
            
            # 检查是否过期（24小时）
            cache_time = cache.updated_at if cache.updated_at else cache.created_at
            if datetime.now() - cache_time > timedelta(seconds=settings.CACHE_L3_TTL):
                print(f"L2 cache expired for user_id={user_id}")
                return None
            
            data = json.loads(cache.recommendations)
            print(f"L2 cache hit for user_id={user_id}")
            return data
            
        except Exception as e:
            print(f"L2 cache get error: {e}")
            return None
    
    def set_l2_cache(self, user_id: int, recommendations: List[Dict]) -> bool:
        """
        设置L2缓存
        """
        if not self.db:
            return False
            
        try:
            cache = self.db.query(RecommendationCache).filter(
                RecommendationCache.user_id == user_id
            ).first()
            
            cache_data = json.dumps(recommendations, ensure_ascii=False)
            
            if cache:
                cache.recommendations = cache_data
                cache.is_stale = False
                cache.updated_at = datetime.now()
            else:
                cache = RecommendationCache(
                    user_id=user_id,
                    recommendations=cache_data,
                    is_stale=False
                )
                self.db.add(cache)
            
            self.db.commit()
            print(f"L2 cache updated for user_id={user_id}")
            return True
            
        except Exception as e:
            print(f"L2 cache set error: {e}")
            self.db.rollback()
            return False
    
    def mark_l2_cache_stale(self, user_id: int) -> bool:
        """
        标记L2缓存为stale（待更新状态）
        下次请求时会重新计算
        """
        if not self.db:
            return False
            
        try:
            cache = self.db.query(RecommendationCache).filter(
                RecommendationCache.user_id == user_id
            ).first()
            
            if cache:
                cache.is_stale = True
                self.db.commit()
                print(f"L2 cache marked as stale for user_id={user_id}")
                return True
            return False
            
        except Exception as e:
            print(f"L2 cache mark stale error: {e}")
            self.db.rollback()
            return False
    
    def invalidate_l2_cache(self, user_id: int) -> bool:
        """
        删除L2缓存
        """
        if not self.db:
            return False
            
        try:
            result = self.db.query(RecommendationCache).filter(
                RecommendationCache.user_id == user_id
            ).delete()
            self.db.commit()
            if result:
                print(f"L2 cache deleted for user_id={user_id}")
            return result > 0
            
        except Exception as e:
            print(f"L2 cache delete error: {e}")
            self.db.rollback()
            return False
    
    # ==================== 统一缓存操作 ====================
    
    def get_recommendations(self, user_id: int) -> Optional[List[Dict]]:
        """
        获取推荐缓存（先L1，后L2）
        
        Returns:
            推荐列表或None
        """
        # 1. 尝试L1缓存
        result = self.get_l1_cache(user_id)
        if result:
            return result
        
        # 2. 尝试L2缓存
        result = self.get_l2_cache(user_id)
        if result:
            # 回填L1缓存
            self.set_l1_cache(user_id, result)
            return result
        
        return None
    
    def set_recommendations(self, user_id: int, recommendations: List[Dict]) -> bool:
        """
        设置推荐缓存（同时设置L1和L2）
        """
        l1_success = self.set_l1_cache(user_id, recommendations)
        l2_success = self.set_l2_cache(user_id, recommendations)
        return l1_success or l2_success
    
    def invalidate_user_cache(self, user_id: int) -> bool:
        """
        立即删除用户的所有推荐缓存（L1 + L2标记为stale）
        """
        l1_result = self.invalidate_l1_cache(user_id)
        l2_result = self.mark_l2_cache_stale(user_id)
        print(f"Cache invalidated for user_id={user_id}: L1={l1_result}, L2_stale={l2_result}")
        return l1_result or l2_result
    
    def should_invalidate(self, event_type: str, user_id: int, book_id: int = None) -> bool:
        """
        判断是否应该触发缓存失效
        
        Args:
            event_type: 事件类型
            user_id: 用户ID
            book_id: 书籍ID
            
        Returns:
            是否应该失效
        """
        # 高价值行为立即失效
        if event_type in ["rating", "collect", "negative_feedback"]:
            return True
        
        # 点击行为累计失效
        if event_type == "click":
            return self._check_click_threshold(user_id)
        
        # 搜索行为部分失效（可以选择不完全失效）
        if event_type == "search":
            return True  # 暂时全部失效，后续可优化为部分失效
        
        return False
    
    def _check_click_threshold(self, user_id: int) -> bool:
        """
        检查点击是否达到失效阈值
        """
        try:
            key = self.cache.click_count_key(user_id)
            # 获取总点击次数
            counts = self.cache.hgetall(key)
            total = sum(int(v) for v in counts.values()) if counts else 0
            return total >= settings.CLICK_INVALIDATION_THRESHOLD
        except Exception as e:
            print(f"Click threshold check error: {e}")
            return True  # 出错时保守处理
    
    # ==================== 缓存合并（增量更新） ====================
    
    def merge_recommendations(
        self, 
        user_id: int, 
        new_recommendations: List[Dict],
        affected_book_ids: List[int] = None
    ) -> List[Dict]:
        """
        合并新旧推荐结果（用于增量更新）
        
        Args:
            user_id: 用户ID
            new_recommendations: 新计算的推荐
            affected_book_ids: 受影响的书籍ID列表
            
        Returns:
            合并后的推荐列表
        """
        # 获取现有缓存
        old_recommendations = self.get_recommendations(user_id) or []
        
        if not affected_book_ids:
            # 没有指定受影响书籍，全部替换
            return new_recommendations
        
        # 创建新推荐的映射
        new_map = {rec.get("book_id"): rec for rec in new_recommendations}
        
        # 合并：受影响的书籍用新推荐，其他保留旧推荐
        merged = []
        seen_ids = set()
        
        # 先添加受影响书籍的新推荐
        for rec in new_recommendations:
            book_id = rec.get("book_id")
            if book_id in affected_book_ids:
                merged.append(rec)
                seen_ids.add(book_id)
        
        # 添加未受影响的旧推荐
        for rec in old_recommendations:
            book_id = rec.get("book_id")
            if book_id not in seen_ids and book_id not in affected_book_ids:
                merged.append(rec)
                seen_ids.add(book_id)
        
        # 按分数重新排序
        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return merged[:settings.RECOMMENDATION_LIMIT]
    
    # ==================== 缓存预热 ====================
    
    def warm_cache(self, user_ids: List[int], compute_func) -> int:
        """
        预热缓存
        
        Args:
            user_ids: 用户ID列表
            compute_func: 计算推荐的函数
            
        Returns:
            预热成功的数量
        """
        success_count = 0
        for user_id in user_ids:
            try:
                # 检查是否需要预热
                if self.get_l1_cache(user_id):
                    continue  # 已有缓存，跳过
                
                # 计算推荐
                recommendations = compute_func(user_id)
                if recommendations:
                    self.set_recommendations(user_id, recommendations)
                    success_count += 1
                    
            except Exception as e:
                print(f"Cache warm error for user_id={user_id}: {e}")
        
        return success_count


# 全局缓存服务实例
cache_service = CacheService()


def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    return cache_service
