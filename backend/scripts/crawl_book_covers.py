import os
import requests
import re
import time
import sys
from urllib.parse import quote
from bs4 import BeautifulSoup

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sql import Book

# Constants
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
COVERS_DIR = os.path.join(STATIC_DIR, "covers")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_image(url: str, save_path: str, timeout: int = 20):
    """下载图片并保存到指定路径"""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        response = requests.get(url, stream=True, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  ❌ 下载失败 {url}: {e}")
        return False

def get_bing_cover_url(title: str, author: str):
    """从必应搜索获取图书封面链接"""
    query = f"{title} {author} 图书封面"
    encoded_query = quote(query)
    url = f"https://cn.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找图片容器
        # 必应图片的原始 URL 通常隐藏在 a.iusc 标签的 m 属性中
        for a_tag in soup.find_all('a', class_='iusc'):
            m_attr = a_tag.get('m')
            if m_attr:
                # 提取 murl (Media URL)
                pattern = r'"murl":"([^"]+)"'
                match = re.search(pattern, m_attr)
                if match:
                    img_url = match.group(1)
                    # 过滤掉一些明显的非图片链接
                    if img_url.startswith('http') and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        return img_url
        return None
    except Exception as e:
        print(f"  ⚠️ 搜索失败 {query}: {e}")
        return None

def main():
    db = SessionLocal()
    try:
        # 获取没有封面或封面是外部链接的图书（可选：只获取没有封面的）
        books = db.query(Book).filter(
            (Book.cover_url == None) | (Book.cover_url == "") | (Book.cover_url.like("http%"))
        ).all()
        
        print(f"🔍 找到 {len(books)} 本待处理的图书")
        
        for i, book in enumerate(books):
            print(f"[{i+1}/{len(books)}] 正在处理: {book.title} - {book.author}")
            
            # 1. 获取图片链接
            img_url = get_bing_cover_url(book.title, book.author)
            
            if img_url:
                # 2. 生成本地保存路径
                # 使用书名和ID组合，避免特殊字符导致路径问题
                safe_title = re.sub(r'[\\/*?:"<>|]', "", book.title).replace(" ", "_")
                filename = f"book_{book.id}_{safe_title[:30]}.jpg"
                save_path = os.path.join(COVERS_DIR, filename)
                
                # 3. 下载图片
                if download_image(img_url, save_path):
                    # 4. 更新数据库路径 (相对路径)
                    db_path = f"/static/covers/{filename}"
                    book.cover_url = db_path
                    db.commit()
                    print(f"  ✅ 成功! 已保存至: {db_path}")
                else:
                    print(f"  ❌ 下载图片失败")
            else:
                print(f"  ❌ 未找到匹配的封面图片")
            
            # 适当延时，避免被封
            time.sleep(1)
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
