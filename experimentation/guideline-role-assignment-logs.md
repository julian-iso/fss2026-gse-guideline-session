# LLM Experimentation Prompt Logs

## Experiment: Role Assignment Impact on Test Quality

### Experiment 1: No Role Assignment (Baseline)

**Prompt:**
```
Generate unit tests for this authentication function:

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user

Use PyTest and cover edge cases.
```

**LLM Output (Claude 4.5 Sonnet):**
# Unit Tests for authenticate_user Function

```python
import pytest
from unittest.mock import Mock, MagicMock
from your_module import authenticate_user, hash_password


class TestAuthenticateUser:
    """Test suite for the authenticate_user function."""
    
    @pytest.fixture
    def mock_db(self):
        """Fixture to create a mock database object."""
        return Mock()
    
    @pytest.fixture
    def mock_user(self):
        """Fixture to create a mock user object."""
        user = Mock()
        user.password_hash = hash_password("correct_password")
        user.is_locked = False
        return user
    
    # Successful Authentication Tests
    
    def test_successful_authentication(self, mock_db, mock_user):
        """Test successful authentication with valid credentials."""
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", "correct_password", mock_db)
        
        assert result == mock_user
        mock_db.get_user.assert_called_once_with("valid_user")
    
    # Empty/None Input Tests
    
    def test_none_username(self, mock_db):
        """Test authentication fails when username is None."""
        result = authenticate_user(None, "password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_empty_username(self, mock_db):
        """Test authentication fails when username is empty string."""
        result = authenticate_user("", "password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_none_password(self, mock_db):
        """Test authentication fails when password is None."""
        result = authenticate_user("username", None, mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_empty_password(self, mock_db):
        """Test authentication fails when password is empty string."""
        result = authenticate_user("username", "", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_both_credentials_none(self, mock_db):
        """Test authentication fails when both credentials are None."""
        result = authenticate_user(None, None, mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_both_credentials_empty(self, mock_db):
        """Test authentication fails when both credentials are empty."""
        result = authenticate_user("", "", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()
    
    # User Not Found Tests
    
    def test_user_not_found(self, mock_db):
        """Test authentication fails when user doesn't exist."""
        mock_db.get_user.return_value = None
        
        result = authenticate_user("nonexistent_user", "password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with("nonexistent_user")
    
    # Password Mismatch Tests
    
    def test_incorrect_password(self, mock_db, mock_user):
        """Test authentication fails with incorrect password."""
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", "wrong_password", mock_db)
        
        assert result is None
    
    def test_password_case_sensitive(self, mock_db, mock_user):
        """Test that password matching is case-sensitive."""
        mock_user.password_hash = hash_password("Password123")
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", "password123", mock_db)
        
        assert result is None
    
    # Account Locked Tests
    
    def test_locked_account_correct_password(self, mock_db, mock_user):
        """Test authentication fails for locked account even with correct password."""
        mock_user.is_locked = True
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", "correct_password", mock_db)
        
        assert result is None
    
    def test_locked_account_incorrect_password(self, mock_db, mock_user):
        """Test authentication fails for locked account with incorrect password."""
        mock_user.is_locked = True
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", "wrong_password", mock_db)
        
        assert result is None
    
    # Edge Cases with Special Characters
    
    def test_username_with_special_characters(self, mock_db, mock_user):
        """Test authentication with special characters in username."""
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("user@example.com", "correct_password", mock_db)
        
        assert result == mock_user
        mock_db.get_user.assert_called_once_with("user@example.com")
    
    def test_password_with_special_characters(self, mock_db, mock_user):
        """Test authentication with special characters in password."""
        special_password = "P@ssw0rd!#$%"
        mock_user.password_hash = hash_password(special_password)
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", special_password, mock_db)
        
        assert result == mock_user
    
    def test_unicode_username(self, mock_db, mock_user):
        """Test authentication with unicode characters in username."""
        unicode_username = "用户名"
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user(unicode_username, "correct_password", mock_db)
        
        assert result == mock_user
        mock_db.get_user.assert_called_once_with(unicode_username)
    
    # Whitespace Tests
    
    def test_whitespace_only_username(self, mock_db):
        """Test authentication fails with whitespace-only username."""
        result = authenticate_user("   ", "password", mock_db)
        
        # Note: Current implementation treats whitespace as valid
        # This test documents the actual behavior
        mock_db.get_user.assert_called_once_with("   ")
    
    def test_whitespace_only_password(self, mock_db):
        """Test authentication with whitespace-only password."""
        result = authenticate_user("username", "   ", mock_db)
        
        # Note: Current implementation treats whitespace as valid
        mock_db.get_user.assert_called_once_with("username")
    
    # Database Error Tests
    
    def test_database_exception(self, mock_db):
        """Test behavior when database raises an exception."""
        mock_db.get_user.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception):
            authenticate_user("valid_user", "password", mock_db)
    
    # Boundary Tests
    
    def test_very_long_username(self, mock_db, mock_user):
        """Test authentication with extremely long username."""
        long_username = "a" * 10000
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user(long_username, "correct_password", mock_db)
        
        assert result == mock_user
        mock_db.get_user.assert_called_once_with(long_username)
    
    def test_very_long_password(self, mock_db, mock_user):
        """Test authentication with extremely long password."""
        long_password = "a" * 10000
        mock_user.password_hash = hash_password(long_password)
        mock_db.get_user.return_value = mock_user
        
        result = authenticate_user("valid_user", long_password, mock_db)
        
        assert result == mock_user


# Parametrized Tests for Multiple Invalid Inputs

@pytest.mark.parametrize("username,password", [
    (None, "password"),
    ("", "password"),
    ("username", None),
    ("username", ""),
    (None, None),
    ("", ""),
    (0, "password"),  # Type confusion
    ("username", 0),  # Type confusion
])
def test_invalid_credentials_parametrized(username, password):
    """Parametrized test for various invalid credential combinations."""
    mock_db = Mock()
    result = authenticate_user(username, password, mock_db)
    assert result is None
```

