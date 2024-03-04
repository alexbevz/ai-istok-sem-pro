
import jwt
import datetime

class JWTGenerator:
    def __init__(self, secret_key: str, algorithm: str='HS256') -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, payload: dict,
                       *,
                       headers: dict|None=None,
                       expiration_minutes: int=5) -> str:
        
        modified_payload = payload.copy()
        modified_payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)
        modified_payload['iat'] = datetime.datetime.utcnow()
        token = jwt.encode(modified_payload, self.secret_key, algorithm=self.algorithm, headers=headers)
        return token

    def decode_token(self, token: str) -> dict|str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return 'Token has expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def create_tokens(self, payload: dict,
                      *,
                      headers: dict|None=None,
                      ttl_access: int=5,
                      ttl_refresh: int=60 * 24 * 7) -> tuple[str, str]:
        
        access_token = self.generate_token(payload,
                                           headers=headers,
                                           expiration_minutes=ttl_access)

        refresh_token = self.generate_token(payload,
                                            headers=headers,
                                            expiration_minutes=ttl_refresh)

        return access_token, refresh_token