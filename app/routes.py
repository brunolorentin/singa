from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    VoucherCreate, VoucherUpdate, VoucherResponse, 
    VoucherListResponse, DeactivateVoucherResponse
)
from app import crud

router = APIRouter()

@router.post("/", response_model=VoucherResponse, status_code=201)
def create_voucher(voucher: VoucherCreate, db: Session = Depends(get_db)):
    """
    Create a new voucher
    
    - **discount_percentage**: Discount percentage (0-100)
    - **expiration_date**: Expiration date in ISO format
    """
    return crud.create_voucher(db=db, voucher_data=voucher)


@router.get("/", response_model=VoucherListResponse)
def list_vouchers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all vouchers with pagination
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    vouchers, total = crud.list_vouchers(db=db, page=page, page_size=page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return VoucherListResponse(
        items=vouchers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{code}", response_model=VoucherResponse)
def get_voucher(code: str, db: Session = Depends(get_db)):
    """
    Retrieve a voucher by code if it's active and not expired
    
    - **code**: Voucher code
    """
    voucher = crud.get_valid_voucher_by_code(db=db, code=code)
    
    if not voucher:
        raise HTTPException(
            status_code=404,
            detail="Voucher not found, expired, or inactive"
        )
    
    return voucher


@router.get("/check/{code}", response_model=VoucherResponse)
def check_voucher(code: str, db: Session = Depends(get_db)):
    """
    Check if a voucher exists (admin endpoint)
    
    - **code**: Voucher code
    """
    voucher = crud.get_voucher_by_code(db=db, code=code)
    
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return voucher


@router.put("/{code}", response_model=VoucherResponse)
def update_voucher(
    code: str,
    voucher: VoucherUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a voucher
    
    - **code**: Voucher code
    - **discount_percentage**: New discount percentage (optional)
    - **expiration_date**: New expiration date (optional)
    """
    db_voucher = crud.get_voucher_by_code(db=db, code=code)
    
    if not db_voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    updated_voucher = crud.update_voucher(db=db, code=code, voucher_data=voucher)
    return updated_voucher


@router.patch("/{code}/deactivate", response_model=DeactivateVoucherResponse)
def deactivate_voucher(code: str, db: Session = Depends(get_db)):
    """
    Deactivate a voucher
    
    - **code**: Voucher code
    """
    voucher = crud.get_voucher_by_code(db=db, code=code)
    
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    deactivated_voucher = crud.deactivate_voucher(db=db, code=code)
    
    return DeactivateVoucherResponse(
        message="Voucher deactivated successfully",
        code=deactivated_voucher.code,
        active=deactivated_voucher.active
    )


@router.delete("/{code}", status_code=204)
def delete_voucher(code: str, db: Session = Depends(get_db)):
    """
    Delete a voucher
    
    - **code**: Voucher code
    """
    success = crud.delete_voucher(db=db, code=code)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return None