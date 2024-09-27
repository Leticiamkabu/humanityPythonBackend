# from pydantic import BaseModel
# from enum import Enum


# class Role(str, Enum):
#     admin = "ADMIN"
#     user = "USER"
    


# class UserCreation(BaseModel):
#     first_name: str
#     last_name: str
#     email: str
#     phone_number:str
#     password: str



# class Login(BaseModel):
#     email: str
#     password: str
    

from fastapi import Form, Depends
from pydantic import BaseModel

class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str

# A function to create the schema from form data
def create_user_schema(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...)
) -> CreateUserSchema:
    return CreateUserSchema(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        password=password
    )


class Login(BaseModel):
    email: str
    password: str

# A function to create the schema from form data
def login_schema(
    email: str = Form(...),
    password: str = Form(...)
) -> Login:
    return Login(  # Create an instance of the Login class
        email=email,
        password=password
    )