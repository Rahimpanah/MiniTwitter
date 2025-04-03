from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from twitter_database import get_db
from schemas import UserCreate, UserOut, UpdateNameInput, PostCreate, PostOut, CommentCreate, CommentOut, UserPosts, PostComments, LoginInput
from twitter_database import User, Post
from dotenv import load_dotenv
import crud
import os
import jwt
import datetime
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
from passlib.context import CryptContext
import json
from cache import get_cachesd_data,set_cashed_data
app = FastAPI()

load_dotenv(".env")
SECRET_KEY=os.environ.get("MySecretKey")
ALGORITHM=os.environ.get("algorithm")

#Create JWT token
def create_jwt_token(user_name: str):
    expiration_time=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload={
        "sub" : user_name,
        "exp" : expiration_time
    }
    token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # print("Generated toke:",token)
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_name = payload.get("sub")
        if user_name is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_name
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user=db.query(User).filter(User.user_name == user.user_name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username is already exist!")
    new_user=crud.create_user(db, user.user_name, user.name, user.password)
    token=create_jwt_token(new_user.user_name)
    response_data = {
        "user_name": new_user.user_name,
        "name": new_user.name,
        "token": token
    }
    print("Final response:",response_data)
    return JSONResponse(content=response_data)

@app.put("/users/", response_model=UserOut)
def update_name(update: UpdateNameInput, 
                db: Session = Depends(get_db), 
                user_name: str = Depends(get_current_user)):
    user=crud.update_name(db, user_name, update.new_name)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return{
        "user_name" : user.user_name,
        "name" : user.name
    }

@app.post("/posts/", response_model=PostOut)
def create_post(post: PostCreate,
                db: Session = Depends(get_db),
                user_name: str= Depends(get_current_user)):
    user=db.query(User).filter(User.user_name==user_name).first()
    new_post=crud.create_post(db, user_id=user.id, text=post.text)
    return new_post

@app.put("/posts/{post_id}", response_model=PostOut)
def update_post(post_id: int, post: PostCreate,
                db: Session = Depends(get_db),
                user_name: str= Depends(get_current_user)):
    existing_post=db.query(Post).filter(Post.id==post_id).first()
    user=db.query(User).filter(User.user_name==user_name).first()
    if not existing_post or existing_post.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post")
    return crud.update_post(db, post_id=post_id, new_text=post.text)

@app.delete("/posts/{post_id}")
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                user_name: str = Depends(get_current_user)):
    existing_post=db.query(Post).filter(Post.id==post_id).first()
    user=db.query(User).filter(User.user_name==user_name).first()
    if not existing_post or existing_post.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
    crud.delete_post(db, post_id=post_id)
    return {"message": "Post deleted successfully"}

@app.post("/comments/{post_id}", response_model=CommentOut)
def create_comment(post_id: int, comment: CommentCreate,
                   db: Session = Depends(get_db),
                   user_name: str = Depends(get_current_user)):
    user=db.query(User).filter(User.user_name==user_name).first()
    post = db.query(Post).filter(Post.id==post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment=crud.create_comment(db, text= comment.text, post_id=post_id, user_id=user.id)
    return new_comment

# Retrieve posts of a user
@app.get("/posts/{user_name}", response_model=List[UserPosts])
def retrieve_user_posts(user_name: str,
                        db: Session = Depends(get_db),
                        Current_user: str = Depends(get_current_user)):
    cache_key = user_name
    print(cache_key)
    cached = get_cachesd_data(cache_key)
    if cached:
        print("Returning cached data!")
        return json.loads(cached)
    user= db.query(User).filter(User.user_name==user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    posts_data = []
    for p in user.posts:
        posts_data.append({"id": p.id, "text": p.text})
    set_cashed_data(cache_key, posts_data)
    print("Cashed new data")
    return posts_data

# Retrieve comments of a post
@app.get("/comments/{post_id}", response_model=List[PostComments])
def retrieve_post_comments(post_id: int,
                           db: Session = Depends(get_db),
                           Current_user: str = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.comments

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
@app.post("/login/")
def login(login_data: LoginInput, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.user_name==login_data.user_name).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user name")
    if not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException (status_code=401, detail="Invalid password")
    token = create_jwt_token(user.user_name)
    return {"access_token": token, "token_type": "bearer"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
