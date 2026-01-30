"""
异步推荐计算Worker
订阅Redis事件，接收缓存失效事件后异步重新计算推荐
"""
import json
import threading
import time
from typing import Optional, Callable
from datetime import datetime

from app.core.cache import redis_cache
from app.core.database import SessionLocal, neo4j_conn
from app.services.event_service import CHANNEL_CACHE_INVALIDATION, CHANNEL_RECOMMENDATION_UPDATE
from app.services.cache_service import CacheService


class RecommendationWorker:
    """推荐计算Worker"""
    
    def __init__(self):
        self.cache = redis_cache
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._pubsub = None
        self._recommendation_func: Optional[Callable] = None
    
    def set_recommendation_function(self, func: Callable):
        """
        设置推荐计算函数
        
        Args:
            func: 接收user_id，返回推荐列表的函数
        """
        self._recommendation_func = func
    
    def start(self):
        """启动Worker（后台线程）"""
        if self.running:
            print("Worker is already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("Recommendation Worker started")
    
    def stop(self):
        """停止Worker"""
        self.running = False
        if self._pubsub:
            self._pubsub.close()
        if self._thread:
            self._thread.join(timeout=5)
        print("Recommendation Worker stopped")
    
    def _run(self):
        """Worker主循环"""
        try:
            # 订阅缓存失效频道
            self._pubsub = self.cache.subscribe(CHANNEL_CACHE_INVALIDATION)
            
            print(f"Worker subscribed to {CHANNEL_CACHE_INVALIDATION}")
            
            for message in self._pubsub.listen():
                if not self.running:
                    break
                
                if message["type"] == "message":
                    self._handle_message(message)
                    
        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            if self._pubsub:
                self._pubsub.close()
    
    def _handle_message(self, message: dict):
        """处理收到的消息"""
        try:
            data = message.get("data", "{}")
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            
            event = json.loads(data)
            
            user_id = event.get("user_id")
            event_type = event.get("event_type")
            priority = event.get("priority", 1)
            
            print(f"Worker received event: user_id={user_id}, type={event_type}, priority={priority}")
            
            # 根据优先级决定处理方式
            if priority >= 3:
                # 高优先级，立即处理
                self._process_event(event)
            else:
                # 普通优先级，加入队列
                self._enqueue_event(event)
                
        except json.JSONDecodeError as e:
            print(f"Invalid message format: {e}")
        except Exception as e:
            print(f"Message handling error: {e}")
    
    def _process_event(self, event: dict):
        """处理单个事件"""
        user_id = event.get("user_id")
        
        if not user_id:
            return
        
        try:
            # 创建数据库会话
            db = SessionLocal()
            neo4j = neo4j_conn.get_session()
            
            try:
                cache_service = CacheService(db)
                
                # 如果有推荐计算函数，则重新计算
                if self._recommendation_func:
                    print(f"Recomputing recommendations for user_id={user_id}")
                    recommendations = self._recommendation_func(user_id, db, neo4j)
                    
                    if recommendations:
                        # 转换为缓存格式
                        cache_data = self._convert_to_cache_format(recommendations)
                        cache_service.set_recommendations(user_id, cache_data)
                        print(f"Cache updated for user_id={user_id}")
                else:
                    # 没有计算函数，只标记缓存失效
                    cache_service.invalidate_user_cache(user_id)
                    
            finally:
                db.close()
                neo4j.close()
                
        except Exception as e:
            print(f"Event processing error for user_id={user_id}: {e}")
    
    def _enqueue_event(self, event: dict):
        """将事件加入队列"""
        try:
            queue_key = f"queue:{CHANNEL_CACHE_INVALIDATION}"
            self.cache.rpush(queue_key, json.dumps(event))
        except Exception as e:
            print(f"Enqueue error: {e}")
    
    def _convert_to_cache_format(self, recommendations: list) -> list:
        """将推荐结果转换为缓存格式"""
        cache_data = []
        for rec in recommendations:
            if hasattr(rec, "get"):
                # 已经是字典
                cache_data.append(rec)
            elif hasattr(rec, "book"):
                # 是推荐对象
                cache_data.append({
                    "book_id": rec["book"].id if hasattr(rec["book"], "id") else rec["book"]["id"],
                    "score": rec.get("score", 0),
                    "reason": rec.get("reason", ""),
                    "tags": rec.get("tags", [])
                })
        return cache_data
    
    def process_queue(self, batch_size: int = 10):
        """
        处理队列中的事件（手动调用）
        
        Args:
            batch_size: 每次处理的事件数量
        """
        queue_key = f"queue:{CHANNEL_CACHE_INVALIDATION}"
        processed = 0
        
        while processed < batch_size:
            event_str = self.cache.rpop(queue_key)
            if not event_str:
                break
            
            try:
                event = json.loads(event_str)
                self._process_event(event)
                processed += 1
            except Exception as e:
                print(f"Queue processing error: {e}")
        
        return processed


class QueueWorker:
    """
    队列Worker（轮询模式）
    适用于不支持Pub/Sub或需要更可靠处理的场景
    """
    
    def __init__(self):
        self.cache = redis_cache
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._recommendation_func: Optional[Callable] = None
    
    def set_recommendation_function(self, func: Callable):
        """设置推荐计算函数"""
        self._recommendation_func = func
    
    def start(self, poll_interval: float = 1.0):
        """
        启动Worker
        
        Args:
            poll_interval: 轮询间隔（秒）
        """
        if self.running:
            print("Queue Worker is already running")
            return
        
        self.running = True
        self._thread = threading.Thread(
            target=self._run, 
            args=(poll_interval,),
            daemon=True
        )
        self._thread.start()
        print("Queue Worker started")
    
    def stop(self):
        """停止Worker"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("Queue Worker stopped")
    
    def _run(self, poll_interval: float):
        """Worker主循环"""
        queue_key = f"queue:{CHANNEL_CACHE_INVALIDATION}"
        
        while self.running:
            try:
                # 阻塞式弹出（带超时）
                result = self.cache.brpop([queue_key], timeout=int(poll_interval))
                
                if result:
                    _, event_str = result
                    event = json.loads(event_str)
                    self._process_event(event)
                    
            except Exception as e:
                print(f"Queue Worker error: {e}")
                time.sleep(poll_interval)
    
    def _process_event(self, event: dict):
        """处理事件"""
        user_id = event.get("user_id")
        
        if not user_id:
            return
        
        try:
            db = SessionLocal()
            neo4j = neo4j_conn.get_session()
            
            try:
                cache_service = CacheService(db)
                
                if self._recommendation_func:
                    print(f"Queue Worker: Recomputing for user_id={user_id}")
                    recommendations = self._recommendation_func(user_id, db, neo4j)
                    
                    if recommendations:
                        cache_data = []
                        for rec in recommendations:
                            if isinstance(rec, dict) and "book" in rec:
                                book = rec["book"]
                                cache_data.append({
                                    "book_id": book.id if hasattr(book, "id") else book.get("id"),
                                    "score": rec.get("score", 0),
                                    "reason": rec.get("reason", ""),
                                    "tags": rec.get("tags", [])
                                })
                        cache_service.set_recommendations(user_id, cache_data)
                else:
                    cache_service.invalidate_user_cache(user_id)
                    
            finally:
                db.close()
                neo4j.close()
                
        except Exception as e:
            print(f"Queue Worker processing error: {e}")


# 全局Worker实例
recommendation_worker = RecommendationWorker()
queue_worker = QueueWorker()


def start_workers():
    """启动所有Worker"""
    # 使用队列Worker作为主要处理方式（更可靠）
    queue_worker.start()
    # 可选：同时启动Pub/Sub Worker（用于实时处理高优先级事件）
    # recommendation_worker.start()


def stop_workers():
    """停止所有Worker"""
    recommendation_worker.stop()
    queue_worker.stop()