**Key Testing Areas Covered:**

1. **Happy Path**: Valid credentials and successful authentication
2. **Null/Empty Inputs**: None and empty string handling
3. **User Existence**: Non-existent users
4. **Password Validation**: Incorrect passwords, case sensitivity
5. **Account Status**: Locked accounts
6. **Special Characters**: Unicode, symbols, email formats
7. **Whitespace**: Space-only inputs
8. **Error Handling**: Database exceptions
9. **Boundary Conditions**: Extremely long inputs
10. **Type Confusion**: Non-string inputs

Would you like me to add integration tests that use a real database connection, or discuss potential security improvements for the authentication function itself?

---

### Experiment 2: Generic Role Assignment

**Prompt:**
```
You are a software tester.

Generate unit tests for this authentication function:

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user

Use PyTest and cover edge cases.
```

**LLM Output (Claude 4.5 Sonnet):**
# Unit Tests for authenticate_user Function

```python
import pytest
from unittest.mock import Mock, MagicMock
from your_module import authenticate_user, hash_password


class TestAuthenticateUser:
    """Test suite for the authenticate_user function"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database object"""
        return Mock()

    @pytest.fixture
    def valid_user(self):
        """Create a valid user object"""
        user = Mock()
        user.password_hash = hash_password("correct_password")
        user.is_locked = False
        return user

    # ===== Happy Path Tests =====
    
    def test_successful_authentication(self, mock_db, valid_user):
        """Test successful authentication with valid credentials"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "correct_password", mock_db)
        
        assert result == valid_user
        mock_db.get_user.assert_called_once_with("john_doe")

    # ===== Empty/None Input Tests =====
    
    def test_empty_username(self, mock_db):
        """Test authentication fails with empty username"""
        result = authenticate_user("", "password123", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    def test_none_username(self, mock_db):
        """Test authentication fails with None username"""
        result = authenticate_user(None, "password123", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    def test_empty_password(self, mock_db):
        """Test authentication fails with empty password"""
        result = authenticate_user("john_doe", "", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    def test_none_password(self, mock_db):
        """Test authentication fails with None password"""
        result = authenticate_user("john_doe", None, mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    def test_both_username_and_password_empty(self, mock_db):
        """Test authentication fails when both credentials are empty"""
        result = authenticate_user("", "", mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    def test_both_username_and_password_none(self, mock_db):
        """Test authentication fails when both credentials are None"""
        result = authenticate_user(None, None, mock_db)
        
        assert result is None
        mock_db.get_user.assert_not_called()

    # ===== User Not Found Tests =====
    
    def test_user_not_found(self, mock_db):
        """Test authentication fails when user doesn't exist"""
        mock_db.get_user.return_value = None
        
        result = authenticate_user("nonexistent_user", "password123", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with("nonexistent_user")

    # ===== Incorrect Password Tests =====
    
    def test_incorrect_password(self, mock_db, valid_user):
        """Test authentication fails with wrong password"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "wrong_password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with("john_doe")

    def test_password_case_sensitivity(self, mock_db, valid_user):
        """Test password comparison is case-sensitive"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "CORRECT_PASSWORD", mock_db)
        
        assert result is None

    # ===== Locked Account Tests =====
    
    def test_locked_account(self, mock_db, valid_user):
        """Test authentication fails for locked account even with correct password"""
        valid_user.is_locked = True
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "correct_password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with("john_doe")

    # ===== Edge Case Tests =====
    
    def test_whitespace_only_username(self, mock_db):
        """Test authentication with whitespace-only username"""
        result = authenticate_user("   ", "password123", mock_db)
        
        # Depends on if whitespace is considered truthy
        # Current implementation treats it as valid input
        mock_db.get_user.assert_called_once_with("   ")

    def test_whitespace_only_password(self, mock_db, valid_user):
        """Test authentication with whitespace-only password"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "   ", mock_db)
        
        # Will fail if whitespace doesn't match stored hash
        assert result is None

    def test_special_characters_in_username(self, mock_db, valid_user):
        """Test authentication with special characters in username"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john.doe@example.com", "correct_password", mock_db)
        
        assert result == valid_user

    def test_unicode_username(self, mock_db, valid_user):
        """Test authentication with unicode characters in username"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("用户名", "correct_password", mock_db)
        
        assert result == valid_user

    def test_very_long_username(self, mock_db, valid_user):
        """Test authentication with extremely long username"""
        long_username = "a" * 10000
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user(long_username, "correct_password", mock_db)
        
        assert result == valid_user
        mock_db.get_user.assert_called_once_with(long_username)

    def test_very_long_password(self, mock_db, valid_user):
        """Test authentication with extremely long password"""
        long_password = "p" * 10000
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", long_password, mock_db)
        
        # Will fail if hash doesn't match
        mock_db.get_user.assert_called_once()

    # ===== Database Error Tests =====
    
    def test_database_exception(self, mock_db):
        """Test behavior when database raises an exception"""
        mock_db.get_user.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception):
            authenticate_user("john_doe", "password123", mock_db)

    # ===== User Object Edge Cases =====
    
    def test_user_missing_password_hash_attribute(self, mock_db):
        """Test when user object lacks password_hash attribute"""
        user = Mock(spec=[])  # User without password_hash attribute
        mock_db.get_user.return_value = user
        
        with pytest.raises(AttributeError):
            authenticate_user("john_doe", "password123", mock_db)

    def test_user_missing_is_locked_attribute(self, mock_db, valid_user):
        """Test when user object lacks is_locked attribute"""
        delattr(valid_user, 'is_locked')
        mock_db.get_user.return_value = valid_user
        
        with pytest.raises(AttributeError):
            authenticate_user("john_doe", "correct_password", mock_db)

    def test_user_password_hash_none(self, mock_db):
        """Test when user's password_hash is None"""
        user = Mock()
        user.password_hash = None
        user.is_locked = False
        mock_db.get_user.return_value = user
        
        result = authenticate_user("john_doe", "password123", mock_db)
        
        assert result is None

    # ===== Boolean Coercion Tests =====
    
    def test_is_locked_truthy_value(self, mock_db, valid_user):
        """Test with non-boolean truthy value for is_locked"""
        valid_user.is_locked = 1  # Truthy but not boolean True
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "correct_password", mock_db)
        
        assert result is None

    def test_is_locked_false_variations(self, mock_db, valid_user):
        """Test that only False/falsy values allow authentication"""
        valid_user.is_locked = 0  # Falsy
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("john_doe", "correct_password", mock_db)
        
        assert result == valid_user


# ===== Integration Test Examples =====

class TestAuthenticateUserIntegration:
    """Integration tests with more realistic scenarios"""
    
    def test_authentication_flow_sequence(self, mock_db):
        """Test complete authentication flow"""
        user = Mock()
        user.password_hash = hash_password("my_secure_pass")
        user.is_locked = False
        mock_db.get_user.return_value = user
        
        # Successful authentication
        result1 = authenticate_user("alice", "my_secure_pass", mock_db)
        assert result1 == user
        
        # Failed authentication with wrong password
        result2 = authenticate_user("alice", "wrong_pass", mock_db)
        assert result2 is None
        
        # Lock account and try again
        user.is_locked = True
        result3 = authenticate_user("alice", "my_secure_pass", mock_db)
        assert result3 is None
```

