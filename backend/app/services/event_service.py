"""
事件发布服务
使用Redis Pub/Sub发布缓存失效事件
"""
import json
from datetime import datetime
from typing import Optional
from app.core.cache import redis_cache
from app.core.config import settings


# 事件频道名称
CHANNEL_CACHE_INVALIDATION = "cache:invalidation"
CHANNEL_RECOMMENDATION_UPDATE = "recommendation:update"


class EventType:
    """事件类型枚举"""
    RATING = "rating"       # 评分事件 - 立即失效
    COLLECT = "collect"     # 收藏事件 - 立即失效
    CLICK = "click"         # 点击事件 - 累计后失效
    SEARCH = "search"       # 搜索事件 - 部分失效
    NEGATIVE_FEEDBACK = "negative_feedback"  # 负反馈事件 - 立即失效
    INCREMENTAL = "incremental"  # 增量更新事件


class EventService:
    """事件服务"""
    
    def __init__(self):
        self.cache = redis_cache
    
    def publish_cache_invalidation(
        self, 
        user_id: int, 
        event_type: str, 
        book_id: Optional[int] = None,
        priority: int = 1,
        extra_data: Optional[dict] = None
    ) -> bool:
        """
        发布缓存失效事件
        
        Args:
            user_id: 用户ID
            event_type: 事件类型 (rating, collect, click, search, negative_feedback)
            book_id: 书籍ID（可选）
            priority: 优先级 1-3，3最高
            extra_data: 额外数据
            
        Returns:
            是否发布成功
        """
        event = {
            "user_id": user_id,
            "event_type": event_type,
            "book_id": book_id,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "extra_data": extra_data or {}
        }
        
        try:
            # 根据事件类型决定是否需要累计
            if event_type == EventType.CLICK:
                # 点击事件需要累计，达到阈值才失效
                if self._should_invalidate_on_click(user_id, book_id):
                    return self._publish_event(CHANNEL_CACHE_INVALIDATION, event)
                return True  # 累计但不触发失效
            else:
                # 其他事件立即发布
                return self._publish_event(CHANNEL_CACHE_INVALIDATION, event)
                
        except Exception as e:
            print(f"Failed to publish cache invalidation event: {e}")
            return False
    
    def publish_incremental_update(
        self,
        user_id: int,
        book_id: int,
        action_type: str,
        affected_books: list = None
    ) -> bool:
        """
        发布增量更新事件
        
        Args:
            user_id: 用户ID
            book_id: 触发更新的书籍ID
            action_type: 行为类型
            affected_books: 受影响的书籍ID列表
            
        Returns:
            是否发布成功
        """
        event = {
            "user_id": user_id,
            "event_type": EventType.INCREMENTAL,
            "book_id": book_id,
            "action_type": action_type,
            "affected_books": affected_books or [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            return self._publish_event(CHANNEL_RECOMMENDATION_UPDATE, event)
        except Exception as e:
            print(f"Failed to publish incremental update event: {e}")
            return False
    
    def _publish_event(self, channel: str, event: dict) -> bool:
        """发布事件到Redis频道"""
        try:
            result = self.cache.publish(channel, event)
            print(f"Published event to {channel}: user_id={event['user_id']}, type={event['event_type']}")
            return result > 0
        except Exception as e:
            print(f"Redis publish error: {e}")
            return False
    
    def _should_invalidate_on_click(self, user_id: int, book_id: Optional[int]) -> bool:
        """
        判断点击事件是否应该触发缓存失效
        累计3次点击后失效
        """
        try:
            click_key = self.cache.click_count_key(user_id)
            
            # 增加点击计数
            count = self.cache.hincrby(click_key, str(book_id) if book_id else "total", 1)
            
            # 设置过期时间（1小时）
            if count == 1:
                self.cache.client.expire(click_key, 3600)
            
            # 达到阈值则重置计数并返回True
            if count >= settings.CLICK_INVALIDATION_THRESHOLD:
                self.cache.hdel(click_key, str(book_id) if book_id else "total")
                return True
                
            return False
            
        except Exception as e:
            print(f"Click count error: {e}")
            return True  # 出错时保守处理，触发失效
    
    def get_pending_events_count(self, channel: str = CHANNEL_CACHE_INVALIDATION) -> int:
        """获取待处理事件数量（从任务队列）"""
        try:
            queue_key = f"queue:{channel}"
            return self.cache.llen(queue_key)
        except Exception as e:
            print(f"Get pending events count error: {e}")
            return 0
    
    def push_to_queue(self, event: dict, channel: str = CHANNEL_CACHE_INVALIDATION) -> bool:
        """
        将事件推送到任务队列（用于异步处理）
        
        注意：这是除了Pub/Sub之外的另一种方式，用于确保事件不丢失
        """
        try:
            queue_key = f"queue:{channel}"
            event_str = json.dumps(event, ensure_ascii=False)
            
            # 按优先级插入（高优先级在前）
            priority = event.get("priority", 1)
            if priority >= 3:
                self.cache.lpush(queue_key, event_str)  # 高优先级插入头部
            else:
                self.cache.rpush(queue_key, event_str)  # 普通优先级插入尾部
            
            return True
        except Exception as e:
            print(f"Push to queue error: {e}")
            return False
    
    def pop_from_queue(self, channel: str = CHANNEL_CACHE_INVALIDATION, timeout: int = 0) -> Optional[dict]:
        """
        从任务队列弹出事件
        
        Args:
            channel: 频道名称
            timeout: 超时时间（秒），0表示不阻塞
            
        Returns:
            事件字典或None
        """
        try:
            queue_key = f"queue:{channel}"
            
            if timeout > 0:
                result = self.cache.brpop([queue_key], timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = self.cache.rpop(queue_key)
                if result:
                    return json.loads(result)
            
            return None
        except Exception as e:
            print(f"Pop from queue error: {e}")
            return None


# 全局事件服务实例
event_service = EventService()


def get_event_service() -> EventService:
    """获取事件服务实例（FastAPI依赖注入）"""
    return event_service
