from pydantic import BaseModel

class UserCreate(BaseModel):
    user_name: str
    name: str
    password: str

class UserOut(BaseModel):
    user_name: str
    name: str 

class UpdateNameInput(BaseModel):
    new_name: str

class PostCreate(BaseModel):
    text: str

class PostOut(BaseModel):
    id: int
    text: str
    user_id: int

class CommentCreate(BaseModel):
    text: str

class CommentOut(BaseModel):
    id: int
    text: str
    post_id: int
    user_id: int

class UserPosts(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True

class CommentUser(BaseModel):
    id: int
    user_name: str
    name: str

    class Config:
        orm_mode = True

class PostComments(BaseModel):
    id: int
    text: str
    user: CommentUser # This mean use comment.user attribute

    class Config:
        orm_mode = True

class LoginInput(BaseModel):
    user_name: str
    password: str