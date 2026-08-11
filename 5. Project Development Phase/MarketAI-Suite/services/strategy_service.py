"""
MarketAI Suite — Strategy Service
===================================
"""

from __future__ import annotations

from services.groq_service import groq_service
from prompts.strategy_prompts import STRATEGY_SYSTEM_PROMPT, build_strategy_prompt
from models.schemas import HistoryRepository, StrategyRepository
from utils.helpers import truncate
from utils.logger import get_logger

log = get_logger("strategy_service")


class StrategyService:

    def generate(self, inputs: dict) -> dict:
        system_prompt = STRATEGY_SYSTEM_PROMPT
        user_prompt = build_strategy_prompt(inputs)

        log.info("Generating strategy for business='%s'", inputs.get("business_name"))

        ai_output = groq_service.generate_json(
            system_prompt,
            user_prompt,
            required_keys=["strategy_title", "market_positioning", "channel_strategy"],
            max_tokens=4096,
            temperature=0.65,
        )

        title = f"Strategy: {truncate(inputs.get('business_name', 'Marketing Strategy'), 60)}"

        history_record = HistoryRepository.create(
            generation_type="strategy",
            title=title,
            user_inputs=inputs,
            ai_output=ai_output,
            metadata={
                "business_name": inputs.get("business_name", ""),
                "industry": inputs.get("industry", ""),
            },
        )

        StrategyRepository.create(
            history_id=history_record["id"],
            inputs=inputs,
            ai_output=ai_output,
        )

        return {
            "history_id": history_record["id"],
            "strategy": ai_output,
            "loaded_from_history": False,
        }


strategy_service = StrategyService()
