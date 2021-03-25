from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base
import datetime

class ShortURL(Base):
    __tablename__ = 'short_urls'

    id = Column(Integer, primary_key = True, index = True)
    base_url = Column(String)
    short = Column(String)
    counter = Column(Integer, default = 0)
    created = Column(DateTime, default = datetime.datetime.utcnow)