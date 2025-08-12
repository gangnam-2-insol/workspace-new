from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime

from models import User
from database import users_collection

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[User])
async def get_users():
    """모든 사용자 조회"""
    try:
        users = await users_collection.find().to_list(1000)
        return [User(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 조회 실패: {str(e)}")

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """특정 사용자 조회"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="잘못된 사용자 ID")
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return User(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 조회 실패: {str(e)}")

@router.post("/", response_model=User)
async def create_user(user: User):
    """새로운 사용자 생성"""
    try:
        user_dict = user.model_dump(exclude={"id"})
        user_dict["created_at"] = datetime.utcnow()
        
        result = await users_collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return User(**user_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 생성 실패: {str(e)}")

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    """사용자 정보 업데이트"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="잘못된 사용자 ID")
        
        user_dict = user.model_dump(exclude={"id"})
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        # 업데이트된 사용자 반환
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return User(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 업데이트 실패: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """사용자 삭제"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="잘못된 사용자 ID")
        
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return {"message": "사용자가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 삭제 실패: {str(e)}")
