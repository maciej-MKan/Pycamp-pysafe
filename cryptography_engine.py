import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class TokenError(InvalidToken):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class KeyMaker:
    def __init__(self, salt) -> None:
        self._kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000
        )

    def get_key(self, password : bytes):
        return base64.urlsafe_b64encode(self._kdf.derive(password))

class Encrypter:
    def __init__(self, password : str, salt : bytes = None) -> None:
        self.password = password.encode('utf-8')
        self.salt = salt or b''

    def encrypt(self, content : bytes):
        fernet = Fernet(KeyMaker(self.salt).get_key(self.password))
        return fernet.encrypt(content)

class Decrypter:
    def __init__(self, password : str, salt = None) -> None:
        self.password = password.encode('utf-8')
        self.salt = salt or b''

    def decrypt(self, content : bytes):
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