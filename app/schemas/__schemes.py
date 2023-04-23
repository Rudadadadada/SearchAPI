from datetime import datetime, timezone

from fastapi import HTTPException
from starlette import status
import pytz

from pydantic import BaseModel, validator


# Здесь описаны различные pydantic модели с валидаторами... Не успеваю описать каждый.
class FolderModel(BaseModel):
    url: str

    @validator('url')
    def url_validator(cls, path):
        if '/' not in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no '/' in path")
        elif path.startswith('/') is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path should starts with '/'")
        elif '//' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is double '//' in path")
        elif '/ ' in path or ' /' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is extra space in path")
        return path


class FileModel(BaseModel):
    url: str
    text: str
    size: int
    creation_time: str

    @validator('url')
    def url_validator(cls, path):
        if '/' not in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no '/' in path")
        elif path.startswith('/') is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path should starts with '/'")
        elif '//' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is double '//' in path")
        elif '/ ' in path or ' /' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is extra space in path")
        return path

    @validator('size')
    def size_validator(cls, size):
        if size < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Size can not be less then zero")
        return size

    @validator('creation_time')
    def date_validator(cls, date):
        utc = pytz.UTC
        date = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
        if not datetime(year=2000, month=1, day=1).replace(tzinfo=utc) <= date.replace(tzinfo=utc) \
               <= datetime.now().replace(tzinfo=utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date out of range")
        return date


class SizeSearchModel(BaseModel):
    value: int
    operator: str

    @validator('value')
    def size_validator(cls, size):
        if size < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Size can not be less then zero")
        return size

    @validator('operator')
    def operator_validator(cls, operator):
        if operator not in ['eq', 'gt', 'lt', 'ge', 'le']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Incorrect operator: {operator}")
        return operator


class DateSearchModel(BaseModel):
    value: str
    operator: str

    @validator('value')
    def date_validator(cls, date):
        utc = pytz.UTC
        date = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
        if not datetime(year=2000, month=1, day=1).replace(tzinfo=utc) <= date.replace(tzinfo=utc) \
               <= datetime.now().replace(tzinfo=utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date out of range")
        return date

    @validator('operator')
    def operator_validator(cls, operator):
        if operator not in ['eq', 'gt', 'lt', 'ge', 'le']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Incorrect operator: {operator}")
        return operator


class SearchModel(BaseModel):
    text: str
    file_mask: str
    url: str
    size: SizeSearchModel
    creation_time: DateSearchModel

    @validator('url')
    def url_validator(cls, path):
        if '/' not in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is no '/' in path")
        elif path.startswith('/') is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path should starts with '/'")
        elif '//' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is double '//' in path")
        elif '/ ' in path or ' /' in path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is extra space in path")
        return path
