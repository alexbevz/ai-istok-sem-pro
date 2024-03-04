import bcrypt
import jwt
from datetime import datetime, timedelta

from src.auth.config import JwtConfig


class BcryptUtil:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        encoded_password = password.encode()
        encoded_hash = bcrypt.hashpw(encoded_password, salt)
        decoded_hash = encoded_hash.decode()
        return decoded_hash

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        encoded_password = password.encode()
        encoded_hash = hashed.encode()
        is_valid = bcrypt.checkpw(encoded_password, encoded_hash)
        return is_valid


class JwtUtil:
    secret_key: str = JwtConfig.get_secret_key()
    algorithm: str = JwtConfig.get_algorithm()

    @classmethod
    def generate_token(cls, payload: dict, *, headers: dict | None = None,
                       expiration_minutes: int = JwtConfig.get_expire_minutes()) -> str:
        modified_payload = payload.copy()
        modified_payload['exp'] = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        modified_payload['iat'] = datetime.utcnow()
        token = jwt.encode(modified_payload, cls.secret_key, algorithm=cls.algorithm, headers=headers)
        return token

    @classmethod
    def decode_token(cls, token: str) -> dict | str:
        payload = jwt.decode(token, cls.secret_key, algorithms=[cls.algorithm])
        return payload
        # try:
        #
        # except jwt.ExpiredSignatureError:
        #     return 'Token has expired. Please log in again.'
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'

    @classmethod
    def create_tokens(cls, payload: dict, *, headers: dict | None = None, ttl_access: int = JwtConfig.get_ttl_access(),
                      ttl_refresh: int = JwtConfig.get_ttl_refresh()) -> tuple[str, str]:

        access_token = cls.generate_token(payload, headers=headers, expiration_minutes=ttl_access)
        refresh_token = cls.generate_token(payload, headers=headers, expiration_minutes=ttl_refresh)

        return access_token, refresh_token

