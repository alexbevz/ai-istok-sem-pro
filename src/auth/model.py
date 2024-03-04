from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from src.model.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = 'user_role'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)


class Role(BaseModel):
    __tablename__ = 'role'

    name = Column(String())

    def __repr__(self) -> str:
        return f'Role(id={self.id!r}, name={self.name!r})'


class User(BaseModel):
    __tablename__ = 'user'

    username = Column(String(32), unique=True)
    password = Column(String())
    email = Column(String(32), nullable=True, unique=True)

    roles = relationship(Role, secondary=UserRole.__tablename__, lazy='joined', )

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, username={self.username!r}, email={self.email!r})'
