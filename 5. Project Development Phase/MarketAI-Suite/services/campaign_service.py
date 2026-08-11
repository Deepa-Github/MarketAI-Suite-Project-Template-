"""
MarketAI Suite — Campaign Service
==================================
Orchestrates campaign generation, storage, and retrieval.
"""

from __future__ import annotations

from services.groq_service import groq_service, GroqServiceError
from prompts.campaign_prompts import CAMPAIGN_SYSTEM_PROMPT, build_campaign_prompt
from models.schemas import HistoryRepository, CampaignRepository
from utils.helpers import truncate
from utils.logger import get_logger

log = get_logger("campaign_service")


class CampaignService:

    def generate(self, inputs: dict) -> dict:
        """
        Generate a marketing campaign via Groq and persist it.

        Returns the complete record including history_id and ai_output.
        """
        system_prompt = CAMPAIGN_SYSTEM_PROMPT
        user_prompt = build_campaign_prompt(inputs)

        log.info("Generating campaign for product='%s'", inputs.get("product_name"))

        ai_output = groq_service.generate_json(
            system_prompt,
            user_prompt,
            required_keys=["campaign_name", "value_proposition", "slogans"],
            max_tokens=4096,
            temperature=0.75,
        )

        # Build a descriptive title for history
        campaign_name = ai_output.get("campaign_name", inputs.get("product_name", "Campaign"))
        title = f"Campaign: {truncate(campaign_name, 80)}"

        # Save to history
        history_record = HistoryRepository.create(
            generation_type="campaign",
            title=title,
            user_inputs=inputs,
            ai_output=ai_output,
            metadata={
                "product_name": inputs.get("product_name", ""),
                "channels": inputs.get("channels", []),
            },
        )

        # Save to campaigns table
        CampaignRepository.create(
            history_id=history_record["id"],
            inputs=inputs,
            ai_output=ai_output,
        )

        return {
            "history_id": history_record["id"],
            "campaign": ai_output,
            "loaded_from_history": False,
        }

    def get_all(self) -> list[dict]:
        return HistoryRepository.list_all(generation_type="campaign")["items"]


campaign_service = CampaignService()