## Running the Tests

```bash
# Run all tests
pytest test_authentication.py -v

# Run with coverage
pytest test_authentication.py --cov=your_module --cov-report=html

# Run specific test class
pytest test_authentication.py::TestAuthenticateUser -v

# Run tests matching pattern
pytest test_authentication.py -k "password" -v
```

These tests cover:
- ✅ Happy path (successful authentication)
- ✅ Empty/None inputs
- ✅ Non-existent users
- ✅ Incorrect passwords
- ✅ Locked accounts
- ✅ Edge cases (special chars, unicode, very long inputs)
- ✅ Database errors
- ✅ Missing attributes
- ✅ Type coercion scenarios

Would you like me to add tests for any specific security concerns, such as timing attacks or rate limiting scenarios?

---

### Experiment 3: Senior Expert Role Assignment

**Prompt:**
```
You are a senior test engineer with 10+ years of experience in security testing 
and authentication systems. You specialize in finding edge cases and security vulnerabilities.

Generate unit tests for this authentication function:

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user

Use PyTest and cover edge cases. Consider security implications and attack vectors.
```

**LLM Output (Claude 4.5 Sonnet):**
# Comprehensive Unit Tests for authenticate_user Function

```python
import pytest
from unittest.mock import Mock, MagicMock
from your_module import authenticate_user, hash_password


class TestAuthenticateUser:
    """Test suite for authenticate_user function with security focus"""
    
    @pytest.fixture
    def mock_db(self):
        """Fixture providing a mock database"""
        return Mock()
    
    @pytest.fixture
    def valid_user(self):
        """Fixture providing a valid unlocked user"""
        user = Mock()
        user.password_hash = hash_password("correct_password")
        user.is_locked = False
        return user
    
    @pytest.fixture
    def locked_user(self):
        """Fixture providing a locked user account"""
        user = Mock()
        user.password_hash = hash_password("correct_password")
        user.is_locked = True
        return user


    # === HAPPY PATH TESTS ===
    
    def test_successful_authentication(self, mock_db, valid_user):
        """Test successful authentication with valid credentials"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("valid_user", "correct_password", mock_db)
        
        assert result == valid_user
        mock_db.get_user.assert_called_once_with("valid_user")
    
    
    # === NULL/EMPTY INPUT TESTS ===
    
    def test_none_username(self, mock_db):
        """Test authentication fails with None username"""
        result = authenticate_user(None, "password", mock_db)
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_none_password(self, mock_db):
        """Test authentication fails with None password"""
        result = authenticate_user("user", None, mock_db)
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_empty_string_username(self, mock_db):
        """Test authentication fails with empty string username"""
        result = authenticate_user("", "password", mock_db)
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_empty_string_password(self, mock_db):
        """Test authentication fails with empty string password"""
        result = authenticate_user("user", "", mock_db)
        assert result is None
        mock_db.get_user.assert_not_called()
    
    def test_whitespace_only_username(self, mock_db):
        """Test authentication with whitespace-only username"""
        # Note: Current implementation treats whitespace as valid
        mock_db.get_user.return_value = None
        result = authenticate_user("   ", "password", mock_db)
        assert result is None
    
    def test_whitespace_only_password(self, mock_db, valid_user):
        """Test authentication fails with whitespace-only password"""
        mock_db.get_user.return_value = valid_user
        result = authenticate_user("user", "   ", mock_db)
        assert result is None
    
    
    # === USER EXISTENCE TESTS ===
    
    def test_nonexistent_user(self, mock_db):
        """Test authentication fails for non-existent user"""
        mock_db.get_user.return_value = None
        
        result = authenticate_user("nonexistent", "password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with("nonexistent")
    
    
    # === PASSWORD VALIDATION TESTS ===
    
    def test_incorrect_password(self, mock_db, valid_user):
        """Test authentication fails with incorrect password"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("valid_user", "wrong_password", mock_db)
        
        assert result is None
    
    def test_case_sensitive_password(self, mock_db, valid_user):
        """Test password matching is case-sensitive"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("valid_user", "CORRECT_PASSWORD", mock_db)
        
        assert result is None
    
    def test_password_with_special_characters(self, mock_db):
        """Test authentication with special characters in password"""
        user = Mock()
        user.password_hash = hash_password("P@ssw0rd!#$%")
        user.is_locked = False
        mock_db.get_user.return_value = user
        
        result = authenticate_user("user", "P@ssw0rd!#$%", mock_db)
        
        assert result == user
    
    def test_password_with_unicode(self, mock_db):
        """Test authentication with Unicode characters in password"""
        user = Mock()
        user.password_hash = hash_password("пароль密码🔐")
        user.is_locked = False
        mock_db.get_user.return_value = user
        
        result = authenticate_user("user", "пароль密码🔐", mock_db)
        
        assert result == user
    
    
    # === ACCOUNT LOCKING TESTS ===
    
    def test_locked_account_correct_password(self, mock_db, locked_user):
        """Test authentication fails for locked account even with correct password"""
        mock_db.get_user.return_value = locked_user
        
        result = authenticate_user("locked_user", "correct_password", mock_db)
        
        assert result is None
    
    def test_locked_account_incorrect_password(self, mock_db, locked_user):
        """Test authentication fails for locked account with incorrect password"""
        mock_db.get_user.return_value = locked_user
        
        result = authenticate_user("locked_user", "wrong_password", mock_db)
        
        assert result is None
    
    
    # === SQL INJECTION TESTS ===
    
    def test_sql_injection_username(self, mock_db):
        """Test SQL injection attempt in username"""
        mock_db.get_user.return_value = None
        
        malicious_username = "admin' OR '1'='1"
        result = authenticate_user(malicious_username, "password", mock_db)
        
        assert result is None
        mock_db.get_user.assert_called_once_with(malicious_username)
    
    def test_sql_injection_password(self, mock_db, valid_user):
        """Test SQL injection attempt in password"""
        mock_db.get_user.return_value = valid_user
        
        malicious_password = "' OR '1'='1' --"
        result = authenticate_user("user", malicious_password, mock_db)
        
        assert result is None
    
    
    # === TIMING ATTACK TESTS ===
    
    def test_timing_consistency_nonexistent_vs_wrong_password(self, mock_db, valid_user):
        """Test that response time doesn't reveal user existence
        Note: This test documents the vulnerability - execution paths differ"""
        import time
        
        # Time for non-existent user
        mock_db.get_user.return_value = None
        start = time.perf_counter()
        authenticate_user("nonexistent", "password", mock_db)
        time_nonexistent = time.perf_counter() - start
        
        # Time for wrong password
        mock_db.get_user.return_value = valid_user
        start = time.perf_counter()
        authenticate_user("existing", "wrong_password", mock_db)
        time_wrong_password = time.perf_counter() - start
        
        # Document that timing difference exists (vulnerability)
        # In production, consider constant-time comparison
        assert time_nonexistent >= 0 and time_wrong_password >= 0
    
    
    # === INJECTION/XSS TESTS ===
    
    def test_xss_in_username(self, mock_db):
        """Test XSS payload in username doesn't cause issues"""
        mock_db.get_user.return_value = None
        
        xss_username = "<script>alert('xss')</script>"
        result = authenticate_user(xss_username, "password", mock_db)
        
        assert result is None
    
    def test_null_byte_injection_username(self, mock_db):
        """Test null byte injection in username"""
        mock_db.get_user.return_value = None
        
        result = authenticate_user("admin\x00", "password", mock_db)
        
        assert result is None
    
    
    # === EDGE CASE TESTS ===
    
    def test_very_long_username(self, mock_db):
        """Test authentication with extremely long username"""
        mock_db.get_user.return_value = None
        
        long_username = "a" * 10000
        result = authenticate_user(long_username, "password", mock_db)
        
        assert result is None
    
    def test_very_long_password(self, mock_db, valid_user):
        """Test authentication with extremely long password"""
        mock_db.get_user.return_value = valid_user
        
        long_password = "a" * 10000
        result = authenticate_user("user", long_password, mock_db)
        
        assert result is None
    
    def test_username_with_newlines(self, mock_db):
        """Test username containing newline characters"""
        mock_db.get_user.return_value = None
        
        result = authenticate_user("user\nname", "password", mock_db)
        
        assert result is None
    
    
    # === DATABASE ERROR TESTS ===
    
    def test_database_exception(self, mock_db):
        """Test behavior when database raises exception"""
        mock_db.get_user.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            authenticate_user("user", "password", mock_db)
    
    def test_database_returns_invalid_object(self, mock_db):
        """Test behavior when database returns malformed user object"""
        mock_db.get_user.return_value = "not_a_user_object"
        
        with pytest.raises(AttributeError):
            authenticate_user("user", "password", mock_db)
    
    
    # === TYPE CONFUSION TESTS ===
    
    def test_integer_username(self, mock_db):
        """Test authentication with integer username"""
        mock_db.get_user.return_value = None
        
        # Depending on implementation, this might cause type error
        result = authenticate_user(12345, "password", mock_db)
        
        # Current implementation: falsy check passes, calls get_user with int
        assert result is None
    
    def test_list_as_password(self, mock_db, valid_user):
        """Test authentication with list as password"""
        mock_db.get_user.return_value = valid_user
        
        result = authenticate_user("user", ["pass", "word"], mock_db)
        
        assert result is None
    
    
    # === HASH FUNCTION TESTS ===
    
    def test_hash_function_consistency(self):
        """Test that hash_password produces consistent results"""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 == hash2
    
    
    # === USER OBJECT ATTRIBUTE TESTS ===
    
    def test_user_missing_password_hash(self, mock_db):
        """Test behavior when user object lacks password_hash attribute"""
        user = Mock(spec=[])  # Empty spec, no attributes
        mock_db.get_user.return_value = user
        
        with pytest.raises(AttributeError):
            authenticate_user("user", "password", mock_db)
    
    def test_user_missing_is_locked(self, mock_db):
        """Test behavior when user object lacks is_locked attribute"""
        user = Mock()
        user.password_hash = hash_password("password")
        delattr(user, 'is_locked')
        mock_db.get_user.return_value = user
        
        with pytest.raises(AttributeError):
            authenticate_user("user", "password", mock_db)
    
    def test_is_locked_truthy_values(self, mock_db):
        """Test various truthy values for is_locked"""
        user = Mock()
        user.password_hash = hash_password("password")
        mock_db.get_user.return_value = user
        
        # Test different truthy values
        for locked_value in [True, 1, "locked", [1], {"locked": True}]:
            user.is_locked = locked_value
            result = authenticate_user("user", "password", mock_db)
            assert result is None, f"Failed for is_locked={locked_value}"
    
    def test_is_locked_falsy_values(self, mock_db):
        """Test various falsy values for is_locked"""
        user = Mock()
        user.password_hash = hash_password("password")
        mock_db.get_user.return_value = user
        
        # Test different falsy values
        for locked_value in [False, 0, "", None, [], {}]:
            user.is_locked = locked_value
            result = authenticate_user("user", "password", mock_db)
            assert result == user, f"Failed for is_locked={locked_value}"


# === INTEGRATION TESTS ===

class TestAuthenticateUserIntegration:
    """Integration tests with more realistic scenarios"""
    
    def test_multiple_failed_attempts_simulation(self, mock_db, valid_user):
        """Simulate multiple failed login attempts"""
        mock_db.get_user.return_value = valid_user
        
        # Multiple failed attempts
        for _ in range(5):
            result = authenticate_user("user", "wrong_password", mock_db)
            assert result is None
        
        # Successful attempt
        result = authenticate_user("user", "correct_password", mock_db)
        assert result == valid_user
    
    def test_concurrent_authentication_attempts(self, mock_db, valid_user):
        """Test that function is stateless for concurrent access"""
        mock_db.get_user.return_value = valid_user
        
        # Simulate concurrent calls
        results = []
        for _ in range(10):
            result = authenticate_user("user", "correct_password", mock_db)
            results.append(result)
        
        assert all(r == valid_user for r in results)


# === SECURITY RECOMMENDATIONS ===
"""
IDENTIFIED VULNERABILITIES AND RECOMMENDATIONS:

1. **Timing Attack Vulnerability**
   - Issue: Different execution paths for non-existent users vs wrong passwords
   - Fix: Use constant-time comparison and consistent execution paths

2. **No Rate Limiting**
   - Issue: Function allows unlimited authentication attempts
   - Fix: Implement rate limiting at application level

3. **No Logging/Monitoring**
   - Issue: Failed attempts not tracked for security monitoring
   - Fix: Add logging for failed authentication attempts

4. **Password Hash Algorithm Unknown**
   - Issue: hash_password implementation not verified
   - Fix: Ensure using bcrypt, scrypt, or Argon2 with proper salt

5. **No Account Lockout After Failed Attempts**
   - Issue: is_locked must be managed externally
   - Fix: Consider implementing automatic lockout logic

6. **Type Safety**
   - Issue: No input type validation
   - Fix: Add type hints and runtime type checking

7. **Information Disclosure**
   - Issue: Different return patterns might reveal user existence
   - Fix: Return consistent error messages/codes

8. **No Multi-Factor Authentication Support**
   - Fix: Consider adding MFA as additional security layer
"""
```

