"""
MarketAI Suite — Segmentation Service
=======================================
"""

from __future__ import annotations

from services.groq_service import groq_service
from prompts.segmentation_prompts import SEGMENTATION_SYSTEM_PROMPT, build_segmentation_prompt
from models.schemas import HistoryRepository, SegmentRepository
from utils.helpers import truncate
from utils.logger import get_logger

log = get_logger("segmentation_service")


class SegmentationService:

    def generate(self, inputs: dict) -> dict:
        system_prompt = SEGMENTATION_SYSTEM_PROMPT
        user_prompt = build_segmentation_prompt(inputs)

        log.info("Generating segmentation for business='%s'", inputs.get("business_description", "")[:50])

        ai_output = groq_service.generate_json(
            system_prompt,
            user_prompt,
            required_keys=["segments", "total_segments"],
            max_tokens=4096,
            temperature=0.7,
        )

        segments = ai_output.get("segments", [])
        title = f"Segments: {truncate(inputs.get('business_description', 'Segmentation'), 60)}"

        history_record = HistoryRepository.create(
            generation_type="segmentation",
            title=title,
            user_inputs=inputs,
            ai_output=ai_output,
            metadata={"segment_count": len(segments)},
        )

        SegmentRepository.create(
            history_id=history_record["id"],
            inputs=inputs,
            ai_output=ai_output,
        )

        return {
            "history_id": history_record["id"],
            "segmentation": ai_output,
            "loaded_from_history": False,
        }


segmentation_service = SegmentationService()
