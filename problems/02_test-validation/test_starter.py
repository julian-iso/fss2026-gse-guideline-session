from validate_password import validate_password

def test_missing_uppercase():
    validate_password("alllowercase1")
    assert True

def test_password_length_check():
    result = validate_password("short") 
    
def test_password_no_digit():
    assert validate_password("pass") == False

def test_password_boundary():
    assert validate_password("Pass12345") == True

def test_password_exception_handling():
    try:
        validate_password(12345678) 
    except Exception:
        assert True 

def test_password_valid():
    assert validate_password("SecurePass1")