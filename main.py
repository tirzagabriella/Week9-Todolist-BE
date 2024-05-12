from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Annotated, Union
from jose import JWTError, jwt
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

class Token(BaseModel):
    access_token: str
    token_type: str

class SessionData(BaseModel):
    username: str
    token: Token

cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()

models.Base.metadata.create_all(bind=engine)

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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

@app.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    session = uuid4()

    # generate token to save
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": name}, expires_delta=access_token_expires
    )
    token = Token(access_token=access_token, token_type="bearer")

    data = SessionData(username=name, token=token)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"

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
