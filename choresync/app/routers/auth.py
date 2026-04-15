"""인증 API — 회원가입, 로그인, 가족 생성, 가족 합류"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.family import Family, FamilyMember, Invitation, InvitationStatus, MemberRole
from app.models.user import User
from app.schemas.auth import (
    CreateFamilyRequest,
    JoinFamilyRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.family import FamilyResponse
from app.security import create_access_token, hash_password, verify_password
from app.seed_templates import seed_templates

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 등록된 이메일입니다")

    user = User(email=req.email, password_hash=hash_password(req.password), name=req.name)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 이메일 사전 지정 초대 확인 — 이 이메일로 초대된 미수락 초대가 있으면 자동 합류
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    pending_inv = (
        db.query(Invitation)
        .filter(
            Invitation.invited_email == req.email,
            Invitation.status == InvitationStatus.PENDING,
        )
        .first()
    )
    if pending_inv:
        expires = pending_inv.expires_at if pending_inv.expires_at.tzinfo is None else pending_inv.expires_at.replace(tzinfo=None)
        if expires >= now:
            member = FamilyMember(
                user_id=user.id,
                family_id=pending_inv.family_id,
                role=MemberRole.MEMBER,
                family_role="기타",
            )
            db.add(member)
            db.flush()
            pending_inv.status = InvitationStatus.ACCEPTED
            pending_inv.accepted_by = member.id
            db.commit()
        else:
            pending_inv.status = InvitationStatus.EXPIRED
            db.commit()

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 잘못되었습니다")

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/create-family", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    req: CreateFamilyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = Family(name=req.name, created_by=current_user.id)
    db.add(family)
    db.flush()

    # 생성자를 Admin으로 추가
    member = FamilyMember(
        user_id=current_user.id,
        family_id=family.id,
        role=MemberRole.ADMIN,
        family_role=req.family_role,
    )
    db.add(member)
    db.flush()

    # 가족 유형에 맞는 템플릿 시드
    seed_templates(family.id, member.id, db, pack=req.family_pack)

    db.commit()
    db.refresh(family)

    return family


@router.post("/join-family", response_model=FamilyResponse)
def join_family(
    req: JoinFamilyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 초대 코드로 가족 찾기
    invitation = (
        db.query(Invitation)
        .filter(
            Invitation.code == req.invite_code,
            Invitation.status == InvitationStatus.PENDING,
        )
        .first()
    )

    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 초대 코드입니다")

    # 만료 확인
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires = invitation.expires_at if invitation.expires_at.tzinfo is None else invitation.expires_at.replace(tzinfo=None)
    if expires < now:
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="만료된 초대 코드입니다")

    # 이미 가족 구성원인지 확인
    existing = (
        db.query(FamilyMember)
        .filter(
            FamilyMember.user_id == current_user.id,
            FamilyMember.family_id == invitation.family_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 이 가족의 구성원입니다")

    # 구성원 추가
    member = FamilyMember(
        user_id=current_user.id,
        family_id=invitation.family_id,
        role=MemberRole.MEMBER,
        family_role=req.family_role,
        age=req.age,
    )
    db.add(member)

    # 초대 수락 처리
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_by = member.id

    db.commit()
    db.refresh(member)

    family = db.get(Family, invitation.family_id)
    return family


# ─── 임시 관리자용 엔드포인트 (로컬 전용) ────────────────────────────────────
@router.post("/admin/reset-password")
def admin_reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    """로컬 관리자용 비밀번호 초기화 (배포 후 제거 예정)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # 없으면 새로 생성
        user = User(email=email, password_hash=hash_password(new_password), name=email.split("@")[0])
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"created": True, "user_id": user.id}
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"reset": True, "user_id": user.id, "email": user.email}


@router.post("/language")
def set_language(
    lang: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """사용자 언어 설정 변경 (ko / en)"""
    if lang not in {"ko", "en"}:
        raise HTTPException(status_code=400, detail="지원하지 않는 언어입니다")
    current_user.language = lang
    db.commit()
    response.set_cookie("lang", lang, max_age=86400 * 365, httponly=False, samesite="lax")
    return {"lang": lang}
