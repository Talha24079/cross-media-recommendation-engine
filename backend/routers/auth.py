from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from core.security import get_password_hash, create_access_token, verify_password, get_current_user
from core.config import settings
from core.database import get_db, get_mongodb
from models.user import User
from schemas.user import FavoriteItem, FavoriteItemCreate, UserCreate, Token, UserLogin, UserResponse
from services.community_authors import user_avatar_url
from services.user_preferences_service import UserPreferencesService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if username or email exists
    result = await db.execute(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=db_user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=db_user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    preferences_service = UserPreferencesService(mongo_db)
    try:
        favorites = await preferences_service.list_favorites(str(current_user.id))
    except Exception as e:
        import logging
        logging.getLogger("backend").warning(f"Failed to fetch favorites: {e}")
        favorites = []
    data = UserResponse.model_validate(current_user)
    return data.model_copy(
        update={
            "avatar_url": user_avatar_url(current_user.username),
            "favorite_items": favorites,
        }
    )


@router.post("/me/favorites", response_model=list[FavoriteItem])
async def add_manual_favorite(
    body: FavoriteItemCreate,
    current_user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    preferences_service = UserPreferencesService(mongo_db)
    favorites = await preferences_service.add_manual_favorite(
        str(current_user.id),
        body.title,
        body.media_type,
    )
    return favorites


@router.delete("/me/favorites", response_model=list[FavoriteItem])
async def remove_favorite(
    media_id: str | None = Query(None),
    title: str | None = Query(None),
    media_type: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    if not media_id and not (title and media_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide media_id or title+media_type",
        )

    preferences_service = UserPreferencesService(mongo_db)
    favorites = await preferences_service.remove_favorite(
        str(current_user.id),
        media_id=media_id,
        title=title,
        media_type=media_type,
    )
    return favorites
