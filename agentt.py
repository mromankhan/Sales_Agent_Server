from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = 'gemini/gemini-2.0-flash'

agent = Agent(
    name = "Sales Assistant",
    instructions = "You are a Sales Assistant Agent respond only to sales-related queries. Politely decline anything unrelated.",
    model = LitellmModel(model=MODEL)
)

# result = Runner.run_sync(agent, "Who is the founder of Pakistan?")
# print(result.final_output)