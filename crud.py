# Handdle different database operations.
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from twitter_database import User, Post, Comment
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# Create a new user
def create_user(db: Session, user_name: str, name: str, password: str):
    hashed_pwd=hash_password(password)
    new_user= User(user_name=user_name, name=name, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Update the name of user
def update_name(db: Session, user_name: str, new_name: str):
    user = db.query(User).filter(User.user_name==user_name).first()
    if user:
        user.updated_at = datetime.datetime.utcnow()
        user.name=new_name
        db.commit()
        db.refresh(user)
        return user
    return None

def create_post(db: Session, user_id: int, text: str):
    post = Post(text=text, user_id= user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def update_post(db: Session, post_id: int, new_text: str):
    post=db.query(Post).filter(Post.id==post_id).first()
    if post:
        post.text = new_text
        db.commit()
        db.refresh(post)
    return post

def delete_post(db: Session, post_id: int):
    post=db.query(Post).filter(Post.id==post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post

def create_comment(db: Session, text: str, post_id: int, user_id: int):
    comment=Comment(text=text, post_id=post_id, user_id=user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment




