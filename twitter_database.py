from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy import DateTime, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

load_dotenv(".env")
password=os.environ.get("mydbpass")

#Configure SQLAlchemy Connection to Local PostgreSQL
DATABASE_URL = f"postgresql://reyhaneh:{password}@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)

#Create a sesssion
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Define an ORM Model (Table)
Base = declarative_base()
class User(Base):
    __tablename__='twitter_users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

class Post(Base):
    __tablename__='posts'
    id = Column (Integer, primary_key=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    user_id = Column (Integer, ForeignKey("twitter_users.id"), nullable=False)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__='comments'
    id = Column (Integer, primary_key=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("twitter_users.id"), nullable=False)
    # The next two line mean comment.user and comment.post attributes are available!
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


#Connect and create table
Base.metadata.create_all(engine)
print("Table twitter_users create successfully!")

#Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

