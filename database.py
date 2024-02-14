from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    longest_message = Column(String)

class Emotion(Base):
    __tablename__ = 'emotion'
    emotion_id = Column(Integer, primary_key=True)
    sademotion = Column(Integer)
    happyemotion = Column(Integer)
    neutralemotion = Column(Integer)

class Word(Base):
    __tablename__ = 'word'
    word_id = Column(Integer, primary_key=True)
    word = Column(String)

class Slideshow(Base):
    __tablename__ = 'slideshow'
    slideshow_id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('user.user_id'))
    receiver_id = Column(Integer, ForeignKey('user.user_id'))
    theme_id = Column(String)
    weekly_id = Column(Integer, ForeignKey('weekly.weekly_id'))
    winner_id = Column(Integer, ForeignKey('user.user_id'))
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    winner = relationship("User", foreign_keys=[winner_id])

class Weekly(Base):
    __tablename__ = 'weekly'
    weekly_id = Column(Integer, primary_key=True)
    sun = Column(Integer)
    mon = Column(Integer)
    tue = Column(Integer)
    wed = Column(Integer)
    thu = Column(Integer)
    fri = Column(Integer)
    sat = Column(Integer)

class WordUsage(Base):
    __tablename__ = 'word_usage'
    word_usage_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    word_id = Column(Integer, ForeignKey('word.word_id'))
    count = Column(Integer)
    user = relationship("User")
    word = relationship("Word")

