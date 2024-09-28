from sqlalchemy import Column, String, UUID, DateTime, func, text, LargeBinary
from database.databaseConnection import Base
from sqlalchemy.orm import relationship




class Item(Base):
    __tablename__ = 'items'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    location = Column(String, nullable=True)
    yearsUsed = Column(String, nullable=True,)
    # image = Column(String, nullable=False)
    # image = Column(LargeBinary, nullable=True)  # Column to store binary image data
    # image_filename = Column(String, nullable=True)
    created_on = Column(DateTime, nullable=True,
                        default=func.current_timestamp())




class ItemImage(Base):
    __tablename__ = 'item_images'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text(
        "uuid_generate_v4()"), unique=True, index=True)
    item_id = Column(String,nullable=False)
    image = Column(String, nullable=False)  # Column to store binary image data
    image_filename = Column(String, nullable=False)

