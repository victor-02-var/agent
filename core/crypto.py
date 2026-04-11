import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class SentinelVault:
    def __init__(self):
        # Load the key from .env
        self.key = os.getenv("SENTINEL_MASTER_KEY").encode()
        self.cipher = Fernet(self.key)

    def encrypt_data(self, plain_text: str) -> str:
        """Converts JSON string into an encrypted AES-256 token"""
        if not plain_text: return ""
        encrypted_bytes = self.cipher.encrypt(plain_text.encode())
        return encrypted_bytes.decode()

    def decrypt_data(self, encrypted_token: str) -> str:
        """Converts encrypted token back into readable JSON string"""
        if not encrypted_token: return ""
        decrypted_bytes = self.cipher.decrypt(encrypted_token.encode())
        return decrypted_bytes.decode()