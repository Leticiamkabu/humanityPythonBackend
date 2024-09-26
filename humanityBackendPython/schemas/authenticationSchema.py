from pydantic import BaseModel



class UserCreation(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number:str
    password: str



class Login(BaseModel):
    email: str
    password: str
    
