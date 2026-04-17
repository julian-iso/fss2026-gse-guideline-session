import pytest

from problem_01_test_generation import validate_password


@pytest.mark.parametrize(
    "password",
    [
        "Abcdefg1",  # minimum valid length (8)
        "A1bcdefghijklmnopqrs",  # maximum valid length (20)
        "Z9veryStrongPass",
        "X1Y2Z3A4",
    ],
)
def test_valid_passwords(password):
    assert validate_password(password) is True


@pytest.mark.parametrize(
    "password",
    [
        "Abcdef1",  # length 7
        "A1bcdefghijklmnopqrst",  # length 21
        "",  # empty string
    ],
)
def test_invalid_length(password):
    assert validate_password(password) is False


@pytest.mark.parametrize(
    "password",
    [
        "Abcdefgh",  # no digit
        "ONLYUPPERCASE",  # no digit
        "lowerUPPER",  # no digit
    ],
)
def test_missing_digit(password):
    assert validate_password(password) is False


@pytest.mark.parametrize(
    "password",
    [
        "lowercase1",  # no uppercase
        "12345678",  # digits only, no uppercase
        "allsmall9",  # no uppercase
    ],
)
def test_missing_uppercase(password):
    assert validate_password(password) is False


@pytest.mark.parametrize(
    "password",
    [
        "MyPassword1",  # contains 'password'
        "mypAsSwOrD9",  # mixed-case occurrence
        "PASSWORD123A",  # uppercase occurrence
    ],
)
def test_rejects_password_word_case_insensitive(password):
    assert validate_password(password) is False


def test_rule_priority_still_rejects_when_multiple_issues_present():
    # Contains banned word and is too long.
    assert validate_password("Apassword1234567890123") is False


@pytest.mark.parametrize("value", [None, 12345678])
def test_non_string_input_raises_type_error(value):
    with pytest.raises(TypeError):
        validate_password(value)


def test_non_string_iterable_input_returns_false():
    assert validate_password(["A", "1", "b"]) is False
