import hashlib
import secrets

def md5(data):
    return hashlib.md5(str(data).encode()).hexdigest()

def hex_token(length: int):
    return secrets.token_hex(length)
