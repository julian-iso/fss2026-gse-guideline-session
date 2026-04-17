def validate_password(password):
# """
# Validates a password based on:
# 1. Length between 8 and 20 characters.
# 2. Must contain at least one digit.
# 3. Must contain at least one uppercase letter.
# 4. Cannot contain the word 'password' (case-insensitive).
# """
    if not (8 <= len(password) <= 20):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if "password" in password.lower():
        return False
    return True