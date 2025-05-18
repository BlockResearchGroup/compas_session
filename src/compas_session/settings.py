from pydantic import BaseModel


class Settings(BaseModel):
    autosave: bool = False
    autosync: bool = True
