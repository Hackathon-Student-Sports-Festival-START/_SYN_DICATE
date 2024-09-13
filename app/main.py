from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import Database
from app.config import Config
from app.users.auth import get_password_hash, verify_password, create_access_token
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],  # Укажите ваш фронтенд адрес
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем базу данных
DB = None

# Конфигурация JWT
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Модель для регистрации
class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    university: str
    email: str
    phone: str
    password: str

# Модель для логина
class LoginRequest(BaseModel):
    email: str
    password: str

# Модель для ответа с токеном
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Событие запуска приложения для подключения к базе данных
@app.on_event("startup")
async def startup():
    global DB
    DB = Database(Config.db_name, Config.db_user, Config.db_user_pass)
    await DB.connect()
    await DB.create_tables()

@app.on_event("shutdown")
async def shutdown():
    await DB.disconnect()


@app.post("/register")
async def register_user(request: RegisterRequest):
    hashed_password = get_password_hash(request.password)
    user = await DB.get_user_by_email(request.email)
    if user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    await DB.add_new_user(
        email=request.email,
        password=hashed_password,
        first_name=request.firstName,
        last_name=request.lastName,
        university=request.university,
        phone=request.phone
    )
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = await DB.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Получение текущего пользователя из токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await DB.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

# Маршрут для получения профиля
@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user.get('name', 'Имя не указано'),
        "last_name": current_user.get('last_name', 'Фамилия не указана'),
        "university": current_user.get('university', 'Университет не указан'),
        "email": current_user.get('email', 'Email не указан'),
        "phone": current_user.get('phone', 'Телефон не указан')
    }


# Модель для обновления профиля
class UpdateProfileRequest(BaseModel):
    name: Optional[str]
    last_name: Optional[str]
    university: Optional[str]
    email: Optional[str]
    phone: Optional[str]


@app.put("/profile")
async def update_profile(request: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    # Проверка email, если его изменили
    if request.email and request.email != current_user['email']:
        existing_user = await DB.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # Обновляем профиль пользователя
    await DB.update_user_profile(
        current_user['email'],
        name=request.name,
        last_name=request.last_name,
        university=request.university,
        email=request.email,
        phone=request.phone
    )

    return {"message": "Профиль успешно обновлен"}