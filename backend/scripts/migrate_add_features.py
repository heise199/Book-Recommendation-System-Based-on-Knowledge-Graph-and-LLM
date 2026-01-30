"""
数据库迁移脚本：添加推荐系统新功能所需的表和字段
- NegativeFeedback: 负反馈记录
- RecommendationHistory: 推荐历史（滑动窗口）
- ExposureLog: 曝光记录
- RecommendationCache.is_stale: 缓存失效标记

运行方式: python scripts/migrate_add_features.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, SessionLocal


def run_migration():
    """执行数据库迁移"""
    
    migrations = [
        # 1. 添加 is_stale 字段到 recommendation_cache 表
        """
        ALTER TABLE recommendation_cache 
        ADD COLUMN IF NOT EXISTS is_stale BOOLEAN DEFAULT FALSE
        """,
        
        # 2. 创建 negative_feedback 表
        """
        CREATE TABLE IF NOT EXISTS negative_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            book_id INT NOT NULL,
            feedback_type VARCHAR(50) NOT NULL,
            reason TEXT,
            strength INT DEFAULT 3,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_book_id (book_id),
            INDEX idx_user_book (user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 3. 创建 recommendation_history 表
        """
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            recommended_books TEXT NOT NULL,
            window_size INT DEFAULT 50,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 4. 创建 exposure_logs 表
        """
        CREATE TABLE IF NOT EXISTS exposure_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            book_id INT NOT NULL,
            exposure_count INT DEFAULT 1,
            click_count INT DEFAULT 0,
            last_exposure_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_book_id (book_id),
            INDEX idx_user_book (user_id, book_id),
            UNIQUE KEY uk_user_book (user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
    ]
    
    db = SessionLocal()
    
    try:
        for i, sql in enumerate(migrations, 1):
            try:
                # 清理SQL语句
                sql = sql.strip()
                if not sql:
                    continue
                    
                print(f"[{i}/{len(migrations)}] 执行迁移...")
                db.execute(text(sql))
                db.commit()
                print(f"  ✓ 成功")
            except Exception as e:
                error_msg = str(e)
                # 忽略已存在的表/列错误
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print(f"  ⊘ 跳过（已存在）")
                else:
                    print(f"  ✗ 失败: {e}")
                    db.rollback()
        
        print("\n迁移完成!")
        
    finally:
        db.close()


def verify_tables():
    """验证表是否创建成功"""
    db = SessionLocal()
    
    try:
        tables = [
            "negative_feedback",
            "recommendation_history", 
            "exposure_logs"
        ]
        
        print("\n验证表结构:")
        for table in tables:
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'"))
            exists = result.fetchone() is not None
            status = "✓" if exists else "✗"
            print(f"  {status} {table}")
        
        # 验证 is_stale 字段
        result = db.execute(text("SHOW COLUMNS FROM recommendation_cache LIKE 'is_stale'"))
        exists = result.fetchone() is not None
        status = "✓" if exists else "✗"
        print(f"  {status} recommendation_cache.is_stale")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("推荐系统功能迁移脚本")
    print("=" * 50)
    
    run_migration()
    verify_tables()
