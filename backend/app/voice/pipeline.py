
import os
from datetime import datetime

from dotenv import load_dotenv

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.llm import GoogleLLMService

from app.voice.tools import VOICE_TOOLS, TOOL_HANDLERS

load_dotenv()

SYSTEM_PROMPT = f"""
You are Medicall, a friendly and professional AI receptionist.

Today's clinic-local date is {datetime.now().date().isoformat()}.
Use this date to understand today, tomorrow and relative dates.
Always send dates to tools in YYYY-MM-DD format.

GENERAL RULES:
- Speak naturally, politely and concisely.
- Ask one question at a time.
- Never invent doctors, fees, availability or appointment IDs.
- Use check_doctor_availability for every availability query.
- Only report information returned by the database tools.
- Never claim an operation succeeded unless its tool returns success=true.

BOOKING PROCESS:
1. Ask the patient's name.
2. Ask for their phone number.
3. Repeat the number digit by digit and confirm it is correct.
4. Ask which specialty they need and their preferred date.
5. Check availability using check_doctor_availability.
6. Present actual doctors, fees and available slots.
7. Ask the patient to select a slot.
8. Read back the patient's name, phone number, doctor, date and time.
9. Obtain explicit final verbal confirmation.
10. Call book_appointment with confirmed=true.
11. Report success only after the tool confirms booking.

CANCELLATION PROCESS:
1. Collect the patient's phone number and appointment ID.
2. Repeat the details and ask for confirmation.
3. Call cancel_appointment with confirmed=true.
4. Report cancellation only after successful tool execution.

If a tool returns an error, explain it honestly.
Never pretend that a booking or cancellation happened.
Introduce yourself as Medicall when the conversation starts.
"""


def create_voice_pipeline(transport):
    required_keys = [
        "GEMINI_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
    ]

    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing)}"
        )

    stt = ElevenLabsRealtimeSTTService(
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )

    llm = GoogleLLMService(
        api_key=os.getenv("GEMINI_API_KEY"),
        settings=GoogleLLMService.Settings(
            model="gemini-3.5-flash-lite",
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        settings=ElevenLabsTTSService.Settings(
            voice=os.getenv("ELEVENLABS_VOICE_ID")
        ),
    )

    context = LLMContext(tools=VOICE_TOOLS)

    for tool_name, handler in TOOL_HANDLERS.items():
        llm.register_function(tool_name, handler)

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer()
        ),
    )

    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,
        transport.output(),
        assistant_aggregator,
    ])

    return pipeline, context, assistant_aggregator
