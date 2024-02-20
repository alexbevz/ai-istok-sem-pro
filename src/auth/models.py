from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = 'role'

    name: Mapped[str]

    def __repr__(self) -> str:
        return f'Address(id={self.id!r}, name={self.name!r})'


class UserRole(BaseModel):
    __tablename__ = 'user_role'

    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(ForeignKey('role.id', ondelete='CASCADE'), nullable=False, index=True)


class User(BaseModel):
    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(String(32))
    password: Mapped[str]
    email: Mapped[Optional[str]]

    roles: Mapped[List['Role']] = relationship(secondary=UserRole.__tablename__, lazy='joined')

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, username={self.username!r}, email={self.email!r})'

