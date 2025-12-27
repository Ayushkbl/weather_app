from fastapi import APIRouter, Query, status, HTTPException, Depends
from typing import Annotated
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import json
from fastapi_limiter.depends import RateLimiter

from app.models.weather import LanguageCode
from app.core.redis import redis_client

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)
dotenv_path = BASE_DIR / '.env'
print(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

@router.get(
        "/weather/current",
        dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def get_current_weather(query: str, language: Annotated[LanguageCode, Query(include_in_schema=False)] = LanguageCode.english):
    cache_key = f"weather:{query.lower()}:{language.value}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        response_data = json.loads(cached_data)
        if "name" not in response_data:
            print(f"response data : {response_data}")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, response_data)
        return response_data


    api_url="https://api.weatherapi.com/v1/current.json"
    api_key = os.getenv("WEATHER_API_KEY")

    params={
        "key" : api_key,
        "q" : query,
        "lang" : language.value
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    print(data)

    if "error" in data:
        response_data = data["error"]["message"]
        print(f"Error Message : {data["error"]["message"]}")
        if data["error"]["code"] != 1006:
            print("Incorrect API Key")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, response_data)
    else:
        response_data : dict = {
            "name" : data["location"]["name"],
            "region" : data["location"]["region"],
            "country" : data["location"]["country"],
            "timezone" : data["location"]["tz_id"],
            "Temperature in ℃" : f"{data["current"]["temp_c"]} ℃",
            "Feels Like in ℃" : f"{data["current"]["feelslike_c"]} ℃",
            "Temperature in ℉" : f"{data["current"]["temp_f"]} ℉",
            "Feels Like in ℉" : f"{data["current"]["feelslike_f"]} ℉",
            "Precipitation in mm" : f"{data["current"]["precip_mm"]} mm",
            "Precipitation in inch" : f"{data["current"]["precip_in"]} inch",
            "Weather Condition" : data["current"]["condition"]["text"]
        }

    redis_client.setex(
        cache_key,
        600,
        json.dumps(response_data, indent=4)
    )

    if "name" not in response_data:
        print("Error here")
        print(f"response data : {response_data}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, response_data)
    return response_data
