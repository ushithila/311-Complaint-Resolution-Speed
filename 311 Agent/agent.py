import json
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

from predictor import get_parser_categories

class Query(BaseModel):
    complaint_type: str | None = None
    agency: str | None = None
    location_type: str | None = None
    open_data_channel_type: str | None = None
    #borough: Borough | None = None
    #incident_zip: str | None = None
    #complaint_detail: str | None = None

load_dotenv()
client = genai.Client()

def _validate_categories(query: Query) -> Query:
    categories = get_parser_categories()
    data = query.model_dump()
    for field in ("complaint_type", "agency", "location_type", "open_data_channel_type"):
        valid = [c for c in categories[field] if c.upper() != "UNKNOWN"]
        lookup = {c.lower(): c for c in valid}
        value = data[field]
        data[field] = lookup.get(value.strip().lower()) if value else None
    return Query(**data)

def parse_question(question: str, current_query: Query | None = None,) -> Query:
    existing = (current_query or Query()).model_dump()
    categories = get_parser_categories()

    prompt = f"""
    You are a NYC 311 complaint question parser.
    Update the existing query using the user's latest message.

    EXISTING QUERY:
    {json.dumps(existing)}

    USER'S LATEST MESSAGE:
    {question}

    FIELD RULES:

    complaint_type: the closest match from this list, exactly as written,
    or null if the message doesn't describe a 311 issue.
    {json.dumps(categories["complaint_type"])}

    agency: ALWAYS infer the responsible NYC agency from the complaint_type,
    choosing exactly from this list. Re-derive it whenever complaint_type
    changes. Use null only if complaint_type is null.
    {json.dumps(categories["agency"])}

    location_type: the type of location, chosen exactly from this list,
    or null if it is not stated or clearly implied.
    {json.dumps(categories["location_type"])}

    open_data_channel_type: how the complaint was submitted. Choose exactly
    from this list when the user states or clearly implies it,
    Use null if the message gives no indication of how it was submitted.
    Do not guess based on the type of complaint alone.
    {json.dumps(categories["open_data_channel_type"])}

    IMPORTANT:
    - Preserve existing values unless the user gives new information or a correction.
    - Never invent complaint_type or location_type. Use null if unknown.
    - Return only the four schema fields.
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Query,
        ),
    )
    parsed = Query.model_validate_json(response.text)

    if parsed.open_data_channel_type is None:
        parsed.open_data_channel_type = existing["open_data_channel_type"]

    return _validate_categories(parsed)




# if __name__ == "__main__":
#     #question = "A streetlight is completely out at 31st Ave and 34th St in Astoria, Queens. It's on the northwest corner and the block is very dark at night."
#     #question = "There's a party going on at E 68th St in Manhattan, NY. It's super loud and I'm trying to get some sleep"
#     #question = "There is no hot water in this building in 21st Ave in Brooklyn. NY. Water is freezing cold."
#     result = parse_question(question)

#     print(result)