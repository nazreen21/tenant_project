import secrets

# token generation
def generate_secure_token(length: int = 48) -> str:
    
    return secrets.token_urlsafe(length)