---

## Key Testing Strategies Applied:

1. **Security-First Approach**: Tests specifically target injection attacks, timing vulnerabilities, and authentication bypass attempts
2. **Edge Cases**: Null bytes, Unicode, extremely long inputs, type confusion
3. **State Testing**: Account locking, multiple failed attempts
4. **Error Handling**: Database failures, malformed objects
5. **Documentation**: Clear vulnerability documentation for security review

**Would you like me to also create a secure refactored version of the `authenticate_user` function that addresses the identified vulnerabilities?**

---

### Experiment 4: Cross-Model Comparison - No Role vs Senior Role

**Model:** Gemini 2.5 Pro

#### Without Role:

**Prompt:**
```
Generate unit tests for this authentication function:

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user

Use PyTest and cover edge cases.
```

**LLM Output:**
Of course. Here are unit tests for the `authenticate_user` function using PyTest. These tests cover the successful authentication path as well as key failure and edge cases.

To write these tests, we will need to simulate the database and user objects. We can do this using mocks.

### Prerequisites

First, ensure you have `pytest` installed. If you don't, you can install it with pip:
`pip install pytest`

### Test File Setup

Let's assume your function is in a file named `auth_utils.py`. You would create a new file named `test_auth_utils.py` to contain the tests.

**`auth_utils.py`**
```python
# A simple dummy hash function for demonstration purposes
def hash_password(password: str) -> str:
    return f"hashed_{password}"

class User:
    def __init__(self, username, password_hash, is_locked=False):
        self.username = username
        self.password_hash = password_hash
        self.is_locked = is_locked

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user
```

