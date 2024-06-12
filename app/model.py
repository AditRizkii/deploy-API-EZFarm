from pydantic import BaseModel, Field
import uuid
from typing import List

class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens...."
            }
        }

class UserSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        orm_mode = True

single_user = UserSchema(username="admin", password="e260bab41ec5c816f90e681cebc4e661414c049bc7f5f7f8")

class UserLoginSchema(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "token": "weakpassword"
            }
        }

class ResultSchema(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    penanganan : List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Brown Spot",
                "penanganan": [
                    "Penggunaan varietas tahan: Pilih varietas padi yang tahan terhadap penyakit ini.",
                    "Pemupukan seimbang: Gunakan pupuk secara bijaksana, terutama nitrogen, karena pemupukan berlebihan dapat meningkatkan kerentanan tanaman."
                    ]
            }
        }

# class TrackingSchema(BaseModel):
#     _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
#     hari: str = Field(...)
#     penanganan : List[str]

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "name": "Brown Spot",
#                 "penanganan": [
#                     "Penggunaan varietas tahan: Pilih varietas padi yang tahan terhadap penyakit ini.",
#                     "Pemupukan seimbang: Gunakan pupuk secara bijaksana, terutama nitrogen, karena pemupukan berlebihan dapat meningkatkan kerentanan tanaman."
#                     ]
#             }
#         }

