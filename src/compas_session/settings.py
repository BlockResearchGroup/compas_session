from pydantic import BaseModel


class Settings(BaseModel):
    autosave: bool = True
