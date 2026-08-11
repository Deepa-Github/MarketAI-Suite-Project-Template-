"""
MarketAI Suite — Lead Scoring Service
=======================================
Handles both manual lead entry and CSV batch upload.
Uses deterministic pre-scoring + AI contextual analysis.
"""

from __future__ import annotations

import io
import math
from typing import Any

import pandas as pd

from services.groq_service import groq_service
from prompts.lead_prompts import (
    LEAD_SCORING_SYSTEM_PROMPT,
    build_lead_scoring_prompt,
    build_batch_scoring_summary_prompt,
)
from models.schemas import HistoryRepository, LeadUploadRepository
from utils.logger import get_logger

log = get_logger("lead_scoring_service")

# ──────────────────────────────────────────────────────────────
# Deterministic scoring weights
# ──────────────────────────────────────────────────────────────

DETERMINISTIC_WEIGHTS = {
    "demo_request": 20,
    "purchase_intent_high": 15,
    "engagement_high": 12,
    "budget_provided": 10,
    "previous_purchases": 10,
    "email_clicks": 8,
    "content_downloads": 7,
    "email_opens": 5,
    "website_visits": 5,
    "company_provided": 3,
    "role_decision_maker": 5,
}

DECISION_MAKER_KEYWORDS = {
    "ceo", "cto", "cmo", "coo", "cfo", "vp", "vice president",
    "director", "head of", "chief", "president", "founder", "owner",
    "manager", "svp", "evp",
}


def _deterministic_score(lead: dict) -> tuple[int, list[str], list[str]]:
    """
    Calculate a deterministic base score (0-60) for a lead
    based on engagement and intent signals.

    Returns (score, positive_signals, negative_signals)
    """
    score = 0
    positive: list[str] = []
    negative: list[str] = []

    # Demo request
    demo = str(lead.get("demo_request", "")).lower()
    if demo in ("yes", "true", "1", "requested"):
        score += DETERMINISTIC_WEIGHTS["demo_request"]
        positive.append("Demo requested — strong intent signal")

    # Purchase intent
    intent = str(lead.get("purchase_intent", "")).lower()
    if intent in ("high", "very high", "strong"):
        score += DETERMINISTIC_WEIGHTS["purchase_intent_high"]
        positive.append(f"High purchase intent ({intent})")
    elif intent in ("medium", "moderate"):
        score += 7
        positive.append(f"Moderate purchase intent ({intent})")
    elif intent in ("low", "none", ""):
        negative.append("Low or unspecified purchase intent")

    # Engagement score
    try:
        eng = float(lead.get("engagement_score", lead.get("engagement", 0)) or 0)
        if eng >= 70:
            score += DETERMINISTIC_WEIGHTS["engagement_high"]
            positive.append(f"High engagement score ({eng:.0f})")
        elif eng >= 40:
            score += 6
            positive.append(f"Moderate engagement score ({eng:.0f})")
        elif eng > 0:
            score += 2
        else:
            negative.append("No engagement score recorded")
    except (TypeError, ValueError):
        negative.append("Engagement score not numeric")

    # Budget
    budget = str(lead.get("budget", "")).strip()
    if budget and budget.lower() not in ("not provided", "unknown", "n/a", ""):
        score += DETERMINISTIC_WEIGHTS["budget_provided"]
        positive.append(f"Budget information available ({budget})")
    else:
        negative.append("Budget not provided — qualification needed")

    # Previous purchases
    prev = str(lead.get("previous_purchases", "")).lower()
    if prev not in ("", "no", "none", "0", "false"):
        score += DETERMINISTIC_WEIGHTS["previous_purchases"]
        positive.append("Has previous purchase history")

    # Email engagement
    try:
        clicks = int(lead.get("email_clicks", 0) or 0)
        if clicks >= 3:
            score += DETERMINISTIC_WEIGHTS["email_clicks"]
            positive.append(f"Multiple email clicks ({clicks})")
        elif clicks > 0:
            score += 3
    except (TypeError, ValueError):
        pass

    # Content downloads
    try:
        downloads = int(lead.get("content_downloads", lead.get("downloads", 0)) or 0)
        if downloads >= 2:
            score += DETERMINISTIC_WEIGHTS["content_downloads"]
            positive.append(f"Content downloads ({downloads}) — research behaviour")
        elif downloads > 0:
            score += 3
    except (TypeError, ValueError):
        pass

    # Email opens
    try:
        opens = int(lead.get("email_opens", 0) or 0)
        if opens >= 3:
            score += DETERMINISTIC_WEIGHTS["email_opens"]
            positive.append(f"Multiple email opens ({opens})")
    except (TypeError, ValueError):
        pass

    # Website visits
    try:
        visits = int(lead.get("website_visits", 0) or 0)
        if visits >= 5:
            score += DETERMINISTIC_WEIGHTS["website_visits"]
            positive.append(f"Repeated website visits ({visits})")
        elif visits >= 2:
            score += 2
    except (TypeError, ValueError):
        pass

    # Company info
    if lead.get("company", "").strip():
        score += DETERMINISTIC_WEIGHTS["company_provided"]
        positive.append("Company information provided")
    else:
        negative.append("Company name not provided")

    # Decision maker role
    role = str(lead.get("job_title", lead.get("role", ""))).lower()
    if any(kw in role for kw in DECISION_MAKER_KEYWORDS):
        score += DETERMINISTIC_WEIGHTS["role_decision_maker"]
        positive.append(f"Decision-maker role ({role.title()})")

    return min(score, 60), positive, negative  # cap at 60 for deterministic portion


