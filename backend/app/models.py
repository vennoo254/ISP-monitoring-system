from sqlalchemy import Column, Integer, String
from .database import Base

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    address = Column(String, unique=True, index=True)
