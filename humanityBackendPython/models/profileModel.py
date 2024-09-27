from sqlalchemy import Column, String, UUID, DateTime, func, text, LargeBinary
from database.databaseConnection import Base
from sqlalchemy.orm import relationship



class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    username = Column(String,nullable=False)
    image = Column(String, nullable=False)  # Column to store binary image data
    image_filename = Column(String, nullable=False)

