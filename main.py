from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from jose import JWTError, jwt
from datetime import datetime, timedelta

from auth import get_current_user
from models import User
from schemas import UserCreate, UserInDB, Token, Result

import os
import json
import logging
import uvicorn
import certifi
from create import main as create_main


templates = Jinja2Templates(directory="templates")
app = FastAPI()

# Security settings
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Json_file_path = 'json/job.json'

def load_allowed_job_categories():
    with open(Json_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
allowed_job_category = load_allowed_job_categories()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSL 인증서 파일 경로 설정
ca = certifi.where()

# MongoDB 연결 설정
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb+srv://zzcv00:dwiqPBh62FHd1sLb@coffee.ntxtbdl.mongodb.net/?retryWrites=true&w=majority&appName=coffee")
client = AsyncIOMotorClient(MONGO_DETAILS, tlsCAFile=ca)
db = client['lkj']
collection = db['JBTI']

# MongoDB 연결 테스트
async def connect_to_mongo():
    try:
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


def clean_data(data):
    """Recursively clean data to ensure it is JSON serializable"""
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(i) for i in data]
    elif isinstance(data, float):
        if data != data or data == float('inf') or data == -float('inf'):
            return str(data)
        else:
            return data
    else:
        return data


async def fetch_job_fields():
    try:
        projection = {"직무": 1, "직종": 1, "_id": 0}
        cursor = collection.find({}, projection)
        results = await cursor.to_list(length=None)
        return clean_data(results)
    except Exception as e:
        logger.error(f"Error fetching job fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job fields")


async def fetch_job_details():
    try:
        projection = {"직종": 1, "직업 설명": 1, "수행 직무": 1, "필요기술 및 지식": 1, "직업 전망": 1, "_id": 0}
        cursor = collection.find({}, projection)
        results = await cursor.to_list(length=None)
        return clean_data(results)
    except Exception as e:
        logger.error(f"Error fetching job details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job details")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post("/api/users/register", response_model=UserInDB)
async def register_user(request: Request):
    user_data = await request.json()
    user = UserCreate(**user_data)
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    user_dict.pop("password")
    
    try:
        new_user = await db["users"].insert_one(user_dict)
        created_user = await db["users"].find_one({"_id": new_user.inserted_id})
        return UserInDB(**created_user)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")


# 유저 정보 가져오기 엔드포인드
@app.get("/api/users")
async def get_all_users():
    users = await db["users"].find().to_list(1000)
    return [user_helper(user) for user in users]


def user_helper(user) -> dict:
    if not user:
        raise ValueError("User object is required")

    return {
        "id": str(user.get("_id", "")),
        "userid": user.get("userid", ""),
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "hp": user.get("hp", ""),
        "hashed_password": user.get("hashed_password", ""),
    }

async def authenticate_user(userid: str, password: str):
    user = await db["users"].find_one({"userid": userid})
    if user and verify_password(password, user["hashed_password"]):
        return UserInDB(**user)
    return None

# 로그인
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.userid}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 로그인 유저 토큰 가져오기
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid: str = payload.get("sub")
        if userid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db["users"].find_one({"userid": userid})
    if user is None:
        raise credentials_exception
    return user

@app.delete("/delete_user")
async def delete_user(current_user: dict = Depends(get_current_user)):
    result = await db["users"].delete_one({"userid": current_user["userid"]})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/job-fields")
async def get_job_fields():
    try:
        data = await fetch_job_fields()
        return data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/job-details")
async def get_job_details():
    try:
        data = await fetch_job_details()
        return data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/job_info")
async def get_job_info(request: Request):
    return templates.TemplateResponse("job_info.html", {"request": request})

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/main")
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/api/selection")
async def get_selection(mbti: str, jobCategory: str):
    logging.info(f'Received MBTI: {mbti}, Job Category: {jobCategory}')
    if jobCategory not in allowed_job_category:
        raise HTTPException(status_code=400, detail="Invalid Job Category")
    # 요청받은 MBTI와 Job Category를 그대로 반환
    return {"mbti": mbti, "jobCategory": jobCategory}

@app.get("/selection", response_class=HTMLResponse)
async def selection_form(request: Request):
    return templates.TemplateResponse("selection.html", {"request": request})

@app.get("/loading", response_class=HTMLResponse)
async def get_loading(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/api/result", response_model=Result)
def get_result(mbti: str = Query(...), jobcategory: str = Query(...)):
    result = create_main(mbti, jobcategory)
    
    if isinstance(result, dict):  # 결과가 딕셔너리인 경우
        if result["line1"] != "No result found.":
            return Result(
                line1=result.get("line1",""),
                line2=result.get("line2",""),
                line3=result.get("line3",""),
                line4=result.get("line4",""),
                line5=result.get("line5",""),
                line6=result.get("line6",""),
                line7=result.get("line7","")
            )
        else:
            raise HTTPException(status_code=404, detail="Result not found for the given MBTI and Job Category")
    else:
        raise HTTPException(status_code=500, detail="Unexpected result format")

    
@app.get("/result", response_class=HTMLResponse)
async def show_result(request: Request, mbti: str, jobCategory: str):
    return templates.TemplateResponse("result.html", {"request": request, "mbti":mbti, "jobcategory":jobCategory})

@app.get("/api/users/me", response_model=UserInDB)
async def get_user_info(current_user: UserInDB = Depends(get_current_user)):
    return current_user

# Static files serving
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/join_in", response_class=HTMLResponse)
async def get_join_in(request: Request):
    return templates.TemplateResponse("join_in.html", {"request": request})

@app.get("/mypage", response_class=HTMLResponse)
async def get_mypage(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
