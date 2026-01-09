import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import Token, TokenRefresh, UserCreate, UserLogin, UserResponse
from app.utils.security import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("app")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    사용자 등록

    - **email**: 고유한 이메일 주소
    - **username**: 고유한 사용자명 (3-100자)
    - **password**: 비밀번호 (최소 8자)
    - **full_name**: 전체 이름 (선택사항)
    """
    # 이메일 중복 확인
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        logger.warning(f"회원가입 실패: 중복된 이메일 {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일이 이미 등록되어 있습니다",
        )

    # 사용자명 중복 확인
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        logger.warning(f"회원가입 실패: 중복된 사용자명 {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자명이 이미 등록되어 있습니다",
        )

    # 새 사용자 생성
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=1,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"새 사용자 등록: {new_user.username} ({new_user.email})")
    return new_user


@router.post("/token", response_model=Token)
async def login(credentials: UserLogin, db: Annotated[Session, Depends(get_db)]):
    """
    로그인 및 토큰 발급

    - **email**: 사용자 이메일
    - **password**: 비밀번호

    반환:
    - **access_token**: 15분 유효한 접근 토큰
    - **refresh_token**: 7일 유효한 갱신 토큰
    """
    # 사용자 찾기
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        logger.warning(f"로그인 실패: 존재하지 않는 사용자 {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다",
        )

    # 비밀번호 검증
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"로그인 실패: 잘못된 비밀번호 {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다",
        )

    # 사용자 활성 상태 확인
    if not user.is_active:
        logger.warning(f"로그인 실패: 비활성 사용자 {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성 계정입니다",
        )

    # 토큰 생성
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)

    access_token = create_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    refresh_token = create_token(
        data={"sub": str(user.id), "email": user.email, "type": "refresh"},
        expires_delta=refresh_token_expires,
    )

    logger.info(f"사용자 로그인: {user.username}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Annotated[Session, Depends(get_db)]):
    """
    토큰 갱신

    - **refresh_token**: 갱신 토큰

    반환:
    - 새로운 접근 토큰과 갱신 토큰
    """
    from app.utils.security import decode_token

    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        logger.warning("토큰 갱신 실패: 유효하지 않은 갱신 토큰")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 갱신 토큰입니다",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        logger.warning(f"토큰 갱신 실패: 유효하지 않은 사용자 ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다",
        )

    # 새 토큰 생성
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)

    new_access_token = create_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    new_refresh_token = create_token(
        data={"sub": str(user.id), "email": user.email, "type": "refresh"},
        expires_delta=refresh_token_expires,
    )

    logger.info(f"토큰 갱신: {user.username}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
    }
