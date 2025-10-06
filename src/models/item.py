from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


# ---------- Submodels ----------


class Author(BaseModel):
    id: Optional[Union[str, int]] = None
    name: str
    role: Optional[str] = Field(
        default="unknown",
        regex="^(scholar|writer|translator|compiler|speaker|unknown)$",
    )
    city: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None


class Organisation(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class QuranReference(BaseModel):
    surah: Union[str, int]
    ayahStart: int
    ayahEnd: int


class HadithReference(BaseModel):
    book: str
    volume: Optional[str] = None
    hadithNumber: Optional[str] = None


class DateInfo(BaseModel):
    gregorian: datetime
    islamic: Optional[str] = None


class Content(BaseModel):
    summary: Optional[str] = None
    tags: List[str] = []
    translation: Optional[str] = None


class Media(BaseModel):
    audioFile: Optional[str] = None
    videoFile: Optional[str] = None
    imageFile: Optional[str] = None
    pdfFile: Optional[str] = None
    link: Optional[HttpUrl] = None


class Audience(BaseModel):
    level: str = Field(default="all", regex="^(beginner|intermediate|advanced|all)$")
    intendedAudience: List[str] = []


class Provenance(BaseModel):
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# ---------- Main Schema ----------


class ItemSchema(BaseModel):
    id: Union[str, int]
    title: str
    type: str = Field(..., regex="^(lecture|book|blog|article|tafseer|hadith|note)$")
    language: str

    author: Author
    organisation: Optional[Organisation] = None

    quranReference: Optional[QuranReference] = None
    hadithReference: Optional[HadithReference] = None
    date: DateInfo

    content: Optional[Content] = None
    media: Optional[Media] = None
    audience: Optional[Audience] = None
    provenance: Optional[Provenance] = None

