
import logging

from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.worker import (
    PipelineParams,
    PipelineWorker,
    ProcessorUnusablePolicy,
)
from pipecat.runner.types import RunnerArguments
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.workers.runner import WorkerRunner
from pipecat.runner.run import main

from app.voice.pipeline import create_voice_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medicall")


async def bot(runner_args: RunnerArguments):
    connection: SmallWebRTCConnection = runner_args.webrtc_connection

    transport = SmallWebRTCTransport(
        webrtc_connection=connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    )

    pipeline, context, assistant_aggregator = (
        create_voice_pipeline(transport)
    )

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        processor_unusable_policy=ProcessorUnusablePolicy.END,
    )

    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint
    )

    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Patient connected to Medicall")

        context.add_message({
            "role": "user",
            "content": "Hello, please introduce yourself as Medicall."
        })

        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Patient disconnected")
        await runner.cancel()

    await runner.run()


if __name__ == "__main__":
    main()
