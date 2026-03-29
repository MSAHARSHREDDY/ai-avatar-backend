






#Modified code for voice agent instaed of open ai
import os
from dotenv import load_dotenv

# LiveKit & Agents
from livekit import agents, rtc
from livekit.agents import  AgentSession, Agent, RoomInputOptions, TurnHandlingOptions,inference
from livekit.plugins import  noise_cancellation, avatario, silero, deepgram, cartesia
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# MCP & Custom
from mcp_client import MCPServerSse
from mcp_client.agent_tools import MCPToolsIntegration
from tools import open_url
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[open_url],
        )

async def entrypoint(ctx: agents.JobContext):
    # 1. Define the Session with the specific OpenAI/Deepgram/Cartesia stack
    session = AgentSession(
        stt="elevenlabs/scribe_v2_realtime:en",
        llm=inference.LLM(
        model="google/gemini-2.5-flash-lite",
        extra_kwargs={
            "max_tokens": 65536   # ⚠️ Gemini uses this (not max_completion_tokens)
        }),

       tts=inference.TTS(
        model="elevenlabs/eleven_turbo_v2_5", 
        voice="Xb7hH8MSUJpSbSDYk0k2", 
        language="en"
            ),
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel(),
        ),
    )

    # 2. Setup MCP Server
    mcp_server = MCPServerSse(
        params={"url": os.environ.get("N8N_MCP_SERVER_URL")},
        cache_tools_list=True,
        name="SSE MCP Server"
    )

    # 3. Create Agent with MCP Tools integrated
    agent = await MCPToolsIntegration.create_agent_with_tools(
        agent_class=Assistant,
        mcp_servers=[mcp_server]
    )

    # 4. Setup Avatario/Tavus
    avatar = avatario.AvatarSession(
        avatar_id=os.environ.get("AVATARIO_ID"),
    )

    try:
        print("Starting Tavus avatar...")
        # Note: Ensure the avatario plugin version supports this session/room handoff
        await avatar.start(session, room=ctx.room)
        print("✅ Tavus avatar started")
    except Exception as e:
        print("❌ Tavus error:", e)

    # 5. Start the session with Noise Cancellation logic
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            # Logic for SIP vs Standard Web participants
            noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                else noise_cancellation.BVC(),
        ),
    )

    # 6. Connect to the room
    await ctx.connect()

    # 7. Initial Greeting
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )