from typing import Optional, Literal
from pydantic import BaseModel, Field

class CalendarEvent(BaseModel):
    title: str = Field(description="The title of the event")
    datetime: Optional[str] = Field(description="event date and time in UTC format")
    duration: Optional[int] = Field(description="Event duration in minutes")
    event_type: Literal['Work','Event','Misc','Due date','Meeting','Trip'] = Field(description="The category of the event")