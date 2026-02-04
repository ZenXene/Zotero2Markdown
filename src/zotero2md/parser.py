import logging
from zotero2md.query_cache import QueryCache
from zotero2md.logger import get_logger


class ZoteroParser:
    def __init__(self, connector):
        self.connector = connector
        self._attachment_cache = {}
        self.query_cache = QueryCache(max_size=1000)
        self.logger = get_logger(__name__)
    
    def _get_conn(self):
        return self.connector.connect()

    def get_all_items(self, batch_size=1000):
        query = """
        SELECT i.itemID, i.key, it.typeName
        FROM items i
        JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
        WHERE i.itemID NOT IN (SELECT itemID FROM itemAttachments)
          AND i.itemID NOT IN (SELECT itemID FROM itemNotes)
          AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query)
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield [dict(row) for row in batch]

    def get_item_metadata(self, item_id):
        cache_key = f"metadata_{item_id}"
        cached = self.query_cache.get(cache_key)
        if cached is not None:
            return cached
        
        query = """
        SELECT f.fieldName, idv.value
        FROM itemData id
        JOIN fields f ON id.fieldID = f.fieldID
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        WHERE id.itemID = ?
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (item_id,))
        
        metadata = {}
        for row in cursor.fetchall():
            metadata[row['fieldName']] = row['value']
        
        self.query_cache.set(cache_key, metadata)
        return metadata

    def get_item_tags(self, item_id):
        cache_key = f"tags_{item_id}"
        cached = self.query_cache.get(cache_key)
        if cached is not None:
            return cached
        
        query = """
        SELECT t.name
        FROM itemTags it
        JOIN tags t ON it.tagID = t.tagID
        WHERE it.itemID = ?
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (item_id,))
        tags = [row['name'] for row in cursor.fetchall()]
        
        self.query_cache.set(cache_key, tags)
        return tags

    def get_item_creators(self, item_id):
        cache_key = f"creators_{item_id}"
        cached = self.query_cache.get(cache_key)
        if cached is not None:
            return cached
        
        query = """
        SELECT c.firstName, c.lastName, ct.creatorType
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (item_id,))
        
        creators = []
        for row in cursor.fetchall():
            name = f"{row['firstName']} {row['lastName']}".strip()
            creators.append({
                'name': name,
                'type': row['creatorType']
            })
        
        self.query_cache.set(cache_key, creators)
        return creators

    def get_item_notes(self, parent_item_id, convert_html=False):
        query = """
        SELECT note
        FROM itemNotes
        WHERE parentItemID = ?
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (parent_item_id,))
        notes = [row['note'] for row in cursor.fetchall()]
        
        if convert_html:
            try:
                from html2text import HTML2Text
                h = HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                notes = [h.handle(note) for note in notes]
            except ImportError:
                pass
        
        return notes

    def get_item_attachments(self, parent_item_id):
        query = """
        SELECT ia.path, ia.contentType, ia.linkMode
        FROM itemAttachments ia
        WHERE ia.parentItemID = ?
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (parent_item_id,))
        
        attachments = []
        for row in cursor.fetchall():
            path = row['path']
            if path:
                path = path.replace('storage:', '')
                attachments.append({
                    'path': path,
                    'content_type': row['contentType'],
                    'link_mode': row['linkMode']
                })
        return attachments

    def get_item_collections(self, item_id):
        query = """
        SELECT c.collectionName
        FROM collectionItems ci
        JOIN collections c ON ci.collectionID = c.collectionID
        WHERE ci.itemID = ?
        """
        cursor = self._get_conn().cursor()
        cursor.execute(query, (item_id,))
        return [row['collectionName'] for row in cursor.fetchall()]

if __name__ == "__main__":
    from zotero2md.database import ZoteroConnector
    
    connector = ZoteroConnector()
    conn = connector.connect()
    if conn:
        parser = ZoteroParser(conn)
        items = parser.get_all_items()
        print(f"找到 {len(items)} 个主条目。")
        
        if items:
            first_item = items[0]
            print(f"\n测试条目 (ID: {first_item['itemID']}, Key: {first_item['key']}, Type: {first_item['typeName']}):")
            
            metadata = parser.get_item_metadata(first_item['itemID'])
            for field, value in metadata.items():
                print(f"  {field}: {value}")
            
            creators = parser.get_item_creators(first_item['itemID'])
            print(f"  作者: {', '.join([c['name'] for c in creators])}")
            
            tags = parser.get_item_tags(first_item['itemID'])
            print(f"  标签: {', '.join(tags)}")
            
            notes = parser.get_item_notes(first_item['itemID'])
            print(f"  笔记数量: {len(notes)}")
            
            attachments = parser.get_item_attachments(first_item['itemID'])
            print(f"  附件数量: {len(attachments)}")
            
            collections = parser.get_item_collections(first_item['itemID'])
            print(f"  收藏夹: {', '.join(collections)}")
            
        connector.close()