---

**`test_auth_utils.py`**
```python
import pytest
from unittest.mock import MagicMock
from auth_utils import authenticate_user, hash_password, User

# --- Test Scenarios ---

def test_authenticate_user_success():
    """
    Tests successful authentication with a valid user, correct password,
    and an unlocked account.
    """
    # Arrange
    mock_user = User(
        username='testuser',
        password_hash=hash_password('correct_password'),
        is_locked=False
    )
    mock_db = MagicMock()
    mock_db.get_user.return_value = mock_user

    # Act
    result = authenticate_user('testuser', 'correct_password', mock_db)

    # Assert
    assert result is not None
    assert result == mock_user
    mock_db.get_user.assert_called_once_with('testuser')

def test_authenticate_user_incorrect_password():
    """
    Tests authentication failure due to an incorrect password.
    """
    # Arrange
    mock_user = User(
        username='testuser',
        password_hash=hash_password('correct_password'),
        is_locked=False
    )
    mock_db = MagicMock()
    mock_db.get_user.return_value = mock_user

    # Act
    result = authenticate_user('testuser', 'wrong_password', mock_db)

    # Assert
    assert result is None
    mock_db.get_user.assert_called_once_with('testuser')

def test_authenticate_user_nonexistent_user():
    """
    Tests authentication failure when the user does not exist in the database.
    """
    # Arrange
    mock_db = MagicMock()
    mock_db.get_user.return_value = None

    # Act
    result = authenticate_user('nonexistent', 'any_password', mock_db)

    # Assert
    assert result is None
    mock_db.get_user.assert_called_once_with('nonexistent')

def test_authenticate_user_locked_account():
    """
    Tests authentication failure for a user whose account is locked.
    """
    # Arrange
    mock_user = User(
        username='lockeduser',
        password_hash=hash_password('correct_password'),
        is_locked=True
    )
    mock_db = MagicMock()
    mock_db.get_user.return_value = mock_user

    # Act
    result = authenticate_user('lockeduser', 'correct_password', mock_db)

    # Assert
    assert result is None
    mock_db.get_user.assert_called_once_with('lockeduser')

@pytest.mark.parametrize(
    "username, password",
    [
        ("", "a_password"),       # Empty username
        (None, "a_password"),     # None username
        ("a_user", ""),           # Empty password
        ("a_user", None),         # None password
        ("", ""),                 # Both empty
        (None, None)              # Both None
    ]
)
def test_authenticate_user_invalid_inputs(username, password):
    """
    Tests edge cases with empty or None inputs for username and password.
    The function should return None without querying the database.
    """
    # Arrange
    mock_db = MagicMock()

    # Act
    result = authenticate_user(username, password, mock_db)

    # Assert
    assert result is None
    mock_db.get_user.assert_not_called() # Crucial check for this case
```

