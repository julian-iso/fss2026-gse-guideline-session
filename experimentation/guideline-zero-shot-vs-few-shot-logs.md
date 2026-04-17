### Experiment 3: Zero-Shot E2E Test (Failed)

**Prompt:**
```
Generate an integration test for a payment processing endpoint that requires 
authentication. The endpoint is POST /api/payments and expects a JSON body 
with amount and currency.
```

**LLM Output (Claude 4.5 Sonnet):**
To create a robust integration test for a protected payment endpoint, you should ensure the test covers both successful authorization and the validation of the payment payload.

The following example uses **Node.js** with **Jest** and **Supertest**, assuming a standard REST structure.

---

### Payment Integration Test

```javascript
const request = require('supertest');
const app = require('../app'); // Path to your Express/Node app
const { generateAuthToken } = require('./testHelpers');

describe('POST /api/payments', () => {
  const endpoint = '/api/payments';

  ### Success Scenarios
  it('should process a payment when authenticated with valid data', async () => {
    const token = generateAuthToken({ userId: 123 });
    const paymentData = {
      amount: 50.00,
      currency: 'USD'
    };

    const response = await request(app)
      .post(endpoint)
      .set('Authorization', `Bearer ${token}`)
      .send(paymentData);

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
    expect(response.body.status).toBe('completed');
  });

  ---

  ### Security & Authentication
  it('should return 401 Unauthorized if no token is provided', async () => {
    const response = await request(app)
      .post(endpoint)
      .send({ amount: 10, currency: 'USD' });

    expect(response.status).toBe(401);
  });

  it('should return 403 Forbidden if the token is invalid', async () => {
    const response = await request(app)
      .post(endpoint)
      .set('Authorization', 'Bearer invalid-token-123')
      .send({ amount: 10, currency: 'USD' });

    expect(response.status).toBe(403);
  });

  ---

  ### Validation Scenarios
  it('should return 400 Bad Request if amount is missing', async () => {
    const token = generateAuthToken({ userId: 123 });
    
    const response = await request(app)
      .post(endpoint)
      .set('Authorization', `Bearer ${token}`)
      .send({ currency: 'EUR' });

    expect(response.status).toBe(400);
    expect(response.body.error).toMatch(/amount/i);
  });
});
```

### Key Considerations for Integration Testing
* **Database State:** Ensure you are using a test database or wrapping your tests in transactions that roll back to keep tests isolated.
* **Mocking External APIs:** If your endpoint calls a third-party gateway (like Stripe or PayPal), use tools like `nock` or provide a mock service to avoid real transactions during testing.
* **Environment Variables:** Verify that your test environment uses a specific `.env.test` file to prevent accidental production data overrides.

**Issues:**
- Includes authentication via `generateAuthToken()` but assumes this helper exists without defining it
- No PyTest fixtures or setup (`@pytest.fixture`) - uses JavaScript/Jest patterns instead
- No database state management implementation (only mentioned in "Key Considerations")
- Framework mismatch: generated JavaScript/Jest code when Python context might be expected from prompt

---

### Experiment 4: Few-Shot with Project Context

**Prompt:**
```
Generate an integration test for the payment processing endpoint. 
Use this existing test as a reference for authentication setup:

# Example from our test suite:
@pytest.fixture
def authenticated_client(client, test_user):
    token = create_test_token(test_user)
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client

def test_user_profile(authenticated_client):
    response = authenticated_client.get("/api/user/profile")
    assert response.status_code == 200

Now generate a test for POST /api/payments with amount and currency fields.
```

**LLM Output (Gemini 3):**
Building an integration test for payment processing requires ensuring both the **authentication layer** and the **request payload** are handled correctly. Since payment endpoints often interact with external gateways, this test focuses on the API structure and the expected response from your server.

---

## Integration Test Implementation

Below is the test case for the `POST /api/payments` endpoint, utilizing your existing `authenticated_client` fixture logic.

