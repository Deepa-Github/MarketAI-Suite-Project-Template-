"""
MarketAI Suite — Sales Pitch Service
=====================================
"""

from __future__ import annotations

from services.groq_service import groq_service
from prompts.sales_prompts import SALES_PITCH_SYSTEM_PROMPT, build_sales_pitch_prompt
from models.schemas import HistoryRepository, SalesPitchRepository
from utils.helpers import truncate
from utils.logger import get_logger

log = get_logger("sales_pitch_service")


class SalesPitchService:

    def generate(self, inputs: dict) -> dict:
        system_prompt = SALES_PITCH_SYSTEM_PROMPT
        user_prompt = build_sales_pitch_prompt(inputs)

        log.info(
            "Generating sales pitch for product='%s' customer='%s'",
            inputs.get("product_name"),
            inputs.get("customer_name"),
        )

        ai_output = groq_service.generate_json(
            system_prompt,
            user_prompt,
            required_keys=["executive_summary", "value_proposition", "elevator_pitch"],
            max_tokens=4096,
            temperature=0.7,
        )

        title = (
            f"Sales Pitch: {truncate(inputs.get('product_name',''), 40)} "
            f"→ {truncate(inputs.get('customer_name',''), 40)}"
        )

        history_record = HistoryRepository.create(
            generation_type="sales_pitch",
            title=title,
            user_inputs=inputs,
            ai_output=ai_output,
            metadata={
                "product_name": inputs.get("product_name", ""),
                "customer_name": inputs.get("customer_name", ""),
                "customer_industry": inputs.get("customer_industry", ""),
            },
        )

        SalesPitchRepository.create(
            history_id=history_record["id"],
            inputs=inputs,
            ai_output=ai_output,
        )

        return {
            "history_id": history_record["id"],
            "pitch": ai_output,
            "loaded_from_history": False,
        }


sales_pitch_service = SalesPitchService()
