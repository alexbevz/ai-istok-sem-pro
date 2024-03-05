from src.repository import CrudRepository
from src.auth.model import Role, User


class RoleRepository(CrudRepository, cls_model=Role):
    pass


roleRep = RoleRepository()


class UserRepository(CrudRepository, cls_model=User):
    pass


userRep = UserRepository()
