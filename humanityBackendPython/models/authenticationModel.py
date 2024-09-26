from sqlalchemy import Column, String, UUID, DateTime, func, text
from database.databaseConnection import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    token = Column(String, nullable=True, unique=True)
    role = Column(String, nullable=True,default="UNIDENTIFIED")
    # profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile = Column(String, nullable=True, unique=True)
    created_on = Column(DateTime, nullable=True,
                        default=func.current_timestamp())



    # use it in the profile model
    # user = relationship("User", back_populates="profile")

