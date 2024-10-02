from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import uuid
import os

from sqlalchemy import select, or_
import requests
from passlib.context import CryptContext
import bcrypt
import random
# from utils.minio_util import upload_file



from models.profileModel import *
# from schemas.itemsSchema import *
from database.databaseConnection import SessionLocal
# from security.auth import *
# from security.error_handling import *
# from security.auth_bearer import jwtBearer

# # logs
# from logging_lib import LogConfig
# from logging.config import dictConfig
import logging

# email
# from emails import *
# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
# from smtplib import SMTPException
import os
import string


# file upload
from fastapi import UploadFile,status, File, Form
# from utils.minio_util import upload_file

import re
from sqlalchemy.sql import func
import base64


# # loging config
# dictConfig(LogConfig().dict())
logger = logging.getLogger("Humanity App")



# create a connection to the database
async def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]




router = APIRouter()


# create_profile

@router.post("/profile/user_profile")
async def create_profile(db: db_dependency, username : str = Form(...),  file: UploadFile = File(...)):

    # Validate file type (e.g., images only)
    allowed_file_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed types: jpeg, png, gif.")
    
    #  Read the file content as binary data
    profile_image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(profile_image_data).decode('utf-8')
    
    # Create an image instance and associate it with the new item
    new_profile_image = Profile(
        username=username,  # Use new_item_data.id here
        image=image_base64,
        image_filename=file.filename
    )
    
    # Add the new image to the database
    db.add(new_profile_image)
    await db.commit()
    
    logger.info("Item image created and saved in the database with ID: %s", new_profile_image.id)

    return {"message": "Item image creation successful", "item_image_id": new_profile_image.id}


# get profile by id
@router.get("/profile/get_profile_by_id")
async def get_profile_by_id(profile_id: uuid.UUID ,db: db_dependency):

    profile_data = await db.get(Profile, profile_id)
    
    
    if profile_data  is None:
        raise HTTPException(status_code=200, detail="item with id does not exist", data = profile_data)
    
    return profile_data


# get profile by username
@router.get("/profile/get_profile_by_username/{username}")
async def get_profile_by_username(username: str, db: db_dependency):
    profile_data = await db.execute(select(Profile).where(Profile.username == username))
    profile_image_data = profile_data.scalar()

    if profile_image_data is None:
        raise HTTPException(status_code=404, detail="Profile with the given username does not exist")

    # Create the profile image object
    profile_image_info = {
        "image": f"data:image/png;base64,{profile_image_data.image}" if profile_image_data.image else None,
        "image_filename": profile_image_data.image_filename if profile_image_data.image_filename else None
    }

    return profile_image_info



# get all profile
@router.get("/profile/get_all_profiles")
async def get_all_profiles( db: db_dependency):

    profiles = await db.execute(select(Profile))
    profile_data = profiles.scalars().all()
    
    if profile_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = profile_data)
    
    return profile_data


# update profile by id
@router.patch("/profile/update_profile/{profile_id}")
async def update_item_image(profile_id: uuid.UUID, db: db_dependency, file: UploadFile = File(...)):

    
    logger.info("Endpoint : update_item_image")
    

    # query for user data
    profile_data = await db.get(Profile, profile_id)
    logger.info("Item image data queried successfully")

    image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    profile_data.image_filename = file.filename
    profile_data.image = image_base64

    db.add(profile_data)
    await db.commit()
    await db.refresh(item_image_data)

    return "Profile updated successfully"



# update profile by username
@router.patch("/profile/update_profile")
async def update_item_image(db: db_dependency, username: str = Form(...), file: UploadFile = File(...)):
    
    logger.info("Endpoint : update_item_image")
    

    # query for user data
    profile = await db.execute(select(Profile).where(Profile.username == username))
    profile_data = profile.scalar_one_or_none()
    logger.info("Item image data queried successfully")

    image_data = await file.read()
    
    # Convert to Base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    profile_data.image_filename = file.filename
    profile_data.image = image_base64

    db.add(profile_data)
    await db.commit()
    await db.refresh(profile_data)

    return "Profile updated successfully"


# delete profile by id
@router.delete("/profile/delete_profile_by_id")
async def delete_profile_by_id(profile_id: uuid.UUID, db: db_dependency):

    profile = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile_data = profile.scalar_one_or_none()
    
    if profile_data is None:
        raise HTTPException(status_code=404, detail="Item not found")

    
    # Delete the user
    await db.delete(profile_data)

    await db.commit()


    return "Profile deleted successfully"

