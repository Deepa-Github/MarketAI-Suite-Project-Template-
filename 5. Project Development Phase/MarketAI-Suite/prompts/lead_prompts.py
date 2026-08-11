"""
MarketAI Suite — Lead Scoring Prompt Templates
===============================================
"""

from __future__ import annotations


LEAD_SCORING_SYSTEM_PROMPT = """You are an expert B2B/B2C sales operations analyst specialising in lead qualification, scoring, and prioritisation.

Your role is to analyse individual lead data and produce an AI-estimated lead assessment.

IMPORTANT DISCLAIMERS YOU MUST FOLLOW:
1. All scores and probability estimates are AI estimates based on the provided data — NOT statistically validated predictions.
2. Label all conversion estimates as "AI Estimated Conversion Probability".
3. Be specific about WHY a lead receives its score — reference the actual data provided.
4. Do not invent data not present in the lead record.
5. If key data is missing (e.g., no engagement data), flag this as a data gap.
6. Return ONLY valid JSON."""


def build_lead_scoring_prompt(lead_data: dict) -> str:
    """Build scoring prompt for a single lead."""
    name = lead_data.get("name", "Unknown")
    company = lead_data.get("company", "Unknown")
    industry = lead_data.get("industry", "Not provided")
    role = lead_data.get("job_title", lead_data.get("role", "Not provided"))
    company_size = lead_data.get("company_size", "Not provided")
    location = lead_data.get("location", "Not provided")
    email = lead_data.get("email", "Not provided")
    engagement = lead_data.get("engagement_score", lead_data.get("engagement", "Not provided"))
    website_visits = lead_data.get("website_visits", "Not provided")
    email_opens = lead_data.get("email_opens", "Not provided")
    email_clicks = lead_data.get("email_clicks", "Not provided")
    downloads = lead_data.get("content_downloads", lead_data.get("downloads", "Not provided"))
    demo_request = lead_data.get("demo_request", "Not provided")
    purchase_intent = lead_data.get("purchase_intent", "Not provided")
    prev_purchases = lead_data.get("previous_purchases", "Not provided")
    budget = lead_data.get("budget", "Not provided")
    lead_source = lead_data.get("lead_source", "Not provided")
    campaign = lead_data.get("campaign", "Not provided")

    return f"""Analyse the following lead record and produce an AI-estimated lead score and priority assessment.

═══════════════════════════════════════════
LEAD RECORD
═══════════════════════════════════════════
Name: {name}
Company: {company}
Industry: {industry}
Job Title / Role: {role}
Company Size: {company_size}
Location: {location}
Email: {email}

ENGAGEMENT DATA:
Overall Engagement Score: {engagement}
Website Visits: {website_visits}
Email Opens: {email_opens}
Email Clicks: {email_clicks}
Content Downloads: {downloads}
Demo Request: {demo_request}

INTENT SIGNALS:
Purchase Intent: {purchase_intent}
Previous Purchases: {prev_purchases}
Budget: {budget}
Lead Source: {lead_source}
Campaign: {campaign}

═══════════════════════════════════════════
SCORING INSTRUCTIONS
═══════════════════════════════════════════
Consider these factors when scoring:

HIGH POSITIVE SIGNALS: demo request, high purchase intent, high engagement, previous purchases, adequate budget, decision-maker role, relevant industry
HIGH NEGATIVE SIGNALS: no engagement data, no purchase intent, missing contact info, unknown company, irrelevant industry

Score 0-100 where:
- 80-100: Hot lead, immediate action needed
- 60-79: Warm lead, needs nurturing and prompt follow-up
- 40-59: Cool lead, requires qualification
- 0-39: Cold lead, low priority

═══════════════════════════════════════════
REQUIRED OUTPUT (strict JSON)
═══════════════════════════════════════════
{{
  "lead_score": <integer 0-100>,
  "priority": "<High|Medium|Low>",
  "ai_conversion_estimate": <float 0.0-1.0, AI estimate only>,
  "lead_quality": "<Excellent|Good|Fair|Poor>",
  "positive_signals": [
    "Specific positive signal from their data",
    "Another positive signal"
  ],
  "negative_signals": [
    "Specific risk or gap in their profile"
  ],
  "data_gaps": [
    "Missing data that would improve scoring accuracy"
  ],
  "score_reasoning": "2-3 sentence explanation referencing actual data points from this lead record",
  "recommended_action": "<specific action e.g. 'Schedule demo call within 24 hours'>",
  "recommended_channel": "<Email|Phone|LinkedIn|Direct Mail|SMS>",
  "follow_up_timing": "<Immediate|Within 24 hours|Within 3 days|Within 1 week|Monthly nurture>",
  "recommended_message_angle": "The key value message that will resonate with this specific lead"
}}"""


def build_batch_scoring_summary_prompt(scored_leads: list[dict]) -> str:
    """Build a prompt for generating insights across a batch of scored leads."""
    total = len(scored_leads)
    high = sum(1 for l in scored_leads if l.get("priority") == "High")
    medium = sum(1 for l in scored_leads if l.get("priority") == "Medium")
    low = sum(1 for l in scored_leads if l.get("priority") == "Low")
    avg_score = sum(l.get("lead_score", 0) for l in scored_leads) / total if total > 0 else 0

    # Top industries
    industries: dict[str, int] = {}
    for lead in scored_leads:
        ind = lead.get("industry", "Unknown")
        industries[ind] = industries.get(ind, 0) + 1

    top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]

    return f"""Based on the analysis of {total} scored leads, provide strategic insights and recommendations.

BATCH STATISTICS:
Total Leads: {total}
High Priority: {high}
Medium Priority: {medium}
Low Priority: {low}
Average AI Score: {avg_score:.1f}/100
Top Industries: {', '.join(f"{ind}({cnt})" for ind, cnt in top_industries)}

Return a JSON object:
{{
  "key_insights": ["Insight about this lead batch", "Another pattern observed"],
  "immediate_actions": ["Action 1 for high-priority leads", "Action 2"],
  "nurture_strategy": "Recommended nurture approach for medium-priority leads",
  "disqualification_criteria": "Criteria that would move a lead to low priority",
  "campaign_recommendations": ["Recommendation based on lead composition"],
  "data_quality_notes": "Overall data quality assessment"
}}"""
