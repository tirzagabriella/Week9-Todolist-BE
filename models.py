from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     display_name = Column(String, index=True)
#     profile_pic = Column(String)  # URL or path to image
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     todos = relationship("Todo", back_populates="user")

class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, index=True)
    task = Column(String, index=True)
    completed = Column(Boolean, default=False)
    datetime = Column(String)
    user_id = Column(String)

    # user = relationship("User", back_populates="todos")
