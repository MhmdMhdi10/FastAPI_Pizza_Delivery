from pydantic import BaseModel, BaseSettings
from typing import Optional
import os


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "MM10",
                "email": "MM10@gmail.com",
                "password": "mm12061382",
                "is_staff": False,
                "is_active": True,
            }
        }


class Setting(BaseSettings):
    authjwt_secret_key: str = "81810c0c803168c5bc89796aae09be95415df62f34a5643b2522b167c722e30b"

    class Config:
        env_file = os.path.expanduser('.env')


class LoginModel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "MEDIUM"
    user_id: Optional[int]
    user: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
               "quantity": 2,
               "pizza_size": "LARGE",
            }
        }


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "order_status": "PENDING"
            }
        }