def _priority_from_score(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def _estimate_conversion(score: int) -> float:
    """Map score 0-100 to a rough conversion probability estimate."""
    # Logistic-style mapping
    return round(1 / (1 + math.exp(-0.07 * (score - 50))), 2)


class LeadScoringService:

    def score_single_lead(self, lead_data: dict) -> dict:
        """
        Score a single lead using deterministic rules + AI contextual analysis.
        """
        det_score, pos_signals, neg_signals = _deterministic_score(lead_data)

        # AI contextual analysis adds up to 40 points of nuance
        user_prompt = build_lead_scoring_prompt(lead_data)

        try:
            ai_result = groq_service.generate_json(
                LEAD_SCORING_SYSTEM_PROMPT,
                user_prompt,
                required_keys=["lead_score", "priority", "score_reasoning"],
                max_tokens=800,
                temperature=0.3,
            )

            # Blend: deterministic base (60%) + AI refinement (40%)
            ai_score = max(0, min(100, int(ai_result.get("lead_score", 50))))
            final_score = round((det_score / 60) * 60 + (ai_score / 100) * 40)
            final_score = max(0, min(100, final_score))

            # Merge signals
            ai_pos = ai_result.get("positive_signals", [])
            ai_neg = ai_result.get("negative_signals", [])
            all_positive = list(dict.fromkeys(pos_signals + ai_pos))[:6]
            all_negative = list(dict.fromkeys(neg_signals + ai_neg))[:4]

            return {
                "lead_score": final_score,
                "priority": _priority_from_score(final_score),
                "ai_conversion_estimate": _estimate_conversion(final_score),
                "lead_quality": ai_result.get("lead_quality", "Fair"),
                "positive_signals": all_positive,
                "negative_signals": all_negative,
                "score_reasoning": ai_result.get("score_reasoning", ""),
                "recommended_action": ai_result.get("recommended_action", "Follow up"),
                "recommended_channel": ai_result.get("recommended_channel", "Email"),
                "follow_up_timing": ai_result.get("follow_up_timing", "Within 3 days"),
                "recommended_message_angle": ai_result.get("recommended_message_angle", ""),
                "scoring_method": "Deterministic + AI",
            }

        except Exception as exc:
            # Fallback to deterministic-only if AI fails
            log.warning("AI scoring failed for lead '%s', using deterministic only: %s",
                        lead_data.get("name"), exc)
            det_score_full = round((det_score / 60) * 100)
            return {
                "lead_score": det_score_full,
                "priority": _priority_from_score(det_score_full),
                "ai_conversion_estimate": _estimate_conversion(det_score_full),
                "lead_quality": "Fair",
                "positive_signals": pos_signals,
                "negative_signals": neg_signals,
                "score_reasoning": f"Deterministic scoring only (AI unavailable): {', '.join(pos_signals[:3])}",
                "recommended_action": "Review and qualify this lead",
                "recommended_channel": "Email",
                "follow_up_timing": "Within 3 days",
                "recommended_message_angle": "",
                "scoring_method": "Deterministic only",
            }

    def process_csv(self, file_bytes: bytes, filename: str) -> dict:
        """
        Process a CSV file of leads.
        Returns scored leads, summary stats, and saves to DB.
        For large files, scores a sample via AI and applies rule-based scoring for the rest.
        """
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as exc:
            raise ValueError(f"Could not parse CSV file: {exc}") from exc

        # Normalise column names: lowercase, strip spaces
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        total_leads = len(df)
        log.info("Processing CSV: filename=%s total_leads=%d", filename, total_leads)

        scored_leads = []
        # For large datasets, limit AI calls; use deterministic for all, AI for sample
        ai_limit = min(total_leads, 50)  # AI-score at most 50 leads to manage costs

        leads_list = df.where(pd.notnull(df), None).to_dict(orient="records")

        for i, lead in enumerate(leads_list):
            # Clean up None values
            clean_lead = {k: (v if v is not None else "") for k, v in lead.items()}
            if i < ai_limit:
                scored = self.score_single_lead(clean_lead)
            else:
                # Deterministic-only for large batches beyond AI limit
                det_score, pos, neg = _deterministic_score(clean_lead)
                det_final = round((det_score / 60) * 100)
                scored = {
                    "lead_score": det_final,
                    "priority": _priority_from_score(det_final),
                    "ai_conversion_estimate": _estimate_conversion(det_final),
                    "lead_quality": "Fair",
                    "positive_signals": pos[:3],
                    "negative_signals": neg[:2],
                    "score_reasoning": "Rule-based scoring (large batch)",
                    "recommended_action": "Review and qualify",
                    "recommended_channel": "Email",
                    "follow_up_timing": "Within 1 week",
                    "recommended_message_angle": "",
                    "scoring_method": "Deterministic only",
                }
            # Merge original lead data with score
            result = {**clean_lead, **scored}
            scored_leads.append(result)

        # Sort by score descending
        scored_leads.sort(key=lambda x: x.get("lead_score", 0), reverse=True)

        # Summary stats
        high = [l for l in scored_leads if l.get("priority") == "High"]
        medium = [l for l in scored_leads if l.get("priority") == "Medium"]
        low = [l for l in scored_leads if l.get("priority") == "Low"]
        avg_score = sum(l.get("lead_score", 0) for l in scored_leads) / total_leads if total_leads > 0 else 0

        summary = {
            "total_leads": total_leads,
            "high_priority": len(high),
            "medium_priority": len(medium),
            "low_priority": len(low),
            "avg_score": round(avg_score, 1),
            "ai_scored_count": min(ai_limit, total_leads),
        }

        # Generate batch insights
        batch_insights = {}
        try:
            insight_prompt = build_batch_scoring_summary_prompt(scored_leads[:50])
            batch_insights = groq_service.generate_json(
                LEAD_SCORING_SYSTEM_PROMPT,
                insight_prompt,
                max_tokens=600,
                temperature=0.4,
            )
        except Exception as exc:
            log.warning("Batch insight generation failed: %s", exc)

        title = f"Lead Analysis: {filename} ({total_leads} leads)"
        history_record = HistoryRepository.create(
            generation_type="lead_scoring",
            title=title,
            user_inputs={"filename": filename, "total_leads": total_leads},
            ai_output={"scored_leads": scored_leads, "batch_insights": batch_insights},
            metadata=summary,
        )

        LeadUploadRepository.create(
            history_id=history_record["id"],
            filename=filename,
            summary=summary,
            scored_leads=scored_leads,
        )

        return {
            "history_id": history_record["id"],
            "summary": summary,
            "scored_leads": scored_leads,
            "batch_insights": batch_insights,
            "loaded_from_history": False,
        }

    def score_manual_lead(self, lead_data: dict) -> dict:
        """Score a single manually entered lead and save to history."""
        scored = self.score_single_lead(lead_data)

        title = f"Lead Score: {lead_data.get('name', 'Unknown')} @ {lead_data.get('company', '')}"
        history_record = HistoryRepository.create(
            generation_type="lead_scoring",
            title=title,
            user_inputs=lead_data,
            ai_output={**lead_data, **scored},
            metadata={"scoring_method": scored.get("scoring_method", "")},
        )

        return {
            "history_id": history_record["id"],
            "lead": {**lead_data, **scored},
            "loaded_from_history": False,
        }


lead_scoring_service = LeadScoringService()
