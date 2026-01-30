"""
清理测试/假数据脚本
删除数据库中明显的测试数据

运行方式: python scripts/cleanup_test_data.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, or_
from app.core.database import SessionLocal
from app.models.sql import Book, Rating, Interaction


def identify_fake_books(db):
    """识别假书籍"""
    fake_books = []
    
    # 查询所有书籍
    books = db.query(Book).all()
    
    for book in books:
        is_fake = False
        reasons = []
        
        # 1. 标题是常见的测试标题
        if book.title in ['Prof.', 'Mrs.', 'Miss.', 'Mr.', 'Dr.', 'Test', 'Fake']:
            is_fake = True
            reasons.append("测试标题")
        
        # 2. ISBN格式不正确（正常ISBN是10或13位数字）
        if book.isbn and len(book.isbn) < 10 and not book.isbn.startswith('97'):
            is_fake = True
            reasons.append("非法ISBN")
        
        # 3. 封面URL是外部链接而非本地静态文件
        # if book.cover_url and not book.cover_url.startswith('/static/'):
        #     is_fake = True
        #     reasons.append("外部封面URL")
        
        # 4. 描述内容包含典型的Lorem Ipsum或测试文本
        if book.description:
            test_phrases = [
                'Navicat', 'Lorem ipsum', 'SSH', 'HTTP Tunneling',
                'database administration', 'Secure Sockets Layer'
            ]
            for phrase in test_phrases:
                if phrase in book.description:
                    is_fake = True
                    reasons.append(f"描述包含测试文本: {phrase}")
                    break
        
        # 5. 出版年份不合理
        if book.publication_year and (book.publication_year < 1000 or book.publication_year > 2030):
            is_fake = True
            reasons.append(f"不合理的出版年份: {book.publication_year}")
        
        # 6. ID很大（通常测试数据是批量插入的，ID较大）
        # if book.id > 500:
        #     # 额外检查：如果封面是本地的，可能是真实数据
        #     if not book.cover_url or not book.cover_url.startswith('/static/'):
        #         is_fake = True
        #         reasons.append("高ID且无本地封面")
        
        if is_fake:
            fake_books.append({
                'id': book.id,
                'title': book.title,
                'isbn': book.isbn,
                'reasons': reasons
            })
    
    return fake_books


def cleanup_fake_data(db, dry_run=True):
    """清理假数据"""
    fake_books = identify_fake_books(db)
    
    print(f"\n发现 {len(fake_books)} 条可能的测试数据:\n")
    
    for i, fb in enumerate(fake_books[:20], 1):  # 只显示前20条
        print(f"  {i}. ID={fb['id']}, 标题={fb['title'][:30]}, 原因={', '.join(fb['reasons'])}")
    
    if len(fake_books) > 20:
        print(f"  ... 还有 {len(fake_books) - 20} 条")
    
    if dry_run:
        print("\n[DRY RUN] 未实际删除数据。如需删除，请使用 --execute 参数")
        return 0
    
    # 确认删除
    confirm = input(f"\n确定要删除这 {len(fake_books)} 条数据吗？(yes/no): ")
    if confirm.lower() != 'yes':
        print("已取消")
        return 0
    
    deleted = 0
    fake_ids = [fb['id'] for fb in fake_books]
    
    try:
        # 先删除关联的评分和交互
        db.query(Rating).filter(Rating.book_id.in_(fake_ids)).delete(synchronize_session=False)
        db.query(Interaction).filter(Interaction.book_id.in_(fake_ids)).delete(synchronize_session=False)
        
        # 删除书籍
        deleted = db.query(Book).filter(Book.id.in_(fake_ids)).delete(synchronize_session=False)
        
        db.commit()
        print(f"\n✓ 成功删除 {deleted} 条测试数据")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 删除失败: {e}")
    
    return deleted


def main():
    import argparse
    parser = argparse.ArgumentParser(description='清理数据库中的测试数据')
    parser.add_argument('--execute', action='store_true', help='实际执行删除（默认只是预览）')
    parser.add_argument('--list-only', action='store_true', help='只列出假数据，不执行删除')
    args = parser.parse_args()
    
    print("=" * 50)
    print("测试数据清理脚本")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        if args.list_only:
            fake_books = identify_fake_books(db)
            print(f"\n发现 {len(fake_books)} 条可能的测试数据")
            for fb in fake_books:
                print(f"  - ID={fb['id']}, {fb['title']}")
        else:
            cleanup_fake_data(db, dry_run=not args.execute)
    finally:
        db.close()


if __name__ == "__main__":
    main()
