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



from models.authenticationModel import *
from schemas.authenticationSchema import *
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


# create user
@router.post("/auth/create_user")
async def create_user(User_data: UserCreation, db: db_dependency):

    logger.info("Endpoint : create_user")

       # create user 

    hashed_password = bcrypt.hashpw(User_data.password.encode('utf-8'), bcrypt.gensalt())
    user_data = User(
                email=User_data.email,
                firstname=User_data.first_name,
                lastname =User_data.last_name,
                username = User_data.first_name + User_data.last_name[0],
                phone_number=User_data.phone_number,
                password =hashed_password.decode('utf-8'),
                role ="USER"

            )
    

    db.add(user_data)
    await db.commit()
    logger.info("User created and saved in the database")


    logger.info("User Registeration Sucessful")
    return {"message": "User registeration successfully", "User": user_data}




# create Admin
@router.post("/auth/create_admin")
async def create_admin_user( db: db_dependency):

    logger.info("Endpoint : create_user")

       # create user 

    admin_password = "boss"
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    admin_user_data = User(
                email= "solo@gmail.com",
                firstname="so",
                lastname ="lo",
                # username = User.firstname + User.lastname[0],
                phone_number="0556852682",
                password =hashed_password.decode('utf-8'),
                role ="ADMIN"

            )
    admin_user_data.username = admin_user_data.firstname + admin_user_data.lastname[0]

    

    db.add(admin_user_data)
    await db.commit()
    logger.info("User created and saved in the database")


    logger.info("User Registeration Sucessful")
    return {"message": "Admin User registeration successfully", "User": admin_user_data}






# login without token

@router.post("/auth/login")
async def login(login: Login, db: db_dependency):

    # Query for user data using email
    user = await db.execute(select(User).where(User.email == login.email))
    user_data = user.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

    # Check if the password is valid
    is_valid = bcrypt.checkpw(login.password.encode('utf-8'), user_data.password.encode('utf-8'))

    if is_valid:
        logger.info("User login successful")
        return {"message": "User login successful", "data": user_data}

    else:
        raise HTTPException(status_code=400, detail="Incorrect password")
    


# login with token

@router.post("/auth/login_generate_token")
async def login_generate_token(login: Login, db: db_dependency):
    # Query for user data using email

    user = await db.execute(select(User).where(User.email == login.email))
    user_data = user.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

    # Check if the password is valid
    is_valid = bcrypt.checkpw(login.password.encode('utf-8'), user_data.password.encode('utf-8'))

    if is_valid:
        # Generate token
        token = generate_characters()
        
        # Save token to the user data
        user_data.token = token
        db.add(user_data)
        await db.commit()
        logger.info("User token saved")

        # Return success message and token
        return {"message": "User token saved", "token": token,"data": user_data.id}

    else:
        raise HTTPException(status_code=400, detail="Incorrect password")


# verify token
@router.get("/auth/verify_login_token")
async def verify_login_token(token: str,user_id: uuid.UUID, db: db_dependency):

    # Query for user data using email
    user_data = await db.get(User, user_id)
    # user_data = user.scalar()
    
    # Check if the user was found
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User data queried successfully")

  
    if user_data.token == token:
        
        logger.info("User login successful")
        return {"message": "User login successful", "data": user_data}

    else:
        raise HTTPException(status_code=400, detail="Invalid token")
    





def generate_characters(length: int = 8) -> str:
    # Define the possible characters (alphanumeric)
    characters = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    random_characters = ''.join(random.choice(characters) for _ in range(length))
    
    return random_characters




# get all users
@router.get("/auth/get_all_users")
async def get_all_users( db: db_dependency):

    users = await db.execute(select(User))
    users_data = users.scalars().all()
    
    if users_data  is None:
        raise HTTPException(status_code=200, detail="No user data exists", data = result)
    
    return users_data 
    


# get user by id
@router.get("/auth/get_user_by_id")
async def get_all_users( user_id: uuid.UUID ,db: db_dependency):

    user_data = await db.get(User, user_id)
    
    
    if user_data  is None:
        raise HTTPException(status_code=200, detail="user with id does not exist", data = user_data)
    
    return user_data



# get user details by usename
@router.get("/auth/get_user_by_username")
async def get_users_by_username( username: str ,db: db_dependency):

    user = await db.execute(select(User).where(User.username == username))
    user_data = user.scalar()
    
    if user_data  is None:
        raise HTTPException(status_code=200, detail="user with provided username does not exist", data = user_data)
    
    return user_data




# get users by role
@router.get("/auth/get_users_by_role")
async def get_users_by_role( role: str ,db: db_dependency):

    user = await db.execute(select(User).where(User.role == role))
    user_data = user.scalars().all()
    
    
    if user_data  is None:
        raise HTTPException(status_code=200, detail="users with role does not exist", data = user_data)
    
    return user_data




# get total number of users
@router.get("/auth/get_total_number_of_users")
async def get_total_number_of_users(db: db_dependency):

    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()  

    return {"total_users": total_users}




# get number of users by role
@router.get("/auth/get_total_number_of_users_by_role")
async def get_total_number_of_users_by_role(role: str, db: db_dependency):

    result = await db.execute(select(func.count(User.id)).where(User.role == role))
    total_users_by_role = result.scalar()

    if total_users_by_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return {"total_users_by_role": total_users_by_role}




# update user by id


@router.patch("/auth/update_individual_user_fields/{user_id}")
async def update_user(user_id: uuid.UUID, db: db_dependency, user_input: UserCreation):

    
    logger.info("Endpoint : update_user")
    
    
        # query for user data
    user_data = await db.get(User, user_id)
    logger.info("User data queried successfully")
        
        # convert user data and user input into a dictionary
    converted_user_data = user_data.__dict__
    inputs = user_input.__dict__
       
        # copy converted user data
    result = converted_user_data.copy() 

        # check if user input key is found in the converted user data, if true initialize the converted use data key with the user inputs value
    for key, value in inputs.items():
        if key in result:
            result[key] = value  
            
        # replace the old user data with the new user data
    for key, value in result.items():
        setattr(user_data, key, value)
            
    logger.info("User data ready for storage")
        
        # save user data in database
    db.add(user_data)
    await db.commit()
    await db.refresh(user_data)
    logger.info("User data updated")
        
        
    return user_data
    
    
    



# delete user

@router.delete("/auth/delete_user_by_id")
async def delete_user_by_id(user_id: uuid.UUID, db: db_dependency):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    await db.delete(user)
    await db.commit()


    return "user deleted successfully"


@router.patch("/auth/update_user_field/{user_id}")
async def update_user_field(user_id: uuid.UUID, user_input: dict, db: db_dependency):



    logger.info("Endpoint : update_user_filed")
    
    
        # query for user data
    user_data = await db.get(User, user_id)
    logger.info("User data queried successfully")
        
        # convert user data and user input into a dictionary
    converted_user_data = user_data.__dict__
    inputs = user_input
       
        # copy converted user data
    result = converted_user_data.copy() 

        # check if user input key is found in the converted user data, if true initialize the converted use data key with the user inputs value
    for key, value in inputs.items():
        if key in result:
            result[key] = value  
            
        # replace the old user data with the new user data
    for key, value in result.items():
        setattr(user_data, key, value)
            
    logger.info("User data ready for storage")
        
        # save user data in database
    db.add(user_data)
    await db.commit()
    await db.refresh(user_data)
    logger.info("User data updated")
        
        
    return user_data
    

