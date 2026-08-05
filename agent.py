from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
    google,
)
from behaviour import AGENT_INSTRUCTION, AGENT_RESPONSE
from ai_tools import get_weather, search_web, send_email
import logging

load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO)

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.0-flash-exp",
                voice="Puck",
                temperature=0.8,
                instructions=AGENT_INSTRUCTION,
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=AGENT_RESPONSE,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