```python
import pytest

@pytest.mark.django_db
def test_create_payment_success(authenticated_client):
    """
    Test successful payment initiation with valid amount and currency.
    """
    endpoint = "/api/payments"
    payload = {
        "amount": 5000,
        "currency": "USD"
    }

    # Execute the POST request
    response = authenticated_client.post(
        endpoint, 
        data=payload, 
        content_type="application/json"
    )

    # Assertions
    assert response.status_code == 201
    assert response.data["amount"] == payload["amount"]
    assert response.data["currency"] == payload["currency"]
    assert "id" in response.data  # Ensure a payment ID is returned

@pytest.mark.django_db
def test_create_payment_unauthorized(client):
    """
    Test that the payment endpoint rejects requests without a valid token.
    """
    endpoint = "/api/payments"
    payload = {
        "amount": 100,
        "currency": "USD"
    }

    # Using the unauthenticated 'client' fixture
    response = client.post(
        endpoint, 
        data=payload, 
        content_type="application/json"
    )

    assert response.status_code == 401
```

---

### Key Considerations for Payment Testing

| Aspect | Recommendation |
| :--- | :--- |
| **Idempotency** | For payments, consider adding an `idempotency_key` in the headers to prevent duplicate charges during retries. |
| **Validation** | Add a test case for invalid currencies (e.g., "XYZ") or negative amounts to ensure your `400 Bad Request` logic is robust. |
| **Mocking** | If your endpoint calls a third-party API (like Stripe or PayPal), use `unittest.mock` to prevent actual API calls during integration tests. |

> **Note:** Ensure your `create_test_token` helper is imported or available in the scope where your fixtures are defined to avoid `NameError` during the test run.

---

### Experiment 5: Full Build Log (Caused Regressions)

**Prompt:**
```
Fix the failing tests. Here is the complete pytest output:

============================= test session starts ==============================
collected 15 items

tests/test_auth.py::test_login PASSED                                    [  6%]
tests/test_auth.py::test_logout PASSED                                   [ 13%]
tests/test_payment.py::test_payment_validation FAILED                    [ 20%]
tests/test_payment.py::test_payment_processing PASSED                    [ 26%]
tests/test_user.py::test_user_creation PASSED                            [ 33%]
tests/test_user.py::test_user_update PASSED                              [ 40%]
tests/test_user.py::test_user_deletion PASSED                            [ 46%]
... (8 more tests)

================================== FAILURES ===================================
______________________________ test_payment_validation ________________________

    def test_payment_validation():
        payment = Payment(amount=-50.00, currency="USD")
>       assert payment.validate() == False
E       AssertionError: assert True == False
E        +  where True = <bound method Payment.validate of <Payment object>>()

tests/test_payment.py:45: AssertionError
=========================== short test summary info ============================
FAILED tests/test_payment.py::test_payment_validation - AssertionError
======================== 1 failed, 14 passed in 2.34s =========================

Here are all the test files:

[test_auth.py - 150 lines]
[test_payment.py - 200 lines]
[test_user.py - 180 lines]
```

**LLM Output (Gemini 3):**
It looks like your `Payment.validate()` method is a bit too optimistic. Based on the test failure, it is returning `True` for a negative amount (`-50.00`), which is likely why your assertion failed.

To fix this, you need to update the logic in your `Payment` class to ensure that the amount is greater than zero.

---

### **The Fix**

In your source code (likely in a file like `models/payment.py` or wherever the `Payment` class is defined), update the `validate` method.

```python
class Payment:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def validate(self) -> bool:
        """
        Validates the payment details.
        Returns False if the amount is zero or negative.
        """
        # The fix: Ensure amount is positive
        if self.amount <= 0:
            return False
        
        # Add other validation logic here (e.g., currency checks)
        return True
```

---

