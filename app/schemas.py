from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class VoucherCreate(BaseModel):
    discount_percentage: float = Field(..., gt=0, le=100, description="Discount percentage between 0 and 100")
    expiration_date: datetime = Field(..., description="Voucher expiration date")

    @validator("discount_percentage")
    def validate_discount(cls, v):
        if v <= 0 or v > 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        return v

    @validator("expiration_date")
    def validate_expiration_date(cls, v):
        if v <= datetime.now():
            raise ValueError("Expiration date must be in the future")
        return v


class VoucherUpdate(BaseModel):
    discount_percentage: Optional[float] = Field(None, gt=0, le=100)
    expiration_date: Optional[datetime] = None

    @validator("discount_percentage")
    def validate_discount(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError("Discount percentage must be between 0 and 100")
        return v

    @validator("expiration_date")
    def validate_expiration_date(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError("Expiration date must be in the future")
        return v


class VoucherResponse(BaseModel):
    code: str
    discount_percentage: float
    expiration_date: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoucherListResponse(BaseModel):
    items: list[VoucherResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


class VoucherDetailResponse(VoucherResponse):
    pass


class DeactivateVoucherResponse(BaseModel):
    message: str
    code: str
    active: bool

    model_config = {"from_attributes": True}