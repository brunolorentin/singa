import pytest

from pydantic import ValidationError
from datetime import timedelta
from app.vouchers.crud import generate_voucher_code, create_voucher, get_voucher_by_code, get_valid_voucher_by_code, \
    list_vouchers, update_voucher, deactivate_voucher
from app.vouchers.schemas import VoucherCreate, VoucherUpdate
from app.vouchers.models import Voucher


class TestVoucherCodeGeneration:
    """Test voucher code generation"""

    def test_generate_voucher_code_length(self):
        """Test that generated code has correct length"""
        code = generate_voucher_code(length=12)
        assert len(code) == 12

    def test_generate_voucher_code_custom_length(self):
        """Test code generation with custom length"""
        code = generate_voucher_code(length=20)
        assert len(code) == 20

    def test_generate_voucher_code_characters(self):
        """Test that generated code contains only uppercase and digits"""
        code = generate_voucher_code(length=50)
        assert all(c.isupper() or c.isdigit() for c in code)

    def test_generate_voucher_code_uniqueness(self):
        """Test that generated codes are unique"""
        codes = {generate_voucher_code() for _ in range(100)}
        assert len(codes) == 100


class TestCreateVoucher:
    """Test voucher creation"""

    def test_create_voucher_success(self, db, valid_future_date):
        """Test successful voucher creation"""
        voucher_data = VoucherCreate(
            discount_percentage=15.5,
            expiration_date=valid_future_date
        )
        voucher = create_voucher(db, voucher_data)

        assert voucher is not None
        assert voucher.code is not None
        assert len(voucher.code) == 12
        assert voucher.discount_percentage == 15.5
        assert voucher.expiration_date == valid_future_date
        assert voucher.active is True
        assert voucher.created_at is not None
        assert voucher.updated_at is not None

    def test_create_voucher_generates_unique_code(self, db, valid_future_date):
        """Test that each voucher gets a unique code"""
        voucher_data = VoucherCreate(
            discount_percentage=10.0,
            expiration_date=valid_future_date
        )
        voucher1 = create_voucher(db, voucher_data)
        voucher2 = create_voucher(db, voucher_data)

        assert voucher1.code != voucher2.code

    def test_create_voucher_with_various_discounts(self, db, valid_future_date):
        """Test creating vouchers with various discount percentages"""
        discounts = [1.0, 25.5, 50.0, 75.99, 100.0]

        for discount in discounts:
            voucher_data = VoucherCreate(
                discount_percentage=discount,
                expiration_date=valid_future_date
            )
            voucher = create_voucher(db, voucher_data)
            assert voucher.discount_percentage == discount

    def test_create_voucher_with_too_low_discount(self, valid_future_date):
        """Test successful voucher creation"""
        with pytest.raises(ValidationError):
            VoucherCreate(
                discount_percentage=-1,
                expiration_date=valid_future_date
            )

    def test_create_voucher_with_too_high_discount(self, valid_future_date):
        """Test successful voucher creation"""
        with pytest.raises(ValidationError):
            VoucherCreate(
                discount_percentage=101,
                expiration_date=valid_future_date
            )

    def test_create_voucher_with_past_expiration_date(self, expired_date):
        """Test successful voucher creation"""
        with pytest.raises(ValidationError):
            VoucherCreate(
                discount_percentage=101,
                expiration_date=expired_date
            )


class TestGetVoucher:
    """Test retrieving vouchers"""

    def test_get_voucher_by_code_exists(self, db, sample_voucher):
        """Test retrieving an existing voucher by code"""
        voucher = get_voucher_by_code(db, "TEST123456")
        assert voucher is not None
        assert voucher.code == "TEST123456"
        assert voucher.discount_percentage == 20.0

    def test_get_voucher_by_code_not_exists(self, db):
        """Test retrieving a non-existent voucher"""
        voucher = get_voucher_by_code(db, "NONEXISTENT")
        assert voucher is None

    def test_get_valid_voucher_active_and_not_expired(self, db, sample_voucher):
        """Test retrieving a valid active and non-expired voucher"""
        voucher = get_valid_voucher_by_code(db, "TEST123456")
        assert voucher is not None
        assert voucher.code == "TEST123456"

    def test_get_valid_voucher_inactive(self, db, sample_voucher):
        """Test retrieving an inactive voucher returns None"""
        sample_voucher.active = False
        db.commit()

        voucher = get_valid_voucher_by_code(db, "TEST123456")
        assert voucher is None

    def test_get_valid_voucher_expired(self, db, expired_date):
        """Test retrieving an expired voucher returns None"""
        voucher = Voucher(
            code="EXPIRED123",
            discount_percentage=10.0,
            expiration_date=expired_date,
            active=True
        )
        db.add(voucher)
        db.commit()

        result = get_valid_voucher_by_code(db, "EXPIRED123")
        assert result is None

    def test_get_valid_voucher_not_exists(self, db):
        """Test retrieving a non-existent voucher as valid returns None"""
        voucher = get_valid_voucher_by_code(db, "NONEXISTENT")
        assert voucher is None


