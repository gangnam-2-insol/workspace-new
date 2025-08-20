"""
MongoDB Tool

MongoDB 데이터베이스 연동 툴
"""

import os
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from .base_tool import BaseTool

class MongoDBTool(BaseTool):
    """MongoDB 연동 툴"""
    
    def __init__(self):
        super().__init__("mongodb_tool", "MongoDB 데이터베이스 연동 툴")
        self.connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = None
        self.db = None
    
    def _get_client(self):
        """MongoDB 클라이언트 연결"""
        if self.client is None:
            try:
                self.client = MongoClient(self.connection_string)
                # 연결 테스트
                self.client.admin.command('ping')
            except PyMongoError as e:
                raise Exception(f"MongoDB 연결 실패: {str(e)}")
        return self.client
    
    def _get_database(self, db_name: str):
        """데이터베이스 가져오기"""
        client = self._get_client()
        return client[db_name]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """MongoDB 작업 실행"""
        action = parameters.get("action", "find_documents")
        
        try:
            if action == "find_documents":
                return self._find_documents(
                    parameters.get("database"),
                    parameters.get("collection"),
                    parameters.get("query", {}),
                    parameters.get("limit", 10)
                )
            elif action == "insert_document":
                return self._insert_document(
                    parameters.get("database"),
                    parameters.get("collection"),
                    parameters.get("document")
                )
            elif action == "update_document":
                return self._update_document(
                    parameters.get("database"),
                    parameters.get("collection"),
                    parameters.get("query"),
                    parameters.get("update"),
                    parameters.get("upsert", False)
                )
            elif action == "delete_document":
                return self._delete_document(
                    parameters.get("database"),
                    parameters.get("collection"),
                    parameters.get("query")
                )
            elif action == "list_collections":
                return self._list_collections(parameters.get("database"))
            elif action == "get_database_stats":
                return self._get_database_stats(parameters.get("database"))
            else:
                return self.create_response(False, error=f"Unknown action: {action}")
                
        except Exception as e:
            return self.create_response(False, error=str(e))
    
    def _find_documents(self, db_name: str, collection_name: str, query: Dict = None, limit: int = 10) -> Dict[str, Any]:
        """문서 조회"""
        if not db_name or not collection_name:
            return self.create_response(False, error="Database and collection names are required")
        
        try:
            db = self._get_database(db_name)
            collection = db[collection_name]
            
            query = query or {}
            cursor = collection.find(query).limit(limit)
            documents = list(cursor)
            
            # ObjectId를 문자열로 변환
            for doc in documents:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            
            return self.create_response(True, data={
                "database": db_name,
                "collection": collection_name,
                "query": query,
                "documents": documents,
                "count": len(documents)
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def _insert_document(self, db_name: str, collection_name: str, document: Dict) -> Dict[str, Any]:
        """문서 삽입"""
        if not db_name or not collection_name or not document:
            return self.create_response(False, error="Database, collection names and document are required")
        
        try:
            db = self._get_database(db_name)
            collection = db[collection_name]
            
            result = collection.insert_one(document)
            
            return self.create_response(True, data={
                "database": db_name,
                "collection": collection_name,
                "inserted_id": str(result.inserted_id),
                "acknowledged": result.acknowledged
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def _update_document(self, db_name: str, collection_name: str, query: Dict, update: Dict, upsert: bool = False) -> Dict[str, Any]:
        """문서 업데이트"""
        if not db_name or not collection_name or not query or not update:
            return self.create_response(False, error="Database, collection names, query and update are required")
        
        try:
            db = self._get_database(db_name)
            collection = db[collection_name]
            
            result = collection.update_one(query, {"$set": update}, upsert=upsert)
            
            return self.create_response(True, data={
                "database": db_name,
                "collection": collection_name,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "acknowledged": result.acknowledged
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def _delete_document(self, db_name: str, collection_name: str, query: Dict) -> Dict[str, Any]:
        """문서 삭제"""
        if not db_name or not collection_name or not query:
            return self.create_response(False, error="Database, collection names and query are required")
        
        try:
            db = self._get_database(db_name)
            collection = db[collection_name]
            
            result = collection.delete_one(query)
            
            return self.create_response(True, data={
                "database": db_name,
                "collection": collection_name,
                "deleted_count": result.deleted_count,
                "acknowledged": result.acknowledged
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def _list_collections(self, db_name: str) -> Dict[str, Any]:
        """컬렉션 목록 조회"""
        if not db_name:
            return self.create_response(False, error="Database name is required")
        
        try:
            db = self._get_database(db_name)
            collections = db.list_collection_names()
            
            return self.create_response(True, data={
                "database": db_name,
                "collections": collections,
                "count": len(collections)
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def _get_database_stats(self, db_name: str) -> Dict[str, Any]:
        """데이터베이스 통계 조회"""
        if not db_name:
            return self.create_response(False, error="Database name is required")
        
        try:
            db = self._get_database(db_name)
            stats = db.command("dbStats")
            
            return self.create_response(True, data={
                "database": db_name,
                "stats": {
                    "collections": stats.get("collections", 0),
                    "views": stats.get("views", 0),
                    "objects": stats.get("objects", 0),
                    "avgObjSize": stats.get("avgObjSize", 0),
                    "dataSize": stats.get("dataSize", 0),
                    "storageSize": stats.get("storageSize", 0),
                    "indexes": stats.get("indexes", 0),
                    "indexSize": stats.get("indexSize", 0)
                }
            })
        except PyMongoError as e:
            return self.create_response(False, error=f"MongoDB error: {str(e)}")
    
    def __del__(self):
        """소멸자: 연결 종료"""
        if self.client:
            self.client.close()

