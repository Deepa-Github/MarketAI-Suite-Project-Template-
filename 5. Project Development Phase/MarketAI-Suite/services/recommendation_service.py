"""
MarketAI Suite — Recommendation Service
=========================================
"""

from __future__ import annotations

from services.groq_service import groq_service
from prompts.strategy_prompts import RECOMMENDATION_SYSTEM_PROMPT, build_recommendation_prompt
from models.schemas import HistoryRepository, RecommendationRepository, LeadUploadRepository
from utils.logger import get_logger

log = get_logger("recommendation_service")


class RecommendationService:

    def generate(self, inputs: dict) -> dict:
        """Generate next best action recommendations."""

        # Enrich context with DB stats
        lead_stats = LeadUploadRepository.get_aggregate_stats()

        leads_summary = (
            f"Total scored leads: {lead_stats.get('total_leads', 0)}, "
            f"High priority: {lead_stats.get('high_priority', 0)}, "
            f"Medium: {lead_stats.get('medium_priority', 0)}, "
            f"Low: {lead_stats.get('low_priority', 0)}, "
            f"Average score: {lead_stats.get('avg_score', 0):.1f}/100"
        )

        enriched_inputs = {
            **inputs,
            "leads_summary": leads_summary,
        }

        system_prompt = RECOMMENDATION_SYSTEM_PROMPT
        user_prompt = build_recommendation_prompt(enriched_inputs)

        log.info("Generating recommendations")

        ai_output = groq_service.generate_json(
            system_prompt,
            user_prompt,
            required_keys=["priority_actions"],
            max_tokens=2000,
            temperature=0.6,
        )

        context_summary = inputs.get("context", "General marketing context")
        title = f"Recommendations: {context_summary[:60]}"

        history_record = HistoryRepository.create(
            generation_type="recommendation",
            title=title,
            user_inputs=inputs,
            ai_output=ai_output,
            metadata={"action_count": len(ai_output.get("priority_actions", []))},
        )

        RecommendationRepository.create(
            history_id=history_record["id"],
            context_summary=context_summary,
            ai_output=ai_output,
        )

        return {
            "history_id": history_record["id"],
            "recommendations": ai_output,
            "loaded_from_history": False,
        }


recommendation_service = RecommendationService()
