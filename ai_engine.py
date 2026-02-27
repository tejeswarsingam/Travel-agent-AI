import os
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the structure for a single activity
class Activity(BaseModel):
    time: str = Field(description="Time of day")
    title: str = Field(description="Name of the place or activity")
    description: str = Field(description="Details about the activity")

# Define the structure for a single day
class DailyPlan(BaseModel):
    day: int
    activities: List[Activity]

# Define the full itinerary wrapper
class FullItinerary(BaseModel):
    destination: str
    daily_plans: List[DailyPlan]

def generate_itinerary_logic(dest, interests, days):
    # Initialize Gemini 2.0 (Stable for 2026)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    structured_llm = llm.with_structured_output(FullItinerary)

    prompt = f"""
    Create a detailed {days}-day itinerary for {dest}.
    Interests: {', '.join(interests)}.
    Make it engaging and unique for each day.
    """

    response = structured_llm.invoke(prompt)
    return response.model_dump() # Convert to dict for JSON transfer