class TestListVouchers:
    """Test listing vouchers"""

    def test_list_vouchers_empty(self, db):
        """Test listing when no vouchers exist"""
        vouchers, total = list_vouchers(db, page=1, page_size=10)
        assert vouchers == []
        assert total == 0

    def test_list_vouchers_single_page(self, db, valid_future_date):
        """Test listing vouchers on a single page"""
        for i in range(5):
            voucher_data = VoucherCreate(
                discount_percentage=10.0 + i,
                expiration_date=valid_future_date
            )
            create_voucher(db, voucher_data)

        vouchers, total = list_vouchers(db, page=1, page_size=10)
        assert len(vouchers) == 5
        assert total == 5

    def test_list_vouchers_pagination_first_page(self, db, valid_future_date):
        """Test pagination on first page"""
        for i in range(15):
            voucher_data = VoucherCreate(
                discount_percentage=10.0 + i,
                expiration_date=valid_future_date
            )
            create_voucher(db, voucher_data)

        vouchers, total = list_vouchers(db, page=1, page_size=10)
        assert len(vouchers) == 10
        assert total == 15

    def test_list_vouchers_pagination_second_page(self, db, valid_future_date):
        """Test pagination on second page"""
        for i in range(15):
            voucher_data = VoucherCreate(
                discount_percentage=10.0 + i,
                expiration_date=valid_future_date
            )
            create_voucher(db, voucher_data)

        vouchers, total = list_vouchers(db, page=2, page_size=10)
        assert len(vouchers) == 5
        assert total == 15

    def test_list_vouchers_custom_page_size(self, db, valid_future_date):
        """Test listing with custom page size"""
        for i in range(25):
            voucher_data = VoucherCreate(
                discount_percentage=10.0 + i,
                expiration_date=valid_future_date
            )
            create_voucher(db, voucher_data)

        vouchers, total = list_vouchers(db, page=1, page_size=5)
        assert len(vouchers) == 5
        assert total == 25


class TestUpdateVoucher:
    """Test updating vouchers"""

    def test_update_discount_percentage(self, db, sample_voucher):
        """Test updating discount percentage"""
        update_data = VoucherUpdate(discount_percentage=25.0)
        updated_voucher = update_voucher(db, "TEST123456", update_data)

        assert updated_voucher is not None
        assert updated_voucher.discount_percentage == 25.0

    def test_update_too_low_discount_percentage(self):
        """Test updating too low discount percentage"""
        with pytest.raises(ValidationError):
            VoucherUpdate(discount_percentage=-1)

    def test_update_too_high_discount_percentage(self):
        """Test updating too high discount percentage"""
        with pytest.raises(ValidationError):
            VoucherUpdate(discount_percentage=101)

    def test_update_expiration_date(self, db, sample_voucher, valid_future_date):
        """Test updating expiration date"""
        new_expiration = valid_future_date + timedelta(days=30)
        update_data = VoucherUpdate(expiration_date=new_expiration)
        updated_voucher = update_voucher(db, "TEST123456", update_data)

        assert updated_voucher is not None
        assert updated_voucher.expiration_date == new_expiration

    def test_update_past_expiration_date(self, expired_date):
        """Test updating past expiration date"""
        with pytest.raises(ValidationError):
            VoucherUpdate(expiration_date=expired_date)

    def test_update_both_fields(self, db, sample_voucher, valid_future_date):
        """Test updating both fields"""
        new_expiration = valid_future_date + timedelta(days=30)
        update_data = VoucherUpdate(
            discount_percentage=35.0,
            expiration_date=new_expiration
        )
        updated_voucher = update_voucher(db, "TEST123456", update_data)

        assert updated_voucher is not None
        assert updated_voucher.discount_percentage == 35.0
        assert updated_voucher.expiration_date == new_expiration

    def test_update_nonexistent_voucher(self, db, valid_future_date):
        """Test updating a non-existent voucher"""
        update_data = VoucherUpdate(discount_percentage=20.0)
        result = update_voucher(db, "NONEXISTENT", update_data)
        assert result is None

    def test_update_preserves_other_fields(self, db, sample_voucher):
        """Test that updating one field preserves others"""
        original_code = sample_voucher.code
        original_active = sample_voucher.active
        original_created_at = sample_voucher.created_at

        update_data = VoucherUpdate(discount_percentage=30.0)
        updated_voucher = update_voucher(db, "TEST123456", update_data)

        assert updated_voucher.code == original_code
        assert updated_voucher.active == original_active
        assert updated_voucher.created_at == original_created_at

    def test_update_updates_timestamp(self, db, sample_voucher):
        """Test that update timestamp is updated"""
        original_updated_at = sample_voucher.updated_at

        # Wait a moment to ensure timestamp differs
        import time
        time.sleep(0.01)

        update_data = VoucherUpdate(discount_percentage=30.0)
        updated_voucher = update_voucher(db, "TEST123456", update_data)

        assert updated_voucher.updated_at > original_updated_at


class TestDeactivateVoucher:
    """Test deactivating vouchers"""

    def test_deactivate_voucher_success(self, db, sample_voucher):
        """Test successful voucher deactivation"""
        voucher = deactivate_voucher(db, "TEST123456")

        assert voucher is not None
        assert voucher.active is False
        assert voucher.code == "TEST123456"

    def test_deactivate_already_inactive_voucher(self, db, sample_voucher):
        """Test deactivating an already inactive voucher"""
        sample_voucher.active = False
        db.commit()

        voucher = deactivate_voucher(db, "TEST123456")
        assert voucher is not None
        assert voucher.active is False

    def test_deactivate_nonexistent_voucher(self, db):
        """Test deactivating a non-existent voucher"""
        result = deactivate_voucher(db, "NONEXISTENT")
        assert result is None

    def test_deactivate_updates_timestamp(self, db, sample_voucher):
        """Test that deactivation updates timestamp"""
        original_updated_at = sample_voucher.updated_at

        import time
        time.sleep(0.01)

        voucher = deactivate_voucher(db, "TEST123456")
        assert voucher.updated_at > original_updated_at