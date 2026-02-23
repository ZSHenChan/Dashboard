from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from .calendar import CalendarEvent

class ReplyOption(BaseModel):
    label: str = Field(description="Short Header for the button. E.g., 'Accept', 'Decline', 'Ask Time'")
    text: List[str] = Field(description="A list of 1-3 short strings to be sent consecutively. E.g. ['can', 'what time?']")
    sentiment: Literal['positive', 'negative', 'neutral'] = Field(description="Helps the UI color-code the button (Green/Red/Gray)")

class DashboardCard(BaseModel):
    title: str
    summary: str = Field(description="A concise 1-sentence summary of the intent. Exclude the sender name if there is no third person in the conversation. Include location and time if possible. Example: 'Asked you if you are going school tomorrow.', 'Said your personal project sucks and won't be useful in the future.'")
    urgency: Literal['low', 'medium', 'high']
    suggested_action: Literal['ignore', 'reply', 'calendar_event']

    reply_options: List[ReplyOption] = Field(default_factory=list, description="Generate 2-3 distinct reply choices if action is 'reply'.")
    auto_reply_allowed: bool = Field(description="Set to True ONLY if the incoming message does not require me to make decision. Example: 'yo check this out!','I am arriving, almost there.', 'nice'")
    calendar_details: Optional[CalendarEvent] = Field(description="Extracted if action is calendar_event")