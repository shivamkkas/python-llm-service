# pkg/util/crypto.py

from cryptography.fernet import Fernet

class CryptoManager:
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())

    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode()