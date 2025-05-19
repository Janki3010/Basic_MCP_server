import httpx
import os
import openai
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import psycopg2

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")
# Create an MCP server
mcp = FastMCP()

### Tools ###
# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    return a+b


@mcp.tool()
def get_weather(city: str) -> str:
    """
    Fetch weather using Open-Meteo (free, no API key).
    """
    try:
        # Use Open-Meteo's geocoding to get lat/lon from city
        url = os.getenv("GEO_URL")
        geo_url = f"{url}?name={city}&count=1"
        geo_resp = httpx.get(geo_url, timeout=10).json()

        if "results" not in geo_resp or not geo_resp["results"]:
            return f"City '{city}' not found."

        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]

        # Get weather from Open-Meteo
        w_url = os.getenv("WEATHER_URL")
        weather_url = f"{w_url}?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = httpx.get(weather_url, timeout=10).json()

        weather = weather_resp["current_weather"]
        temp = weather["temperature"]
        wind = weather["windspeed"]
        return f"Temperature in {city} is {temp}°C with wind speed {wind} km/h."

    except Exception as e:
        return f"Error getting weather: {e}"

@mcp.tool()
def random_joke() -> str:
    try:
        joke_url : str = os.getenv("JOKE_URL")
        resp = httpx.get(joke_url).json()
        return f"{resp['setup']} - {resp['punchline']}"
    except Exception as e:
        return f"Error fetching joke: {e}"


### Resources ##
@mcp.resource("quote://{quote_id}")
def get_quote(quote_id: int):
    return get_quote_from_postgres(quote_id)

### Prompts ###
@mcp.prompt()
def ask_llm(query: str):
    """
    Uses OpenAI GPT to answer the query.
    """
    if not openai.api_key:
        return "Missing OpenAI API key."

    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        return f"Error querying LLM: {e}"


def get_quote_from_postgres(quote_id: int) -> str:
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DATABASE_NAME"),
            user=os.getenv("POSTGRES_USERNAME"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT quote FROM quotes WHERE id = %s", (quote_id,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else f"No quote found for ID {quote_id}"
    except Exception as e:
        return f"DB Error: {e}"


if __name__ == "__main__":
    mcp.run(transport='sse')
