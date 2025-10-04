from pydantic import BaseModel, HttpUrl
from typing import Optional


class LectureDetailsByScholarRequest(BaseModel):
    Page: int
    PageSize: int
    ScholarId: int


class Category(BaseModel):
    id: int
    name: str


class Scholar(BaseModel):
    id: int
    name: str
    city: str
    country: str
    language: str


class Centre(BaseModel):
    id: int
    name: str
    city: str
    country: str


class CreatedBy(BaseModel):
    id: int
    fullName: str
    userName: str
    email: str


class UpdatedBy(BaseModel):
    id: int
    fullName: str
    userName: str
    email: str


class LectureDetailsByScholarResponse(BaseModel):
    id: int
    subCategory: str
    title: str
    itemDate: Optional[str] = None
    islamicDate: Optional[str] = None
    language: str
    link: HttpUrl
    views: Optional[int] = None
    audioFile: Optional[str] = None
    imageFile: Optional[str] = None
    isDone: Optional[bool] = None
    category: Category
    centre: Centre
    scholar: Scholar
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    createdBy: Optional[CreatedBy] = None
    updatedBy: Optional[UpdatedBy] = None
