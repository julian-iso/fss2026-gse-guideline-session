# LLM Experimentation Prompt Logs

### Experiment 1: Generic Prompt (Without Framework Specification)

**Prompt:**
```
Generate unit tests for this password validation function:

def validate_password(password):
    if not (8 <= len(password) <= 20):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True
```

**LLM Output (Gemini 3):**
To thoroughly test the `validate_password` function, we need to cover the three primary requirements: **length** (8–20 characters), inclusion of at least one **digit**, and inclusion of at least one **uppercase letter**.

Below are the unit tests using Python’s built-in `unittest` framework.

---

### Unit Test Suite

```python
import unittest

# Assuming the function is in the same file or imported
def validate_password(password):
    if not (8 <= len(password) <= 20):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True

class TestPasswordValidation(unittest.TestCase):

    # --- Success Cases ---
    def test_valid_password(self):
        """Should return True for a password meeting all criteria."""
        self.assertTrue(validate_password("Valid123"))
        self.assertTrue(password_is_at_limit := validate_password("A1" + "b" * 18)) # 20 chars

    # --- Length Cases ---
    def test_password_too_short(self):
        """Should return False if length is less than 8."""
        self.assertFalse(validate_password("V1alt")) # 5 chars

    def test_password_too_long(self):
        """Should return False if length is greater than 20."""
        self.assertFalse(validate_password("A1" + "b" * 19)) # 21 chars

    # --- Character Requirement Cases ---
    def test_missing_digit(self):
        """Should return False if there are no numbers."""
        self.assertFalse(validate_password("NoDigitsHere"))

    def test_missing_uppercase(self):
        """Should return False if there are no uppercase letters."""
        self.assertFalse(validate_password("alllowercase123"))

    def test_empty_string(self):
        """Should return False for an empty string."""
        self.assertFalse(validate_password(""))

if __name__ == "__main__":
    unittest.main()
```

---

### Test Coverage Summary

| Test Category | Input Example | Expected | Reason |
| :--- | :--- | :--- | :--- |
| **Valid** | `"Valid123"` | `True` | Meets length, digit, and casing rules. |
| **Boundary (Min)** | `"Abcdefg1"` | `True` | Exactly 8 characters. |
| **Boundary (Max)** | `"A1bcdefghij0klmnopqr"` | `True` | Exactly 20 characters. |
| **Length Fail** | `"Short1"` | `False` | Less than 8 characters. |
| **Digit Fail** | `"NoNumbers"` | `False` | No numeric characters present. |
| **Casing Fail** | `"lowercaseno1"` | `False` | No uppercase characters present. |

---

### Experiment 2: Framework-Pinned Prompt

**Prompt:**
```
Write a PyTest suite for this function utilizing `pytest.mark.parametrize` 
and strictly use standard Python `assert` statements.

def validate_password(password):
    if not (8 <= len(password) <= 20):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True
```

**LLM Output (Gemini 3):**
Testing your `validate_password` function requires checking three main constraints: **length**, **numerical presence**, and **capitalization**. Using `pytest.mark.parametrize` allows us to run multiple test cases through the same logic efficiently while keeping the code clean.

Here is the PyTest suite written in English, as requested.

```python
import pytest

# The function to be tested
def validate_password(password):
    if not (8 <= len(password) <= 20):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True

@pytest.mark.parametrize("password, expected_result", [
    # Valid passwords
    ("ValidPass1", True),
    ("LongerValidPass2026", True),
    ("Exact8Ch1", True),
    ("TwentyCharsLongPass1", True),
    
    # Invalid: Too short (< 8 characters)
    ("Short1A", False),
    ("", False),
    
    # Invalid: Too long (> 20 characters)
    ("ThisPasswordIsWayTooLongForThisSystem1", False),
    
    # Invalid: Missing digit
    ("NoDigitsHere", False),
    ("ALLCAPSNODIGITS", False),
    
    # Invalid: Missing uppercase letter
    ("lowercase123", False),
    ("all_lower_case_1", False),
    
    # Invalid: Missing both digit and uppercase
    ("onlylower", False)
])
def test_validate_password(password, expected_result):
    """
    Tests the validate_password function with various inputs to ensure 
    length, digit, and uppercase constraints are enforced.
    """
    assert validate_password(password) == expected_result
```

### Key Components of the Suite

* **`@pytest.mark.parametrize`**: This decorator maps the `password` and `expected_result` arguments to the list of tuples provided. Each tuple represents a unique test case.
* **Edge Case Testing**: The suite includes boundary checks for length (8 and 20 characters) to ensure the range logic is inclusive.
* **Standard Assertions**: As requested, it uses the standard Python `assert` statement, which PyTest "rewrites" behind the scenes to provide detailed failure messages if a test case does not match the expected boolean outcome.

---

### How to Run
To execute these tests, ensure you have `pytest` installed and run the following command in your terminal:

```bash
pytest name_of_your_file.py
```