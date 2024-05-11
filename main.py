from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# to handle cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# to test api activity
@app.get("/", response_model=schemas.Message)
def welcome_message():
    return {"message": "Welcome to a todolist example of FastAPI!"}

# Todos endpoints
@app.get("/todos/all/{user_id}", response_model=list[schemas.Todo])
def read_todos_by_user(user_id: str, db: Session = Depends(get_db)):
    return crud.get_todos_by_user(db, user_id=user_id)

@app.get("/todos/{task}", response_model=schemas.Todo)
def read_todo_by_task(task: str, db: Session = Depends(get_db)):
    return crud.get_todo_by_task(db, task=task)

@app.post("/todos/create", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    newTodo: models.Todo = models.Todo(
        id=todo.id,
        task=todo.task,
        completed=False,
        datetime=todo.datetime,
        user_id=todo.user_id
    )
    
    return crud.create_todo(db, newTodo)

@app.put("/todos/edit/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: str, todo: schemas.Todo, db: Session = Depends(get_db)):
    return crud.update_todo(db, todo_id, todo)

@app.delete("/todos/delete/{todo_id}", response_model=schemas.Message)
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    success = crud.delete_todo(db, todo_id)
    if success:
        return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")

# User endpoints
# @app.post("/users/create", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     return crud.create_user(db, user)

# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     return crud.get_user(db, user_id)

# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_users(db, skip=skip, limit=limit)

# @app.put("/users/edit/{user_id}", response_model=schemas.User)
# def update_user(user_id: int, user: schemas.User, db: Session = Depends(get_db)):
#     return crud.update_user(db, user_id, user)

# @app.delete("/users/delete/{user_id}", response_model=schemas.Message)
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     success = crud.delete_user(db, user_id)
#     if success:
#         return {"message": "User deleted successfully"}
#     raise HTTPException(status_code=404, detail="User not found")
