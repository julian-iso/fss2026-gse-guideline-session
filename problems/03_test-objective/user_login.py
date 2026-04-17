class UserLogin:
    def __init__(self, username, password):
        self.username = username
        if self.validate_password(password):
            self.password = password
        else:
            raise ValueError("Password does not meet requirements.")

    def validate_password(self, password):
        if not (8 <= len(password) <= 20):
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if "password" in password.lower():
            return False
        return True

    def login(self, input_password):
        cleaned_input = input_password.strip()
        
        if cleaned_input == self.password:
            return "✅ Login Successful!"
        else:
            return "❌ Login Failed!"