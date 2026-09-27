from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

class Query(BaseModel):
    complaint_type: str | None = None
    complaint_detail: str | None = None
    agency: str | None = None
    city: str | None = None
    address: str | None = None

load_dotenv()
client = genai.Client()

def parse_question(question: str):
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=
            f"""
            You are a NYC 311 question parser.

            Your job is to convert a user's natural language questions into structured information
            about a 311 complaint.

            Determine what the user is asking for and extract any relevant information.

            If the user does not provide a piece of information, leave it as null.

            The possible complaint type values are:
            - Illegal Parking
            - Water Maintenance
            - Blocked Driveway
            - Noise - Cause of Noise
            - Food Establishment
            - Electric
            - General

            For Noise complaints, replace "Cause of Noise" with the specific cause of the noise described by the user.

            For example:
            - "There is a party going on" -> "Noise - Residental, Complaint Detail: Loud Music/Party"
            - "Car is blasting music" -> "Noise - Vehicle, Complaint Detail: Car/Truck Music"
            - "Lots of loud laughging and talking outside while im trying to sleep" -> "Noise - Street/Sidewalk, Complaint Detail: Loud Talking"

            If the user does not provide the cause of the noise, use "Noise - Unknown"

            Do not modify the format of the other complaint types.

            User question:
            {question}
            """,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Query.model_json_schema(),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    return Query.model_validate_json(response.text)

if __name__ == "__main__":
    #question = "A streetlight is completely out at 31st Ave and 34th St in Astoria, Queens. It's on the northwest corner and the block is very dark at night."
    #question = "There's a party going on at E 68th St in Manhattan, NY. It's super loud and I'm trying to get some sleep"
    question = "There is no hot water in this building in 21st Ave in Brooklyn. NY. Water is freezing cold."
    result = parse_question(question)

    print(result)