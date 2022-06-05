from app.utils.io_utils import Base
from sqlalchemy import Column, Integer, String, BOOLEAN


class user_data(Base):
    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)

    def __init__(self, id, name, gender):
        self.id = id
        self.name = name
        self.gender = gender
