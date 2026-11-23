import json
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

from predictor import get_parser_categories
from comparisons import (
    BOROUGH_VALUES,
    DAY_TYPE_VALUES,
    MONTH_VALUES,
    TIME_OF_DAY_VALUES,
    compare_resolution_times,
    format_comparison_message,
)

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
    If the message describes noise from people or activity (loud music,
    parties, shouting, barking dogs, equipment) at a home, business, or
    street, you MUST use "noise - general". Use "noise" only when the
    message does not describe people/activity noise.
    If the message describes construction, plumbing, or building repair
    work, you MUST use "general construction/plumbing". Use "general" only
    when it does not describe that.
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


def answer_comparison(question: str) -> dict | None:
    """Returns a comparison result if the question asks to compare/rank historical
    resolution times across boroughs/agencies/complaint types/location types."""
    categories = get_parser_categories()

    prompt = f"""
    You help with NYC 311 resolution-time questions. Call compare_resolution_times
    ONLY if the user is asking to compare or rank HISTORICAL resolution times across
    boroughs, agencies, complaint types, location types, submission channels, time
    of day, weekday vs weekend, or months (e.g. "which borough is slowest for noise
    complaints", "compare DOB vs DEP", "is it slower on weekends", "how has it
    changed in the last 3 months"). Do NOT call it if the message is about a single
    specific complaint someone wants a time estimate for.

    For a head-to-head between two or more specifically named groups (like "DOB vs
    DEP"), pass those exact values in group_values instead of leaving it empty -
    this restricts the comparison to just the named groups instead of a full breakdown.
    For a relative recent time window, pass the number of months in months_back
    (e.g. "the last 3 months") or the number of days in days_back for shorter
    windows (e.g. "the last 10 days") - use whichever unit the message implies.

    If complaint_type is about noise from people or activity (loud music,
    parties, shouting, barking dogs, equipment), you MUST use "noise - general",
    not "noise". If it's about construction, plumbing, or building repair work,
    you MUST use "general construction/plumbing", not "general".

    USER MESSAGE:
    {question}

    Valid complaint_type values: {json.dumps(categories["complaint_type"])}
    Valid agency values: {json.dumps(categories["agency"])}
    Valid location_type values: {json.dumps(categories["location_type"])}
    Valid borough values: {json.dumps(BOROUGH_VALUES)}
    Valid channel values: {json.dumps(categories["open_data_channel_type"])}
    Valid time_of_day values: {json.dumps(TIME_OF_DAY_VALUES)}
    Valid day_type values: {json.dumps(DAY_TYPE_VALUES)}
    Valid month values: {json.dumps(MONTH_VALUES)}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[compare_resolution_times],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
    except Exception:
        return None

    calls = response.function_calls or []
    if not calls:
        return None

    try:
        result = compare_resolution_times(**calls[0].args)
        return {
            "message": format_comparison_message(result),
            "group_by": result["group_by"],
            "breakdown": result["results"],
        }
    except Exception:
        return None


# if __name__ == "__main__":
#     #question = "A streetlight is completely out at 31st Ave and 34th St in Astoria, Queens. It's on the northwest corner and the block is very dark at night."
#     #question = "There's a party going on at E 68th St in Manhattan, NY. It's super loud and I'm trying to get some sleep"
#     #question = "There is no hot water in this building in 21st Ave in Brooklyn. NY. Water is freezing cold."
#     result = parse_question(question)

#     print(result)