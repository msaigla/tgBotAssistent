from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserAddSheet(BaseModel):
    chat_id: int
    username: str
    gender: str
    city: str
    where_practicing: str
    were_clients: str
    massage_technique: str
    using_social: str


class UserAddDB(UserAddSheet):
    row_sheet: str


class User(UserAddDB):
    lang: str
    number_of_days: int
    trial: int
    premium: date
    create_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPermission(BaseModel):
    id: int
    login: str


class UserPatch(BaseModel):
    username: str
    gender: str
    city: str
    where_practicing: str
    were_clients: str
    massage_technique: str
    using_social: str
    row_sheet: str
    lang: str
    number_of_days: int
    trial: int
    premium: date
    create_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)
