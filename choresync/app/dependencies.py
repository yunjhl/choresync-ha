"""FastAPI 의존성 — 인증 + 권한 검증"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.family import FamilyMember, MemberRole
from app.models.user import User
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """JWT에서 현재 사용자 추출"""
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없음")
    return user


def get_family_member(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMember:
    """현재 사용자가 해당 가족의 구성원인지 확인"""
    member = (
        db.query(FamilyMember)
        .filter(FamilyMember.user_id == current_user.id, FamilyMember.family_id == family_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 가족의 구성원이 아닙니다")
    return member


def get_admin_member(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMember:
    """현재 사용자가 해당 가족의 Admin인지 확인"""
    member = get_family_member(family_id, current_user, db)
    if member.role != MemberRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin 권한이 필요합니다")
    return member
