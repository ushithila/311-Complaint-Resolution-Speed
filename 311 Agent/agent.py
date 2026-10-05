from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from enum import Enum

class ComplaintType(str, Enum):
    ILLEGAL_PARKING = "Illegal Parking"
    NOISE_RESIDENTIAL = "Noise - Residential"
    HEAT_HOT_WATER = "HEAT/HOT WATER"
    BLOCKED_DRIVEWAY = "Blocked Driveway"
    NOISE_STREET_SIDEWALK = "Noise - Street/Sidewalk"
    UNSANITARY_CONDITION = "UNSANITARY CONDITION"
    STREET_CONDITION = "Street Condition"
    PLUMBING = "PLUMBING"
    ABANDONED_VEHICLE = "Abandoned Vehicle"
    WATER_SYSTEM = "Water System"
    DIRTY_CONDITION = "Dirty Condition"
    PAINT_PLASTER = "PAINT/PLASTER"
    SNOW_ICE = "Snow or Ice"
    NOISE_COMMERCIAL = "Noise - Commercial"
    NOISE = "Noise"
    TRAFFIC_SIGNAL = "Traffic Signal Condition"
    NOISE_VEHICLE = "Noise - Vehicle"
    DOOR_WINDOW = "DOOR/WINDOW"
    ENCAMPMENT = "Encampment"
    WATER_LEAK = "WATER LEAK"

class Borough(str, Enum):
    BROOKLYN = "BROOKLYN"
    QUEENS = "QUEENS"
    BRONX = "BRONX"
    MANHATTAN = "MANHATTAN"
    STATEN_ISLAND = "STATEN ISLAND"

class Agency(str, Enum):
    NYPD = "NYPD"
    HPD = "HPD"
    DSNY = "DSNY"
    DOT = "DOT"
    DEP = "DEP"
    DOB = "DOB"
    DPR = "DPR"
    DOHMH = "DOHMH"
    DHS = "DHS"
    DCWP = "DCWP"
    TLC = "TLC"
    OOS = "OOS"
    DOE = "DOE"
    NYC311_PRD = "NYC311-PRD"
    OTI = "OTI"
    EDC = "EDC"

class Query(BaseModel):
    complaint_type: ComplaintType | None = None
    complaint_detail: str | None = None
    agency: Agency | None = None
    borough: Borough | None = None
    location_type: str | None = None
    incident_zip: str | None = None


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

            Only extract information that is stated or strongly supported by
            the user's question.

            If information is missing or cannot be determined, return null.
            Never invent information.

            FIELD RULES:

            complaint_type:
            Map the user's problem to the closest matching NYC 311 "Problem"
            value from the allowed values in the schema.

            complaint_detail:
            Extract the specific detail of the problem when it is clear.

            agency:
            Only provide an agency when:
            1. The user explicitly names the agency, OR
            2. The agency is an extremely clear and direct match to the complaint.

            borough:
            Extract the borough when the user provides it.

            location_type:
            Extract the type of location when the user provides enough information
            to determine it.

            incident_zip:
            Extract the ZIP code only when the user provides it.
            Do not derive a ZIP code from an address.

            IMPORTANT:
            - Do not invent missing fields.
            - Do not guess a ZIP code.
            - Do not guess an agency.
            - Do not confuse an address with a ZIP code.
            - Preserve the dataset's exact complaint_type formatting.
            - Use null when uncertain.

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
    #question = "There is no hot water in this building in 21st Ave in Brooklyn. NY. Water is freezing cold."
    result = parse_question(question)

    print(result)