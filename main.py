#!/usr/bin/env python3
"""
AI BOX OFFICE FILM ENGINE - MAIN ORCHESTRATOR
=============================================
True Story | Love | Pain | Struggle | What's Next | Who We Are

Powered by:
  - OpenAI GPT-4.1 (o3 planner + script writer)
  - Grok xAI (Grok Imagine - cinematic video generation)
  - InVideo AI (full video production pipeline)
  - Webhook triggers (GitHub Actions / Flask)
  - Full multi-agent architecture
"""

import os
import json
import asyncio
import logging
from datetime import datetime

from agents.story_writer import StoryWriterAgent
from agents.grok_video import GrokVideoAgent
from agents.invideo_producer import InVideoProducerAgent
from agents.visual_director import VisualDirectorAgent
from agents.sound_composer import SoundComposerAgent
from webhook.server import WebhookServer
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BoxOfficeFilmEngine:
    """
    Master orchestrator that coordinates all AI agents
    to produce a breathtaking, heart-racing cinematic experience.
    """

    FILM_TITLE = "SIGNAL"
    FILM_TAGLINE = "A true story of love, pain, struggle - and the possibility of what's next."

    # Film acts structure
    ACTS = [
        {
            "act": 1,
            "title": "Who We Are",
            "emotion": "identity, origin, love",
            "visual_tone": "warm golden light, soft focus, dawn breaking",
            "music_tone": "intimate piano, rising strings",
        },
        {
            "act": 2,
            "title": "The Pain",
            "emotion": "loss, struggle, darkness",
            "visual_tone": "desaturated blues, harsh shadows, rain-soaked streets",
            "music_tone": "heavy bass, dissonant chords, silence",
        },
        {
            "act": 3,
            "title": "The Fight",
            "emotion": "resilience, courage, fire",
            "visual_tone": "high contrast, deep reds, slow-motion impact",
            "music_tone": "driving percussion, soaring brass",
        },
        {
            "act": 4,
            "title": "What's Next",
            "emotion": "hope, possibility, transcendence",
            "visual_tone": "4K ultra-wide, HDR, cosmic scale, sunrise over earth",
            "music_tone": "full orchestral swell, choir, electronic pulse",
        },
    ]

    def __init__(self):
        self.config = Config()
        self.story_agent = StoryWriterAgent(
            openai_api_key=self.config.OPENAI_API_KEY
        )
        self.grok_agent = GrokVideoAgent(
            grok_api_key=self.config.GROK_API_KEY
        )
        self.invideo_agent = InVideoProducerAgent(
            invideo_api_key=self.config.INVIDEO_API_KEY,
            openai_api_key=self.config.OPENAI_API_KEY,
        )
        self.visual_director = VisualDirectorAgent()
        self.sound_composer = SoundComposerAgent()
        self.webhook_server = WebhookServer(
            port=self.config.WEBHOOK_PORT,
            secret=self.config.WEBHOOK_SECRET,
        )
        self.output_dir = f"output/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)

    async def run(self):
        logger.info(f"=== {self.FILM_TITLE} :: AI Film Engine Starting ===")
        logger.info(self.FILM_TAGLINE)

        # Phase 1: Generate the full screenplay
        logger.info("[PHASE 1] Generating screenplay with OpenAI o3 + GPT-4.1...")
        screenplay = await self.story_agent.generate_screenplay(
            title=self.FILM_TITLE,
            tagline=self.FILM_TAGLINE,
            acts=self.ACTS,
            style="Christopher Nolan meets Terrence Malick - cinematic, poetic, visceral",
        )
        self._save_output("screenplay.json", screenplay)
        logger.info(f"Screenplay complete: {len(screenplay['scenes'])} scenes generated")

        # Phase 2: Generate visual shot prompts for each scene
        logger.info("[PHASE 2] Visual Director generating cinematic shot prompts...")
        shot_list = await self.visual_director.generate_shots(
            screenplay=screenplay,
            acts=self.ACTS,
        )
        self._save_output("shot_list.json", shot_list)

        # Phase 3: Generate video clips via Grok Imagine API
        logger.info("[PHASE 3] Grok xAI generating cinematic video clips (720p)...")
        video_clips = await self.grok_agent.generate_clips(
            shot_list=shot_list,
            resolution="720p",
            with_audio=True,
            output_dir=self.output_dir,
        )
        logger.info(f"Grok generated {len(video_clips)} video clips")

        # Phase 4: Compose soundtrack
        logger.info("[PHASE 4] Sound Composer building emotional soundtrack...")
        soundtrack = await self.sound_composer.compose(
            acts=self.ACTS,
            duration_seconds=sum(c.get('duration', 8) for c in video_clips),
        )
        self._save_output("soundtrack_manifest.json", soundtrack)

        # Phase 5: Full production via InVideo AI
        logger.info("[PHASE 5] InVideo AI assembling final film...")
        final_film = await self.invideo_agent.produce(
            screenplay=screenplay,
            video_clips=video_clips,
            soundtrack=soundtrack,
            title=self.FILM_TITLE,
            output_dir=self.output_dir,
        )

        logger.info("=" * 60)
        logger.info(f"FILM COMPLETE: {final_film['output_url']}")
        logger.info(f"Duration: {final_film['duration_seconds']}s")
        logger.info(f"Resolution: {final_film['resolution']}")
        logger.info("=" * 60)
        return final_film

    def _save_output(self, filename: str, data: dict):
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved: {path}")

    def start_webhook_listener(self):
        """Start webhook server to trigger film generation remotely."""
        self.webhook_server.on_trigger(self.run)
        self.webhook_server.start()


if __name__ == "__main__":
    engine = BoxOfficeFilmEngine()

    import sys
    if "--webhook" in sys.argv:
        # Start as webhook listener (GitHub Actions / external trigger)
        engine.start_webhook_listener()
    else:
        # Run immediately
        asyncio.run(engine.run())
