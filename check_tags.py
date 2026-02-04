import sqlite3
import shutil
import tempfile
import os

db_path = "/Users/jie/Zotero/zotero.sqlite"

# 创建临时副本
fd, temp_db = tempfile.mkstemp(suffix=".sqlite")
os.close(fd)
shutil.copy2(db_path, temp_db)

conn = sqlite3.connect(temp_db)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查看所有标签
cursor.execute("SELECT name FROM tags ORDER BY name")
tags = cursor.fetchall()
print(f"共有 {len(tags)} 个标签:")
for i, tag in enumerate(tags[:30], 1):
    print(f"  {i}. {tag['name']}")

if len(tags) > 30:
    print(f"  ... 还有 {len(tags) - 30} 个标签")

# 查看条目的年份分布
cursor.execute("""
    SELECT idv.value as date
    FROM itemData id
    JOIN fields f ON id.fieldID = f.fieldID
    JOIN itemDataValues idv ON id.valueID = idv.valueID
    WHERE f.fieldName = 'date'
    ORDER BY idv.value DESC
    LIMIT 20
""")
dates = cursor.fetchall()
print(f"\n前 20 个条目的日期:")
for date in dates:
    print(f"  - {date['date']}")

# 查看每个条目的标签
cursor.execute("""
    SELECT i.key, GROUP_CONCAT(t.name, ', ') as tags
    FROM items i
    LEFT JOIN itemTags it ON i.itemID = it.itemID
    LEFT JOIN tags t ON it.tagID = t.tagID
    WHERE i.itemID NOT IN (SELECT itemID FROM itemAttachments)
      AND i.itemID NOT IN (SELECT itemID FROM itemNotes)
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY i.itemID
    LIMIT 10
""")
items_with_tags = cursor.fetchall()
print(f"\n前 10 个条目的标签:")
for item in items_with_tags:
    print(f"  {item['key']}: {item['tags'] or '(无标签)'}")

conn.close()
os.remove(temp_db)