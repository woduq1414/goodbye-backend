from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


from db import Base


class User(Base):
    __tablename__ = "user"

    seq = Column(Integer, primary_key=True, index=True, autoincrement=True)

    id = Column(String, nullable=False)
    pw = Column(String, nullable=False)
    name = Column(String, nullable=False)



class Target(Base):
    __tablename__ = "target"

    seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_seq = Column(Integer, ForeignKey("user.seq"))

    target_name = Column(String, nullable=False)

    target_lost_date = Column(DateTime, nullable=True)
    target_add_datetime = Column(DateTime, nullable=False)
    target_relation = Column(String, nullable=True)


    target_kakao_chat = Column(String, nullable=True)
    target_history = Column(String, nullable=True)


class Diary(Base):
    __tablename__ = "diary"

    seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_seq = Column(Integer, ForeignKey("user.seq"))
    target_seq = Column(Integer, ForeignKey("target.seq"))

    diary_dday = Column(Integer, nullable=False)
    diary_content = Column(String, nullable=False)
    diary_add_datetime = Column(DateTime, nullable=False)