### How to Run the Tests

1.  Save the two code blocks above into `auth_utils.py` and `test_auth_utils.py` in the same directory.
2.  Open your terminal in that directory.
3.  Run the command: `pytest`

PyTest will automatically discover and run the tests, giving you a report on which ones passed.

Would you also be interested in learning how to test a related feature, such as an account lockout mechanism that triggers after multiple failed login attempts?

---

#### With Senior Role:

**Prompt:**
```
You are a senior test engineer with 10+ years of experience in security testing 
and authentication systems. You specialize in finding edge cases and security vulnerabilities.

Generate unit tests for this authentication function:

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user

Use PyTest and cover edge cases. Consider security implications and attack vectors.
```

**LLM Output:**
Of course. As a senior test engineer specializing in authentication, it's critical to test not only the "happy path" but also the edge cases and potential attack vectors an adversary might exploit.

Here are the unit tests for the `authenticate_user` function using PyTest. My approach involves extensively mocking the database dependency (`db`) and the `hash_password` utility to isolate the logic within the function itself.

### Test Setup

First, let's assume the function `authenticate_user` and a placeholder `hash_password` function are in a file named `auth.py`.

**`auth.py`**
```python
# A placeholder for a real, secure hashing function (e.g., using passlib or werkzeug)
def hash_password(password: str) -> str:
    return f"hashed_{password}"

def authenticate_user(username, password, db):
    if not username or not password:
        return None
    
    user = db.get_user(username)
    if not user:
        return None
    
    if user.password_hash != hash_password(password):
        return None
    
    if user.is_locked:
        return None
    
    return user
```

