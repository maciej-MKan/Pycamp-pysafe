"""Module with cryptography methods

    Raises:
        TokenError: exception when password or salt are invalid

    Returns:
        str: content after cryptographic processing
    """
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class TokenError(InvalidToken):
    """Exception when decrypt is impossible
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class KeyMaker:
    """a class that creates a key from a password and salt"""
    def __init__(self, salt) -> None:
        self._kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000
        )

    def get_key(self, password : bytes):
        """public method to get key"""
        return base64.urlsafe_b64encode(self._kdf.derive(password))

class Encrypter:
    """class to encrypt processing"""
    def __init__(self, password : str, salt : bytes = None) -> None:
        self.password = password.encode('utf-8')
        self.salt = salt or b''

    def encrypt(self, content : bytes):
        """encrypt method"""
        fernet = Fernet(KeyMaker(self.salt).get_key(self.password))
        return fernet.encrypt(content)

class Decrypter:
    """class to decrypt processing"""
    def __init__(self, password : str, salt = None) -> None:
        self.password = password.encode('utf-8')
        self.salt = salt or b''

    def decrypt(self, content : bytes):
        """decrypt method"""
        try:
            fernet = Fernet(KeyMaker(self.salt).get_key(self.password))
            return fernet.decrypt(content)
        except InvalidToken:
            raise TokenError('access denied')

if __name__ == '__main__':
    msg = b'test mssage'
    password = 'default'
    salt = b'test salt'

    print(msg)
    safe_text = Encrypter(password, salt).encrypt(msg)
    print(safe_text)
    print(Decrypter('default', salt).decrypt(safe_text))