"""
Redis缓存服务模块
提供缓存操作、消息队列（Pub/Sub）功能
"""
import redis
import json
from typing import Any, Optional, List, Set
from datetime import timedelta
from app.core.config import settings


class RedisCache:
    """Redis缓存服务"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
    
    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端（懒加载）"""
        if self._client is None:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return self._client
    
    def is_connected(self) -> bool:
        """检查Redis连接是否正常"""
        try:
            self.client.ping()
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            return False
    
    # ==================== 基础缓存操作 ====================
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            return self.client.set(key, value)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查key是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取key的剩余生存时间（秒）"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            print(f"Redis TTL error: {e}")
            return -2
    
    # ==================== JSON缓存操作 ====================
    
    def get_json(self, key: str) -> Optional[Any]:
        """获取JSON格式的缓存值"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置JSON格式的缓存值"""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return self.set(key, json_str, ttl)
        except (TypeError, json.JSONDecodeError) as e:
            print(f"Redis SET JSON error: {e}")
            return False
    
    # ==================== Set操作（用于黑名单） ====================
    
    def sadd(self, key: str, *values: str) -> int:
        """添加元素到Set"""
        try:
            return self.client.sadd(key, *values)
        except Exception as e:
            print(f"Redis SADD error: {e}")
            return 0
    
    def srem(self, key: str, *values: str) -> int:
        """从Set中移除元素"""
        try:
            return self.client.srem(key, *values)
        except Exception as e:
            print(f"Redis SREM error: {e}")
            return 0
    
    def sismember(self, key: str, value: str) -> bool:
        """检查元素是否在Set中"""
        try:
            return self.client.sismember(key, value)
        except Exception as e:
            print(f"Redis SISMEMBER error: {e}")
            return False
    
    def smembers(self, key: str) -> Set[str]:
        """获取Set中所有元素"""
        try:
            return self.client.smembers(key)
        except Exception as e:
            print(f"Redis SMEMBERS error: {e}")
            return set()
    
    def scard(self, key: str) -> int:
        """获取Set的元素数量"""
        try:
            return self.client.scard(key)
        except Exception as e:
            print(f"Redis SCARD error: {e}")
            return 0
    
    # ==================== Hash操作（用于用户行为计数） ====================
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """获取Hash字段值"""
        try:
            return self.client.hget(name, key)
        except Exception as e:
            print(f"Redis HGET error: {e}")
            return None
    
    def hset(self, name: str, key: str, value: str) -> int:
        """设置Hash字段值"""
        try:
            return self.client.hset(name, key, value)
        except Exception as e:
            print(f"Redis HSET error: {e}")
            return 0
    
    def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        """Hash字段值增加"""
        try:
            return self.client.hincrby(name, key, amount)
        except Exception as e:
            print(f"Redis HINCRBY error: {e}")
            return 0
    
    def hgetall(self, name: str) -> dict:
        """获取Hash所有字段"""
        try:
            return self.client.hgetall(name)
        except Exception as e:
            print(f"Redis HGETALL error: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除Hash字段"""
        try:
            return self.client.hdel(name, *keys)
        except Exception as e:
            print(f"Redis HDEL error: {e}")
            return 0
    
    # ==================== Pub/Sub消息队列 ====================
    
    def publish(self, channel: str, message: Any) -> int:
        """发布消息到频道"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, ensure_ascii=False)
            return self.client.publish(channel, message)
        except Exception as e:
            print(f"Redis PUBLISH error: {e}")
            return 0
    
    def subscribe(self, *channels: str) -> redis.client.PubSub:
        """订阅频道"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            print(f"Redis SUBSCRIBE error: {e}")
            raise
    
    def psubscribe(self, *patterns: str) -> redis.client.PubSub:
        """模式订阅"""
        try:
            pubsub = self.client.pubsub()
            pubsub.psubscribe(*patterns)
            return pubsub
        except Exception as e:
            print(f"Redis PSUBSCRIBE error: {e}")
            raise
    
    # ==================== List操作（用于任务队列） ====================
    
    def lpush(self, key: str, *values: str) -> int:
        """从左侧插入列表"""
        try:
            return self.client.lpush(key, *values)
        except Exception as e:
            print(f"Redis LPUSH error: {e}")
            return 0
    
    def rpush(self, key: str, *values: str) -> int:
        """从右侧插入列表"""
        try:
            return self.client.rpush(key, *values)
        except Exception as e:
            print(f"Redis RPUSH error: {e}")
            return 0
    
    def lpop(self, key: str) -> Optional[str]:
        """从左侧弹出元素"""
        try:
            return self.client.lpop(key)
        except Exception as e:
            print(f"Redis LPOP error: {e}")
            return None
    
    def rpop(self, key: str) -> Optional[str]:
        """从右侧弹出元素"""
        try:
            return self.client.rpop(key)
        except Exception as e:
            print(f"Redis RPOP error: {e}")
            return None
    
    def brpop(self, keys: List[str], timeout: int = 0) -> Optional[tuple]:
        """阻塞式从右侧弹出元素"""
        try:
            return self.client.brpop(keys, timeout)
        except Exception as e:
            print(f"Redis BRPOP error: {e}")
            return None
    
    def llen(self, key: str) -> int:
        """获取列表长度"""
        try:
            return self.client.llen(key)
        except Exception as e:
            print(f"Redis LLEN error: {e}")
            return 0
    
    # ==================== 缓存Key生成辅助方法 ====================
    
    @staticmethod
    def recommendation_key(user_id: int) -> str:
        """生成推荐缓存Key"""
        return f"rec:user:{user_id}"
    
    @staticmethod
    def blacklist_key(user_id: int) -> str:
        """生成黑名单Key"""
        return f"blacklist:user:{user_id}"
    
    @staticmethod
    def click_count_key(user_id: int) -> str:
        """生成点击计数Key"""
        return f"clicks:user:{user_id}"
    
    @staticmethod
    def exposure_count_key(user_id: int) -> str:
        """生成曝光计数Key"""
        return f"exposure:user:{user_id}"
    
    @staticmethod
    def category_dislike_key(user_id: int) -> str:
        """生成类别不喜欢Key"""
        return f"dislike:category:user:{user_id}"
    
    @staticmethod
    def author_dislike_key(user_id: int) -> str:
        """生成作者不喜欢Key"""
        return f"dislike:author:user:{user_id}"
    
    def close(self):
        """关闭Redis连接"""
        if self._client:
            self._client.close()
            self._client = None


# 全局Redis缓存实例
redis_cache = RedisCache()


def get_redis_cache() -> RedisCache:
    """获取Redis缓存实例（FastAPI依赖注入）"""
    return redis_cache
