import bcrypt


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