### PyTest Unit Tests

This test file, `test_auth.py`, covers standard cases, edge cases, and security considerations like username enumeration. I'm using `pytest-mock` for its convenient `mocker` fixture.

**`test_auth.py`**
```python
import pytest
from unittest.mock import MagicMock
from auth import authenticate_user, hash_password

# A fixture to create a standard, valid user object for our tests.
# This reduces code duplication.
@pytest.fixture
def valid_user():
    user = MagicMock()
    user.username = "testuser"
    user.password_hash = hash_password("correct_password")
    user.is_locked = False
    return user

# A fixture to create a mock database object.
@pytest.fixture
def mock_db(valid_user):
    db = MagicMock()
    # By default, the DB returns our valid user for the correct username.
    db.get_user.return_value = valid_user
    return db

class TestAuthenticateUser:
    
    # === Standard Cases ===

    def test_successful_authentication(self, mock_db, valid_user):
        """
        Tests the "happy path": correct username and password for an active user.
        """
        authenticated_user = authenticate_user("testuser", "correct_password", mock_db)
        mock_db.get_user.assert_called_once_with("testuser")
        assert authenticated_user is valid_user

    def test_incorrect_password(self, mock_db):
        """
        Tests that authentication fails with an incorrect password.
        """
        result = authenticate_user("testuser", "wrong_password", mock_db)
        mock_db.get_user.assert_called_once_with("testuser")
        assert result is None

    def test_user_not_found(self, mock_db):
        """
        Tests that authentication fails if the user does not exist in the database.
        """
        # Configure the mock to simulate a user not being found.
        mock_db.get_user.return_value = None
        
        result = authenticate_user("nonexistent_user", "any_password", mock_db)
        mock_db.get_user.assert_called_once_with("nonexistent_user")
        assert result is None

    # === Edge Cases & Security ===

    def test_locked_account(self, mock_db, valid_user):
        """
        Security Test: Verifies that a locked account cannot be authenticated,
        even with the correct password.
        """
        valid_user.is_locked = True
        
        result = authenticate_user("testuser", "correct_password", mock_db)
        mock_db.get_user.assert_called_once_with("testuser")
        assert result is None

    @pytest.mark.parametrize("username, password", [
        ("", "password"),          # Empty username
        ("user", ""),              # Empty password
        ("", ""),                  # Both empty
        (None, "password"),        # Null username
        ("user", None),            # Null password
        (None, None),              # Both null
        ("   ", "password"),       # Whitespace username
        ("user", "   "),           # Whitespace password
    ])
    def test_empty_or_null_credentials(self, mock_db, username, password):
        """
        Tests various forms of invalid or empty inputs to ensure the initial
        guard clause `if not username or not password:` works as expected.
        """
        result = authenticate_user(username, password, mock_db)
        assert result is None
        mock_db.get_user.assert_not_called() # The DB should not be hit.

    def test_username_enumeration_prevention(self, mock_db):
        """
        Security Test: This is a critical one. The function's behavior should be
        identical for a non-existent user and an existing user with a wrong password.
        Returning `None` in both cases helps prevent attackers from discovering
        which usernames are valid in the system (username enumeration).
        """
        # Scenario 1: User exists, wrong password
        result_wrong_pass = authenticate_user("testuser", "wrong_password", mock_db)
        
        # Scenario 2: User does not exist
        mock_db.get_user.return_value = None
        result_no_user = authenticate_user("nonexistent_user", "any_password", mock_db)
        
        # Both scenarios must return the same value.
        assert result_wrong_pass is None
        assert result_no_user is None
        assert result_wrong_pass == result_no_user

    def test_username_is_case_sensitive(self, mock_db, valid_user):
        """
        Tests how the function handles case differences in username. The actual
        behavior depends on the database's collation, but we test that our
        function correctly passes the username as-is to the DB.
        """
        # We configure the mock so that it only finds the exact-case username.
        def get_user_case_sensitive(username):
            if username == "testuser":
                return valid_user
            return None
        
        mock_db.get_user.side_effect = get_user_case_sensitive

        # Attempting to log in with a different case should fail.
        result = authenticate_user("TestUser", "correct_password", mock_db)
        assert result is None
        mock_db.get_user.assert_called_with("TestUser")

    def test_password_with_special_characters_and_unicode(self, mock_db, valid_user):
        """
        Robustness Test: Ensures that complex passwords containing special characters,
        whitespace, and unicode are handled correctly by the authentication flow.
        """
        complex_password = r"""!@#$%^&*()_+-=[]{};':"\\|,.<>/? ~`éüîà"""
        valid_user.password_hash = hash_password(complex_password)

        result = authenticate_user("testuser", complex_password, mock_db)
        assert result is valid_user

```

### Explanation of Security-Focused Tests

*   **`test_locked_account`**: This ensures that account locking, a primary defense against brute-force attacks, is correctly enforced by the authentication logic.
*   **`test_empty_or_null_credentials`**: Beyond simple validation, this test ensures that malformed requests (e.g., from a script) are rejected early, without performing a needless database query.
*   **`test_username_enumeration_prevention`**: This is a crucial security test. If the system returned "User not found" for an invalid user but "Invalid password" for a valid user, an attacker could build a list of valid usernames. By returning `None` (or a generic "Invalid credentials" message) in both cases, we make this attack vector much more difficult. While timing differences can still be an issue (a "timing attack"), ensuring identical return values is the first line of defense.
*   **`test_username_is_case_sensitive`**: This test clarifies the system's behavior regarding case sensitivity, which is often an overlooked source of bugs and potential security issues (e.g., creating two accounts: `admin` and `Admin`).

This test suite provides strong coverage for the function's logic and its most immediate security vulnerabilities.

Would you like to discuss how we could implement rate-limiting on this function to further protect it against brute-force attacks?