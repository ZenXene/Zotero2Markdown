import sqlite3
import platform
from pathlib import Path

def find_zotero_db():
    system = platform.system()
    home = Path.home()
    
    paths = []
    if system == "Darwin":
        paths.append(home / "Library/Application Support/Zotero/Profiles")
        paths.append(home / "Zotero")
    elif system == "Windows":
        import os
        paths.append(Path(os.environ.get("APPDATA", "")) / "Zotero/Zotero/Profiles")
    elif system == "Linux":
        paths.append(home / ".zotero/zotero")
    
    for p in paths:
        if p.exists():
            db_path = p / "zotero.sqlite"
            if db_path.exists():
                return str(db_path)
            
            for profile in p.glob("*.default*"):
                db_path = profile / "zotero.sqlite"
                if db_path.exists():
                    return str(db_path)
    
    return None

db_path = find_zotero_db()
if db_path:
    print(f"找到数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 查看所有标签
    cursor.execute("SELECT name FROM tags ORDER BY name")
    tags = cursor.fetchall()
    print(f"\n共有 {len(tags)} 个标签:")
    for i, tag in enumerate(tags[:50], 1):
        print(f"{i}. {tag['name']}")
    
    if len(tags) > 50:
        print(f"... 还有 {len(tags) - 50} 个标签")
    
    # 查看条目的年份分布
    cursor.execute("""
        SELECT idv.value as date
        FROM itemData id
        JOIN fields f ON id.fieldID = f.fieldID
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        WHERE f.fieldName = 'date'
        LIMIT 20
    """)
    dates = cursor.fetchall()
    print(f"\n前 20 个条目的日期:")
    for date in dates:
        print(f"  - {date['date']}")
    
    # 查看收藏夹
    cursor.execute("SELECT collectionName FROM collections")
    collections = cursor.fetchall()
    print(f"\n共有 {len(collections)} 个收藏夹:")
    for i, col in enumerate(collections[:20], 1):
        print(f"{i}. {col['collectionName']}")
    
    if len(collections) > 20:
        print(f"... 还有 {len(collections) - 20} 个收藏夹")
    
    conn.close()
else:
    print("未找到 Zotero 数据库")