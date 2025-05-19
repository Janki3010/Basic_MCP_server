import os

from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv

load_dotenv()

async def run():
    localhost_url = os.getenv("LOCALHOST_URL")
    async with sse_client(url=f"{localhost_url}/sse") as streams:
        async  with ClientSession(*streams) as session:

            await session.initialize()

            # list available tools
            tools = await session.list_tools()
            print(f"tools: {tools}")

            result = await session.call_tool("add", arguments={"a": 4, "b": 5})
            print(f"Addition: {result.content[0].text}")

            joke_res = await session.call_tool("random_joke")
            print(joke_res.content[0].text)

            # Real-time Tool: Weather
            result = await session.call_tool("get_weather", arguments={"city": "Ahmedabad"})
            print(f"Weather: {result.content[0].text}")

            # list available tools
            resource = await session.list_resources()
            print(f"resource: {resource}")

            quote = await session.read_resource("quote://1")
            print(f"Quote: {quote.contents[0].text}")

            # List available prompts
            prompts = await session.list_prompts()
            print(f"prompts: {prompts}")

            # LLM Query
            prompt = await session.get_prompt("ask_llm", arguments={"query": "What are quantum computers?"})
            print(f"LLM Response: {prompt.messages[0].content.text}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
