from sqlalchemy.orm import Session
from app.models import Voucher
from app.schemas import VoucherCreate, VoucherUpdate
from datetime import datetime
import uuid

def generate_voucher_code(length: int = 12) -> str:
    return str(uuid.uuid4())

def create_voucher(db: Session, voucher_data: VoucherCreate) -> Voucher:
    """Create a new voucher"""
    # Generate unique code
    code = generate_voucher_code()
    while db.query(Voucher).filter(Voucher.code == code).first():
        code = generate_voucher_code()

    db_voucher = Voucher(
        code=code,
        discount_percentage=voucher_data.discount_percentage,
        expiration_date=voucher_data.expiration_date,
        active=True
    )
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    return db_voucher


def get_voucher_by_code(db: Session, code: str) -> Voucher | None:
    """Get a voucher by code"""
    return db.query(Voucher).filter(Voucher.code == code).first()


def get_valid_voucher_by_code(db: Session, code: str) -> Voucher | None:
    """Get a voucher by code if it's active and not expired"""
    voucher = db.query(Voucher).filter(Voucher.code == code).first()
    
    if not voucher:
        return None
    
    if not voucher.active:
        return None
    
    if voucher.expiration_date <= datetime.now():
        return None
    
    return voucher


def list_vouchers(db: Session, page: int = 1, page_size: int = 10) -> tuple[list[Voucher], int]:
    """List all vouchers with pagination"""
    skip = (page - 1) * page_size
    
    total = db.query(Voucher).count()
    vouchers = db.query(Voucher).offset(skip).limit(page_size).all()
    
    return vouchers, total


def update_voucher(db: Session, code: str, voucher_data: VoucherUpdate) -> Voucher | None:
    """Update a voucher"""
    voucher = db.query(Voucher).filter(Voucher.code == code).first()
    
    if not voucher:
        return None
    
    update_data = voucher_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(voucher, field, value)
    
    voucher.updated_at = datetime.now()
    db.commit()
    db.refresh(voucher)
    return voucher


def deactivate_voucher(db: Session, code: str) -> Voucher | None:
    """Deactivate a voucher"""
    voucher = db.query(Voucher).filter(Voucher.code == code).first()
    
    if not voucher:
        return None
    
    voucher.active = False
    voucher.updated_at = datetime.now()
    db.commit()
    db.refresh(voucher)
    return voucher