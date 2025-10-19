from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from schemas.user import UpdateUser, UserResponse
from models.database import get_db
from models.user import User, Role, UserRole
from .auth import pwd_context, required_role_check
from typing import List
from datetime import datetime

route=APIRouter(prefix="/user")

async def updatedUser(db,user_data,userID):
    try:
        # eager load user
        result=await db.execute(select(User).options(selectinload(User.user_role)).where(User.id==userID))
        user=result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with userID not found")

        if user_data.roles is not None:
            result=await db.execute(select(Role).where(Role.name.in_(user_data.roles)))
            roles=result.scalars().all()
            if len(roles)!=len(user_data.roles):
                raise HTTPException(status_code=404, detail="Some roles does not exists")

            user.user_role.clear()
            print("userID")
            print(userID)
            for role in roles:
                user.user_role.append(UserRole(role_id=role.id))
        if user_data.username:
            user.username=user_data.username
        if user_data.password:
            hashed_password=pwd_context.hash(user_data.password)
            user.password=hashed_password
        user.updated_at=datetime.utcnow()

        await db.commit()
        await db.refresh(user)
        print("user")
        print(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[updatedUser func] Something went wrong: {str(e)} ")


@route.get("/me",response_model=UserResponse)
async def user(db:AsyncSession=Depends(get_db),user: dict=Depends(required_role_check(["user","admin"]))):
    return JSONResponse(
        content=user,
        status_code=200
    ) 
@route.get("/get_users",response_model=List[UserResponse],status_code=200)
async def get_all(db:AsyncSession=Depends(get_db)):
    try:
        usersResult=await db.execute(select(User).options(selectinload(User.user_role).selectinload(UserRole.role)))
        users=usersResult.scalars().all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[get_all_users] something went wrong: {str(e)}")

@route.put("/update_user/{userID}",response_model=UserResponse)
async def update_user(userID:int,user_data:UpdateUser,db:AsyncSession=Depends(get_db)):
    try:
        updateUser=await updatedUser(db,user_data,userID)
        return updateUser
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[Update user route] Something went wrong: {str(e)}")
