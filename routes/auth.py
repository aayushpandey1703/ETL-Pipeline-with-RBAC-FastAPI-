from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models.database import get_db
from models.user import User, Role, UserRole
from schemas.user import UserInsert, UserResponse
from jose import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from typing import List
load_dotenv()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
auth_router=APIRouter(prefix="/auth")
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ALGORITHM=os.getenv("JWT_ALGORITHM","HS256")
EXPIRY_TIME=int(os.getenv("TOKEN_EXPIRY_TIME",60))

async def check_user(username,db):
    try:
        userObj=await db.execute(select(User).options(selectinload(User.user_role).selectinload(UserRole.role)).where(User.username==username))
        print(userObj)
        user=userObj.scalars().first()
        if user:
            return True, user
        return False,None
    except Exception as e:
        print(f"[check_user] Something went wrong : {e}")
        raise HTTPException(status_code=500, detail=f"Somthing went wrong: {str(e)}")

async def check_password(plain_password,hash_password):
    return pwd_context.verify(plain_password,hash_password)

def create_access_token(userID, roles, expiry_time):
    try:
        ExpireTime=datetime.utcnow() + timedelta(minutes=expiry_time)
        payload={
            "sub":str(userID),
            "roles":roles,
            "exp":ExpireTime
        }
        token=jwt.encode(payload,JWT_SECRET_KEY,algorithm=ALGORITHM)
        response={
            "access_token":token,
            "token_type":"bearer"
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[create_access_toke] Something went wrong: {str(e)}")

async def get_current_user(token: str=Depends(oauth2_scheme)):
    try:
        token_payload=jwt.decode(token,JWT_SECRET_KEY,algorithms=ALGORITHM)
        return token_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[get_current_user] something went wrongs: {str(e)}")

def required_role_check(required_role: List[str]):
    async def start_check(user:dict=Depends(get_current_user)):
        try:
            if "admin" in user.get("roles"):
                return user
            for i in required_role:
                if i in user["roles"]:
                    return user
            print("no perission for the user")
            raise HTTPException(status_code=403, detail="You don't have required permission")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[required_role_check] something went wrong: {str(e)}")
    return start_check


@auth_router.post("/register",response_model=UserResponse,status_code=201)
async def register(user: UserInsert, db:AsyncSession=Depends(get_db)):
    try:
        # get role for admin
        role="admin"
        rolename=await db.execute(select(Role).where(Role.name==role))
        roleObj=rolename.scalars().first()
        if not roleObj:
            roleObj=Role(name=role)
            db.add(roleObj)
            await db.flush()
            raise HTTPException(status_code=404, detail="Role admin does not exists")
        roleID=roleObj.id

        # add user 
        checkUser,userObj=await check_user(user.username,db)
        if checkUser:
            raise HTTPException(status_code=409, detail="User already exists")
        print("success user does not exists")
        pass_hash=pwd_context.hash(user.password)
        print(pass_hash)
        user.password=pass_hash
        dbUser=User(**user.dict())
        db.add(dbUser)
        await db.flush()
        userid=dbUser.id

        # add role for user
        userrole={
            "user_id":userid,
            "role_id":roleID
        }
        userRole=UserRole(**userrole)
        db.add(userRole)
        await db.commit()
        await db.refresh(dbUser)
        return dbUser
    
    except HTTPException:
        raise
    except Exception as e:
        response={
            "details":f"failed to register user: {str(e)}"
        }
        return JSONResponse(content=response,status_code=500)
        
@auth_router.post("/login")
async def login(user: OAuth2PasswordRequestForm=Depends(), db: AsyncSession=Depends(get_db)):
    try:
        username=user.username
        checkUser,UserObj=await check_user(username,db)
        if not checkUser:
            raise HTTPException(status_code=401, detail="User does not exists")
        checkPass=await check_password(user.password,UserObj.password)
        if not checkPass:
            raise HTTPException(status_code=401, detail="Wrong credential")
        
        roles = [ur.role.name for ur in UserObj.user_role]
        
        token=create_access_token(userID=UserObj.id,roles=roles,expiry_time=EXPIRY_TIME)
        return token
    except HTTPException:
        raise
    except Exception as e:
        print(f"[login] Something went wrong: {str(e)}")
        response={
            "detail":f"Something went wrong: {str(e)}"
        }
        return JSONResponse(content=response,status_code=500)