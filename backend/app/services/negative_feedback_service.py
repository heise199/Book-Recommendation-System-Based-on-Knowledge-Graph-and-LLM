"""
负反馈服务
处理隐式负反馈收集、软降权、特征传播
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from neo4j import Session as Neo4jSession

from app.core.cache import redis_cache
from app.core.config import settings
from app.models.sql import NegativeFeedback, ExposureLog, Rating, Book
from app.services.blacklist_service import BlacklistService
from app.services.sync_service import SyncService


class NegativeFeedbackService:
    """负反馈服务"""
    
    def __init__(self, db: Session = None, neo4j: Neo4jSession = None):
        self.db = db
        self.neo4j = neo4j
        self.cache = redis_cache
        self.blacklist_service = BlacklistService(db, neo4j)
    
    def set_db(self, db: Session):
        """设置数据库会话"""
        self.db = db
        self.blacklist_service.set_db(db)
    
    def set_neo4j(self, neo4j: Neo4jSession):
        """设置Neo4j会话"""
        self.neo4j = neo4j
        self.blacklist_service.set_neo4j(neo4j)
    
    # ==================== 隐式负反馈检测 ====================
    
    def detect_implicit_negative(
        self, 
        user_id: int, 
        book_id: int, 
        behavior: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        检测隐式负反馈
        
        Args:
            user_id: 用户ID
            book_id: 书籍ID
            behavior: 行为类型
                - exposure: 曝光
                - quick_return: 快速返回（点击后<5秒离开）
                - low_rating: 低评分（1-2星）
            **kwargs: 额外参数
                - duration: 停留时间（秒）
                - rating: 评分
                
        Returns:
            检测到的隐式负反馈信息，或None
        """
        result = None
        
        if behavior == "exposure":
            result = self._handle_exposure(user_id, book_id)
        elif behavior == "quick_return":
            duration = kwargs.get("duration", 0)
            result = self._handle_quick_return(user_id, book_id, duration)
        elif behavior == "low_rating":
            rating = kwargs.get("rating", 3)
            result = self._handle_low_rating(user_id, book_id, rating)
        
        return result
    
    def _handle_exposure(self, user_id: int, book_id: int) -> Optional[Dict]:
        """处理曝光事件"""
        if not self.db:
            return None
        
        try:
            # 查找或创建曝光记录
            exposure = self.db.query(ExposureLog).filter(
                ExposureLog.user_id == user_id,
                ExposureLog.book_id == book_id
            ).first()
            
            if exposure:
                exposure.exposure_count += 1
                exposure.last_exposure_at = datetime.now()
            else:
                exposure = ExposureLog(
                    user_id=user_id,
                    book_id=book_id,
                    exposure_count=1,
                    click_count=0
                )
                self.db.add(exposure)
            
            self.db.commit()
            
            # 检查是否达到负反馈阈值
            threshold = settings.IMPLICIT_NEGATIVE_EXPOSURE_THRESHOLD
            if exposure.exposure_count >= threshold and exposure.click_count == 0:
                # 自动创建弱负反馈
                return self._create_implicit_feedback(
                    user_id, book_id, 
                    "implicit_no_click", 
                    f"曝光{exposure.exposure_count}次未点击",
                    strength=1
                )
            
            return None
            
        except Exception as e:
            print(f"Exposure handling error: {e}")
            self.db.rollback()
            return None
    
    def _handle_quick_return(
        self, 
        user_id: int, 
        book_id: int, 
        duration: float
    ) -> Optional[Dict]:
        """处理快速返回事件"""
        if duration >= 5:  # 超过5秒不算快速返回
            return None
        
        if not self.db:
            return None
        
        try:
            # 更新曝光记录的点击计数
            exposure = self.db.query(ExposureLog).filter(
                ExposureLog.user_id == user_id,
                ExposureLog.book_id == book_id
            ).first()
            
            if exposure:
                exposure.click_count += 1
                self.db.commit()
            
            # 快速返回视为弱负反馈信号
            return self._create_implicit_feedback(
                user_id, book_id,
                "implicit_quick_return",
                f"点击后{duration:.1f}秒返回",
                strength=1
            )
            
        except Exception as e:
            print(f"Quick return handling error: {e}")
            self.db.rollback()
            return None
    
    def _handle_low_rating(
        self, 
        user_id: int, 
        book_id: int, 
        rating: int
    ) -> Optional[Dict]:
        """处理低评分事件"""
        if rating > 2:  # 3星及以上不算负反馈
            return None
        
        # 低评分视为中等强度负反馈
        return self._create_implicit_feedback(
            user_id, book_id,
            "implicit_low_rating",
            f"评分仅{rating}星",
            strength=2
        )
    
    def _create_implicit_feedback(
        self,
        user_id: int,
        book_id: int,
        feedback_type: str,
        reason: str,
        strength: int
    ) -> Dict[str, Any]:
        """创建隐式负反馈记录"""
        if not self.db:
            return {"type": feedback_type, "strength": strength}
        
        try:
            # 检查是否已存在显式负反馈
            existing = self.db.query(NegativeFeedback).filter(
                NegativeFeedback.user_id == user_id,
                NegativeFeedback.book_id == book_id,
                NegativeFeedback.is_active == True
            ).first()
            
            if existing:
                # 已有负反馈，不覆盖
                return {"type": "existing", "id": existing.id}
            
            # 创建隐式负反馈
            feedback = NegativeFeedback(
                user_id=user_id,
                book_id=book_id,
                feedback_type=feedback_type,
                reason=reason,
                strength=strength
            )
            self.db.add(feedback)
            self.db.commit()
            
            # 如果强度达到阈值，加入黑名单
            if strength >= 2:
                self.blacklist_service.add_to_blacklist(
                    user_id, book_id, feedback_type, reason
                )
            
            return {
                "type": feedback_type,
                "id": feedback.id,
                "strength": strength,
                "blacklisted": strength >= 2
            }
            
        except Exception as e:
            print(f"Create implicit feedback error: {e}")
            self.db.rollback()
            return {"type": feedback_type, "strength": strength, "error": str(e)}
    
    # ==================== 软降权机制 ====================
    
    def apply_soft_penalty(
        self,
        user_id: int,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        应用软降权
        
        基于曝光次数降低推荐分数：
        最终分数 = 原始分数 × (1 - 曝光次数 × penalty_factor)
        
        Args:
            user_id: 用户ID
            candidates: 候选书籍列表
            
        Returns:
            降权后的候选列表
        """
        if not self.db:
            return candidates
        
        try:
            # 获取用户的曝光记录
            exposures = self.db.query(ExposureLog).filter(
                ExposureLog.user_id == user_id
            ).all()
            
            exposure_map = {e.book_id: e for e in exposures}
            penalty_factor = settings.SOFT_PENALTY_FACTOR
            threshold = settings.IMPLICIT_NEGATIVE_EXPOSURE_THRESHOLD
            
            result = []
            for c in candidates:
                book_id = c.get("book_id") or c.get("book", {}).get("id")
                score = c.get("score", 1.0)
                
                if book_id in exposure_map:
                    exp = exposure_map[book_id]
                    
                    # 计算惩罚
                    if exp.click_count == 0:  # 只有未点击的才惩罚
                        penalty = min(exp.exposure_count * penalty_factor, 0.9)  # 最多降90%
                        score = score * (1 - penalty)
                        
                        # 超过阈值加入黑名单
                        if exp.exposure_count >= threshold:
                            self.blacklist_service.add_to_blacklist(
                                user_id, book_id, "implicit_no_click",
                                f"曝光{exp.exposure_count}次未点击"
                            )
                            continue  # 跳过黑名单书籍
                
                c["score"] = score
                result.append(c)
            
            return result
            
        except Exception as e:
            print(f"Soft penalty error: {e}")
            return candidates
    
    def get_penalty_score(self, user_id: int, book_id: int) -> float:
        """
        获取书籍的惩罚分数
        
        Returns:
            惩罚系数 (0-1)，0表示完全不推荐，1表示正常推荐
        """
        if not self.db:
            return 1.0
        
        try:
            exposure = self.db.query(ExposureLog).filter(
                ExposureLog.user_id == user_id,
                ExposureLog.book_id == book_id
            ).first()
            
            if not exposure or exposure.click_count > 0:
                return 1.0
            
            penalty = min(exposure.exposure_count * settings.SOFT_PENALTY_FACTOR, 0.9)
            return 1 - penalty
            
        except Exception as e:
            print(f"Get penalty score error: {e}")
            return 1.0
    
    # ==================== 负反馈时间衰减 ====================
    
    def apply_time_decay(
        self,
        user_id: int,
        decay_lambda: float = 0.1
    ) -> int:
        """
        应用负反馈时间衰减
        
        strength(t) = original_strength × e^(-λt)
        
        Args:
            user_id: 用户ID
            decay_lambda: 衰减系数（每月衰减10%时约为0.1）
            
        Returns:
            更新的记录数
        """
        if not self.db:
            return 0
        
        import math
        
        try:
            feedbacks = self.db.query(NegativeFeedback).filter(
                NegativeFeedback.user_id == user_id,
                NegativeFeedback.is_active == True
            ).all()
            
            now = datetime.now()
            updated = 0
            
            for f in feedbacks:
                # 计算经过的月数
                age_days = (now - f.created_at).days
                age_months = age_days / 30
                
                # 计算衰减后的强度
                decayed_strength = f.strength * math.exp(-decay_lambda * age_months)
                
                # 如果强度降到0.5以下，考虑重新尝试推荐
                if decayed_strength < 0.5:
                    # 移出黑名单
                    self.blacklist_service.remove_from_blacklist(user_id, f.book_id)
                    
                    # 软删除负反馈
                    if decayed_strength < 0.1:
                        f.is_active = False
                        updated += 1
            
            self.db.commit()
            return updated
            
        except Exception as e:
            print(f"Time decay error: {e}")
            self.db.rollback()
            return 0
    
    # ==================== 统计分析 ====================
    
    def get_user_negative_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户负反馈统计
        """
        if not self.db:
            return {}
        
        try:
            # 统计各类型负反馈数量
            stats = self.db.query(
                NegativeFeedback.feedback_type,
                func.count(NegativeFeedback.id).label("count")
            ).filter(
                NegativeFeedback.user_id == user_id,
                NegativeFeedback.is_active == True
            ).group_by(
                NegativeFeedback.feedback_type
            ).all()
            
            # 获取黑名单数量
            blacklist_count = self.blacklist_service.get_blacklist_count(user_id)
            
            # 获取曝光未点击数量
            exposure_no_click = self.db.query(ExposureLog).filter(
                ExposureLog.user_id == user_id,
                ExposureLog.click_count == 0
            ).count()
            
            return {
                "feedback_by_type": {s.feedback_type: s.count for s in stats},
                "total_feedbacks": sum(s.count for s in stats),
                "blacklist_count": blacklist_count,
                "exposure_no_click": exposure_no_click,
                "disliked_categories": list(self.blacklist_service.get_disliked_categories(user_id)),
                "disliked_authors": list(self.blacklist_service.get_disliked_authors(user_id))
            }
            
        except Exception as e:
            print(f"Get negative stats error: {e}")
            return {}


# 全局负反馈服务实例
negative_feedback_service = NegativeFeedbackService()


def get_negative_feedback_service() -> NegativeFeedbackService:
    """获取负反馈服务实例"""
    return negative_feedback_service
