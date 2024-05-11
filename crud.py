from sqlalchemy.orm import Session

import models, schemas

# CRUD operations for Todos
def get_todos_by_user(db: Session, user_id: int):
    return db.query(models.Todo).filter(models.Todo.user_id == user_id).all()

def get_todo_by_task(db: Session, task: str):
    return db.query(models.Todo).filter(models.Todo.task == task).first()

def create_todo(db: Session, db_todo: models.Todo):
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: str, todo: schemas.Todo):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo:
        if todo.task is not None:
            db_todo.task = todo.task
        if todo.completed is not None:
            db_todo.completed = todo.completed
        if todo.datetime is not None:
            db_todo.datetime = todo.datetime
        if todo.user_id is not None:
            db_todo.user_id = todo.user_id
        db.commit()
        db.refresh(db_todo)
        return db_todo
    else:
        return None

def delete_todo(db: Session, todo_id: str):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False

# CRUD operations for User
# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "examplehash"  # Example hashing
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password,
#                           display_name=user.display_name, profile_pic=user.profile_pic, is_active=True)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()

# def update_user(db: Session, user_id: int, user: schemas.User):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user:
#         if user.email is not None:
#             db_user.email = user.email
#         if user.display_name is not None:
#             db_user.display_name = user.display_name
#         if user.profile_pic is not None:
#             db_user.profile_pic = user.profile_pic
#         if user.is_active is not None:
#             db_user.is_active = user.is_active
#         db.commit()
#         db.refresh(db_user)
#         return db_user
#     else:
#         return None

# def delete_user(db: Session, user_id: int):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user:
#         db.delete(db_user)
#         db.commit()
#         return True
#     return False
