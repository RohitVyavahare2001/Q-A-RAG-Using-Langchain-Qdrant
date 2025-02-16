from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    question = Column(String(1000))
    answer = Column(String(4000))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)