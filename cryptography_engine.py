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

class Crypto:
    """class with content coding methods using password and salt"""
    def __init__(self, passwd : str, pys_salt : bytes) -> None:
        self.password = passwd.encode('utf-8')
        self.salt = pys_salt or b''
        self._kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=390000
        )
        self.key = self.get_key()

    def get_key(self):
        """public method to get key"""
        return base64.urlsafe_b64encode(self._kdf.derive(self.password))

    def encrypt(self, content : bytes):
        """encrypt method"""

        fernet = Fernet(self.key)
        return fernet.encrypt(content)

    def decrypt(self, content : bytes):
        """decrypt method"""

        try:
            fernet = Fernet(self.key)
            return fernet.decrypt(content)
        except InvalidToken as err:
            print(err)
            raise TokenError('access denied') from err