### **Why this failed**
* **The Input:** The test initialized a `Payment` object with `amount=-50.00`.
* **The Expectation:** The test expected `payment.validate()` to return `False` (since you can't really have a negative payment amount in this context).
* **The Reality:** The actual implementation of `validate()` returned `True`, triggering the `AssertionError: assert True == False`.

### **Verification**
After applying the change, run your tests again:
```bash
pytest tests/test_payment.py
```
This should now show `test_payment_validation` as **PASSED**.

---

### Experiment 6: Targeted Traceback Only

**Prompt:**
```
The test `test_payment_validation` failed with an AssertionError. 
Here is the isolated test code and the stack trace. 
Fix the logic for this specific assertion only.

Failing test:
def test_payment_validation():
    payment = Payment(amount=-50.00, currency="USD")
    assert payment.validate() == False

Error:
AssertionError: assert True == False
 +  where True = <bound method Payment.validate of <Payment object>>()
tests/test_payment.py:45: AssertionError

Context: The Payment.validate() method should return False for negative amounts.
```

**LLM Output (Gemini 3):**
To fix the failing test, you need to update the `validate` method within your `Payment` class to check if the `amount` is greater than or equal to zero. 

Based on the error, the current implementation is likely returning `True` by default or missing the logic to handle negative values.

### Updated Logic

```python
class Payment:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def validate(self):
        # Ensure the amount is not negative
        if self.amount < 0:
            return False
        
        # Existing validation logic (e.g., checking currency) would go here
        return True
```

---

### Why this fixes it
The `AssertionError` occurred because `payment.validate()` returned `True` for an amount of `-50.00`. 
* **The Problem:** The method was likely only checking for the existence of data or had no bounds checking for numerical values.
* **The Solution:** By adding `if self.amount < 0: return False`, the method now correctly identifies negative transactions as invalid, satisfying the assertion `assert payment.validate() == False`.

---

## Cross-Model Comparison

### Claude 4.5 Sonnet - Zero-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.
The method requires an authenticated user and creates a payment with amount, 
currency, and description. The payment should be stored in the database.

Requirements:
- Test successful payment creation
- Test authentication requirement
- Test database state after payment creation

Use PyTest and include all necessary fixtures.
```

**LLM Output:**
```
# Integration Tests for PaymentService.create_payment()

Here's a comprehensive PyTest integration test suite for the `PaymentService.create_payment()` method:

```python
"""
Integration tests for PaymentService.create_payment() method.

Tests cover authentication requirements, successful payment creation,
database state validation, and edge cases.
"""

import pytest
from datetime import datetime
from typing import Generator


# Fixtures

@pytest.fixture
def database() -> Generator[PaymentDatabase, None, None]:
    """Provide a clean database instance for each test."""
    db = PaymentDatabase()
    yield db
    db.clear()  # Cleanup after test


@pytest.fixture
def payment_service(database: PaymentDatabase) -> PaymentService:
    """Provide a PaymentService instance with a clean database."""
    return PaymentService(database)


@pytest.fixture
def active_user(database: PaymentDatabase) -> User:
    """Provide an active user registered in the database."""
    user = User("user_001", "john_doe", "john@example.com", is_active=True)
    database.add_user(user)
    return user


@pytest.fixture
def authenticated_user(active_user: User) -> User:
    """Provide an authenticated user."""
    active_user.authenticate("john_doe_pass")
    assert active_user.is_authenticated()
    return active_user


@pytest.fixture
def inactive_user(database: PaymentDatabase) -> User:
    """Provide an inactive user registered in the database."""
    user = User("user_002", "jane_doe", "jane@example.com", is_active=False)
    database.add_user(user)
    return user


# Test Cases

class TestPaymentServiceCreatePayment:
    """Integration tests for PaymentService.create_payment()."""

    def test_successful_payment_creation(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test that an authenticated user can successfully create a payment."""
        # Arrange
        amount = 99.99
        currency = Currency.USD
        description = "Test payment for product purchase"

        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=amount,
            currency=currency,
            description=description
        )

        # Assert - Payment object returned
        assert payment is not None
        assert payment.payment_id.startswith("pay_")
        assert payment.user_id == authenticated_user.user_id
        assert payment.amount == amount
        assert payment.currency == currency
        assert payment.description == description
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.created_at is not None
        assert payment.completed_at is not None

        # Assert - Payment stored in database
        stored_payment = database.get_payment(payment.payment_id)
        assert stored_payment is not None
        assert stored_payment.payment_id == payment.payment_id
        assert stored_payment.user_id == authenticated_user.user_id
        assert stored_payment.amount == amount
        assert stored_payment.status == PaymentStatus.COMPLETED

        # Assert - Payment appears in user's history
        user_payments = database.get_user_payments(authenticated_user.user_id)
        assert len(user_payments) == 1
        assert user_payments[0].payment_id == payment.payment_id


    def test_authentication_required(
        self,
        payment_service: PaymentService,
        active_user: User
    ):
        """Test that unauthenticated users cannot create payments."""
        # Arrange - User is not authenticated
        assert not active_user.is_authenticated()

        # Act & Assert
        with pytest.raises(PermissionError, match="User must be authenticated"):
            payment_service.create_payment(
                user=active_user,
                amount=50.00,
                currency=Currency.USD,
                description="Should fail"
            )


    def test_inactive_user_cannot_create_payment(
        self,
        payment_service: PaymentService,
        inactive_user: User
    ):
        """Test that inactive users cannot create payments even when authenticated."""
        # Arrange - Authenticate but user is inactive
        inactive_user.auth_token = "fake_token"  # Simulate authentication
        assert inactive_user.is_authenticated()
        assert not inactive_user.is_active

        # Act & Assert
        with pytest.raises(ValueError, match="User account is not active"):
            payment_service.create_payment(
                user=inactive_user,
                amount=50.00,
                currency=Currency.USD,
                description="Should fail"
            )


    def test_database_state_after_payment_creation(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test database state after creating payment."""
        # Arrange
        initial_payment_count = len(database.payments)

        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=150.00,
            currency=Currency.EUR,
            description="Database state test"
        )

        # Assert - Database updated correctly
        assert len(database.payments) == initial_payment_count + 1
        assert payment.payment_id in database.payments
        
        # Assert - Payment can be retrieved
        retrieved_payment = database.get_payment(payment.payment_id)
        assert retrieved_payment is not None
        assert retrieved_payment.user_id == authenticated_user.user_id
        assert retrieved_payment.amount == 150.00
        assert retrieved_payment.currency == Currency.EUR


    def test_multiple_payments_for_same_user(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test that a user can create multiple payments."""
        # Act - Create multiple payments
        payment1 = payment_service.create_payment(
            user=authenticated_user,
            amount=25.00,
            currency=Currency.USD,
            description="First payment"
        )
        payment2 = payment_service.create_payment(
            user=authenticated_user,
            amount=50.00,
            currency=Currency.EUR,
            description="Second payment"
        )
        payment3 = payment_service.create_payment(
            user=authenticated_user,
            amount=75.00,
            currency=Currency.GBP,
            description="Third payment"
        )

        # Assert - All payments created
        assert payment1 is not None
        assert payment2 is not None
        assert payment3 is not None

        # Assert - All have unique IDs
        payment_ids = {payment1.payment_id, payment2.payment_id, payment3.payment_id}
        assert len(payment_ids) == 3

        # Assert - All stored in database
        user_payments = database.get_user_payments(authenticated_user.user_id)
        assert len(user_payments) == 3


    def test_invalid_payment_amount_zero(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test that payments with zero amount are rejected."""
        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=0.0,
            currency=Currency.USD,
            description="Zero amount"
        )

        # Assert - Payment not created
        assert payment is None
        assert len(database.payments) == 0


    def test_invalid_payment_amount_negative(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test that payments with negative amount are rejected."""
        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=-50.00,
            currency=Currency.USD,
            description="Negative amount"
        )

        # Assert - Payment not created
        assert payment is None
        assert len(database.payments) == 0


    def test_invalid_payment_amount_exceeds_limit(
        self,
        payment_service: PaymentService,
        authenticated_user: User,
        database: PaymentDatabase
    ):
        """Test that payments exceeding maximum limit are rejected."""
        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=10001.00,  # Exceeds 10000 limit
            currency=Currency.USD,
            description="Exceeds limit"
        )

        # Assert - Payment not created
        assert payment is None
        assert len(database.payments) == 0


    def test_payment_with_all_currency_types(
        self,
        payment_service: PaymentService,
        authenticated_user: User
    ):
        """Test payment creation with all supported currencies."""
        # Act & Assert
        for currency in Currency:
            payment = payment_service.create_payment(
                user=authenticated_user,
                amount=100.00,
                currency=currency,
                description=f"Payment in {currency.value}"
            )
            assert payment is not None
            assert payment.currency == currency
            assert payment.status == PaymentStatus.COMPLETED


    def test_payment_description_optional(
        self,
        payment_service: PaymentService,
        authenticated_user: User
    ):
        """Test that payment description is optional."""
        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=99.99,
            currency=Currency.USD
            # No description provided
        )

        # Assert
        assert payment is not None
        assert payment.description == ""


    def test_payment_timestamps_set_correctly(
        self,
        payment_service: PaymentService,
        authenticated_user: User
    ):
        """Test that payment timestamps are set correctly."""
        # Arrange
        before_creation = datetime.now()

        # Act
        payment = payment_service.create_payment(
            user=authenticated_user,
            amount=99.99,
            currency=Currency.USD,
            description="Timestamp test"
        )

        # Assert
        after_creation = datetime.now()
        assert payment.created_at >= before_creation
        assert payment.created_at <= after_creation
        assert payment.completed_at is not None
        assert payment.completed_at >= payment.created_at
```

This test suite covers:

- Successful payment creation: Validates the payment object and database state
- Authentication requirement: Tests that unauthenticated users are rejected
- Database state: Verifies payments are correctly stored and retrievable
- Edge cases: Invalid amounts, inactive users, multiple payments, currency types

All tests use proper fixtures for isolation and cleanup. Would you like me to add tests for any additional scenarios?

---

### Claude 4.5 Sonnet - Few-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.

Here is an example test from our codebase showing the authentication pattern:

    import pytest
    from payment_system import User, PaymentDatabase, PaymentService

    @pytest.fixture
    def database():
        db = PaymentDatabase()
        yield db
        db.clear()

    @pytest.fixture
    def authenticated_user(database):
        user = User("test_001", "testuser", "test@example.com")
        database.add_user(user)
        user.authenticate("testuser_pass")
        return user

    @pytest.fixture
    def service(database):
        return PaymentService(database)

    def test_user_authentication(authenticated_user):
        assert authenticated_user.is_authenticated() is True
        assert authenticated_user.auth_token is not None

Now generate a test for PaymentService.create_payment() that:
- Uses the same fixture pattern
- Tests successful payment creation with amount=100.00, currency=USD
- Verifies the payment is stored in the database
- Checks the payment status is COMPLETED
```

**LLM Output:**
```python
import pytest
from payment_system import User, PaymentDatabase, PaymentService, Currency, PaymentStatus

@pytest.fixture
def database():
    db = PaymentDatabase()
    yield db
    db.clear()

@pytest.fixture
def authenticated_user(database):
    user = User("test_001", "testuser", "test@example.com")
    database.add_user(user)
    user.authenticate("testuser_pass")
    return user

@pytest.fixture
def service(database):
    return PaymentService(database)

def test_create_payment_success(authenticated_user, service, database):
    # Act
    payment = service.create_payment(
        user=authenticated_user,
        amount=100.00,
        currency=Currency.USD,
        description="Test payment"
    )
    
    # Assert - payment object returned
    assert payment is not None
    assert payment.payment_id is not None
    assert payment.user_id == authenticated_user.user_id
    assert payment.amount == 100.00
    assert payment.currency == Currency.USD
    
    # Assert - payment status is COMPLETED
    assert payment.status == PaymentStatus.COMPLETED
    assert payment.completed_at is not None
    
    # Assert - payment is stored in database
    stored_payment = database.get_payment(payment.payment_id)
    assert stored_payment is not None
    assert stored_payment.payment_id == payment.payment_id
    assert stored_payment.status == PaymentStatus.COMPLETED
    
    # Assert - payment appears in user's history
    user_payments = database.get_user_payments(authenticated_user.user_id)
    assert len(user_payments) == 1
    assert user_payments[0].payment_id == payment.payment_id
```

This integration test follows the established fixture pattern and comprehensively verifies that:
1. The payment object is successfully created and returned
2. The payment has the correct amount (100.00) and currency (USD)
3. The payment status is set to COMPLETED
4. The payment is persisted in the database
5. The payment can be retrieved and contains the expected data

Would you like me to add additional test cases for edge scenarios like authentication failures or invalid payment amounts?

---

### Gemini 2.5 Pro - Zero-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.
The method requires an authenticated user and creates a payment with amount, 
currency, and description. The payment should be stored in the database.

Requirements:
- Test successful payment creation
- Test authentication requirement
- Test database state after payment creation

Use PyTest and include all necessary fixtures.
```

**LLM Output:**
Of course. Here is a complete integration test for the `PaymentService.create_payment()` method using PyTest, including all necessary fixtures to test for success, authentication, and database state.

```python
import pytest

# Assuming the provided classes (User, Payment, PaymentDatabase, etc.)
# are in a file named `payment_system.py`
from payment_system import (
    PaymentDatabase,
    PaymentService,
    User,
    Currency,
    PaymentStatus,
    Payment,
)


# --- Fixtures for Test Setup ---

@pytest.fixture
def db_instance() -> PaymentDatabase:
    """
    Provides a clean, in-memory database for each test function.
    It yields the database and then clears it after the test is complete.
    """
    db = PaymentDatabase()
    yield db
    db.clear()


@pytest.fixture
def payment_service(db_instance: PaymentDatabase) -> PaymentService:
    """Provides a PaymentService instance linked to the test database."""
    return PaymentService(database=db_instance)


@pytest.fixture
def active_user(db_instance: PaymentDatabase) -> User:
    """
    Provides an active, unauthenticated user and adds them to the database.
    """
    user = User(user_id="user_001", username="test_user", email="test@example.com")
    db_instance.add_user(user)
    return user


@pytest.fixture
def authenticated_user(active_user: User) -> User:
    """Provides an authenticated version of the active_user."""
    # The password logic is simplified for the test
    active_user.authenticate("test_user_pass")
    return active_user


# --- Integration Tests for PaymentService.create_payment() ---

def test_create_payment_success_and_database_state(
    payment_service: PaymentService,
    authenticated_user: User,
    db_instance: PaymentDatabase,
):
    """
    Tests successful payment creation for an authenticated user and
    verifies that the payment is correctly stored in the database.
    """
    # Arrange
    amount = 99.99
    currency = Currency.USD
    description = "A successful test payment"

    # Act
    payment = payment_service.create_payment(
        user=authenticated_user,
        amount=amount,
        currency=currency,
        description=description,
    )

    # Assert: Check that a valid Payment object was returned
    assert payment is not None
    assert isinstance(payment, Payment)
    assert payment.user_id == authenticated_user.user_id
    assert payment.amount == amount
    assert payment.currency == currency
    assert payment.status == PaymentStatus.COMPLETED

    # Assert: Verify the database state after creation
    user_payments = db_instance.get_user_payments(authenticated_user.user_id)
    assert len(user_payments) == 1, "Database should contain exactly one payment for the user."

    retrieved_payment = user_payments[0]
    assert retrieved_payment.payment_id == payment.payment_id
    assert retrieved_payment.amount == amount


def test_create_payment_requires_authentication(
    payment_service: PaymentService, active_user: User, db_instance: PaymentDatabase
):
    """
    Tests that calling create_payment with an unauthenticated user
    raises a PermissionError and does not create a payment.
    """
    # Arrange: The 'active_user' fixture provides a user that is not authenticated.
    assert not active_user.is_authenticated()

    # Act & Assert: The method call should raise a PermissionError
    with pytest.raises(PermissionError, match="User must be authenticated"):
        payment_service.create_payment(
            user=active_user,
            amount=50.00,
            currency=Currency.EUR,
            description="Attempted payment without auth",
        )

    # Assert: Ensure no payment was added to the database
    user_payments = db_instance.get_user_payments(active_user.user_id)
    assert len(user_payments) == 0, "No payment should be created for an unauthenticated user."

```

Would you like to see how to write a test for another scenario, such as creating a payment with an invalid amount or for an inactive user?

---

### Gemini 2.5 Pro - Few-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.

Here is an example test from our codebase showing the authentication pattern:

    import pytest
    from payment_system import User, PaymentDatabase, PaymentService

    @pytest.fixture
    def database():
        db = PaymentDatabase()
        yield db
        db.clear()

    @pytest.fixture
    def authenticated_user(database):
        user = User("test_001", "testuser", "test@example.com")
        database.add_user(user)
        user.authenticate("testuser_pass")
        return user

    @pytest.fixture
    def service(database):
        return PaymentService(database)

    def test_user_authentication(authenticated_user):
        assert authenticated_user.is_authenticated() is True
        assert authenticated_user.auth_token is not None

Now generate a test for PaymentService.create_payment() that:
- Uses the same fixture pattern
- Tests successful payment creation with amount=100.00, currency=USD
- Verifies the payment is stored in the database
- Checks the payment status is COMPLETED
```

**LLM Output:**
```
Of course. Here is an integration test for the `PaymentService.create_payment()` method that follows your specified pattern and requirements.

```python
import pytest
from payment_system import (
    User,
    PaymentDatabase,
    PaymentService,
    Currency,
    PaymentStatus,
)


@pytest.fixture
def database():
    """Provides a clean, isolated database instance for each test."""
    db = PaymentDatabase()
    yield db
    db.clear()


@pytest.fixture
def authenticated_user(database):
    """Creates and authenticates a user, adding them to the database."""
    user = User("test_001", "testuser", "test@example.com")
    database.add_user(user)
    user.authenticate("testuser_pass")
    return user


@pytest.fixture
def service(database):
    """Provides a PaymentService instance initialized with the test database."""
    return PaymentService(database)


def test_create_payment_success(service, authenticated_user):
    """
    Tests successful creation of a payment for an authenticated user.
    """
    # Arrange
    amount = 100.00
    currency = Currency.USD
    description = "Test purchase"

    # Act
    payment = service.create_payment(
        user=authenticated_user,
        amount=amount,
        currency=currency,
        description=description,
    )

    # Assert
    assert payment is not None
    assert payment.user_id == authenticated_user.user_id
    assert payment.amount == amount
    assert payment.currency == currency
    assert payment.description == description

    # Verify the payment status is COMPLETED
    assert payment.status == PaymentStatus.COMPLETED

    # Verify the payment is stored correctly in the database
    db_payment = service.db.get_payment(payment.payment_id)
    assert db_payment is not None
    assert db_payment.payment_id == payment.payment_id
    assert db_payment.status == PaymentStatus.COMPLETED
```

Would you also like to see a test for a scenario where payment creation should fail, for instance, if the user is not authenticated?

---

### GPT-5 - Zero-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.
The method requires an authenticated user and creates a payment with amount, 
currency, and description. The payment should be stored in the database.

Requirements:
- Test successful payment creation
- Test authentication requirement
- Test database state after payment creation

Use PyTest and include all necessary fixtures.

**LLM Output:**
```
# test_payment_service_integration.py
# Note: Adjust the import path below to match where your classes are defined.
# For example, if your module is named `payment_module.py`, use:
# from payment_module import PaymentDatabase, PaymentService, User, Currency, PaymentStatus

import pytest

try:
    from payment_processing_system import (
        PaymentDatabase,
        PaymentService,
        User,
        Currency,
        PaymentStatus,
    )
except Exception:
    # Fallback if tests run in an environment where the classes are in __main__ (e.g., a single-file execution)
    from __main__ import (
        PaymentDatabase,
        PaymentService,
        User,
        Currency,
        PaymentStatus,
    )


@pytest.fixture
def db():
    return PaymentDatabase()


@pytest.fixture
def service(db):
    return PaymentService(db)


@pytest.fixture
def active_user(db):
    user = User(user_id="user_001", username="john_doe", email="john@example.com", is_active=True)
    db.add_user(user)
    return user


@pytest.fixture
def auth_user(active_user):
    # Authenticate using the simulated rule: password == f"{username}_pass"
    assert active_user.authenticate("john_doe_pass") is True
    return active_user


def test_successful_payment_creation(service, auth_user, db):
    # Arrange
    amount = 99.99
    currency = Currency.USD
    description = "Order #123"

    # Act
    payment = service.create_payment(auth_user, amount, currency, description)

    # Assert
    assert payment is not None
    assert payment.payment_id == "pay_user_001_1"
    assert payment.user_id == auth_user.user_id
    assert payment.amount == amount
    assert payment.currency == currency
    assert payment.description == description
    assert payment.status == PaymentStatus.COMPLETED
    assert payment.created_at is not None
    assert payment.completed_at is not None

    # Database should have exactly one payment entry for this user
    assert len(db.payments) == 1
    stored = db.get_payment(payment.payment_id)
    assert stored is payment  # Same object reference stored
    history = db.get_user_payments(auth_user.user_id)
    assert len(history) == 1
    assert history[0] is payment

    # Service history should match
    service_history = service.get_payment_history(auth_user)
    assert len(service_history) == 1
    assert service_history[0] is payment


def test_authentication_requirement(service, active_user, db):
    # Act / Assert
    with pytest.raises(PermissionError, match="User must be authenticated"):
        service.create_payment(active_user, 50.0, Currency.EUR, "Should fail")

    # Database should be unchanged (no payments added)
    assert len(db.payments) == 0
    assert db.get_user_payments(active_user.user_id) == []


def test_database_state_after_payment_creation(service, auth_user, db):
    # Arrange
    amount = 10.50
    currency = Currency.GBP
    description = "Subscription Fee"

    # Act
    payment = service.create_payment(auth_user, amount, currency, description)

    # Assert database state reflects the newly created, completed payment
    assert len(db.payments) == 1
    assert payment.payment_id in db.payments

    stored = db.payments[payment.payment_id]
    assert stored.status == PaymentStatus.COMPLETED
    assert stored.amount == amount
    assert stored.currency == currency
    assert stored.description == description
    assert stored.user_id == auth_user.user_id

    # User's payment list in DB should include this payment
    user_payments = db.get_user_payments(auth_user.user_id)
    assert len(user_payments) == 1
    assert user_payments[0] is stored

Would you like me to also include tests for invalid amounts and inactive users to cover more edge cases?
```

---

### GPT-5 - Few-Shot

**Prompt:**
```
Generate an integration test for the PaymentService.create_payment() method.

Here is an example test from our codebase showing the authentication pattern:

    import pytest
    from payment_system import User, PaymentDatabase, PaymentService

    @pytest.fixture
    def database():
        db = PaymentDatabase()
        yield db
        db.clear()

    @pytest.fixture
    def authenticated_user(database):
        user = User("test_001", "testuser", "test@example.com")
        database.add_user(user)
        user.authenticate("testuser_pass")
        return user

    @pytest.fixture
    def service(database):
        return PaymentService(database)

    def test_user_authentication(authenticated_user):
        assert authenticated_user.is_authenticated() is True
        assert authenticated_user.auth_token is not None

Now generate a test for PaymentService.create_payment() that:
- Uses the same fixture pattern
- Tests successful payment creation with amount=100.00, currency=USD
- Verifies the payment is stored in the database
- Checks the payment status is COMPLETED
```

**LLM Output:**
```python
import pytest
from payment_system import Currency, PaymentStatus

def test_create_payment_success(authenticated_user, service, database):
    payment = service.create_payment(
        user=authenticated_user,
        amount=100.00,
        currency=Currency.USD,
        description="Integration test payment"
    )

    # Payment is created and returned
    assert payment is not None
    assert payment.amount == 100.00
    assert payment.currency == Currency.USD

    # Payment is stored in the database
    stored = database.get_payment(payment.payment_id)
    assert stored is not None
    assert stored.payment_id == payment.payment_id

    # Payment status is COMPLETED
    assert payment.status == PaymentStatus.COMPLETED
    assert stored.status == PaymentStatus.COMPLETED
```

Would you also like tests for failure cases, such as unauthenticated users or invalid amounts?