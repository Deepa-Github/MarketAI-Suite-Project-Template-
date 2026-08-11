"""
MarketAI Suite — Segmentation Prompt Templates
================================================
"""

from __future__ import annotations


SEGMENTATION_SYSTEM_PROMPT = """You are an expert customer intelligence analyst and audience segmentation specialist.

Your expertise covers:
- Psychographic, demographic, firmographic, and behavioural segmentation
- Customer persona development and Jobs-to-be-Done (JTBD) framework
- Market sizing and segment prioritisation
- Personalisation strategy by segment
- Channel and messaging optimisation for each segment

CRITICAL RULES:
1. Create specific, differentiated segments — not generic categories.
2. Each segment must have distinct characteristics, needs, and messaging angles.
3. Recommended offers and channels must differ meaningfully between segments.
4. Base personas on the provided data — do not invent unsupported demographic data.
5. Return ONLY valid JSON."""


def build_segmentation_prompt(inputs: dict) -> str:
    business_desc = inputs.get("business_description", "")
    target_market = inputs.get("target_market", "")
    demographics = inputs.get("demographics", "Not specified")
    age_range = inputs.get("age_range", "Not specified")
    location = inputs.get("location", "Not specified")
    industry = inputs.get("industry", "Not specified")
    job_roles = inputs.get("job_roles", "Not specified")
    company_size = inputs.get("company_size", "Not specified")
    purchase_history = inputs.get("purchase_history", "Not specified")
    interests = inputs.get("interests", "Not specified")
    engagement = inputs.get("engagement_behavior", "Not specified")
    pain_points = inputs.get("pain_points", "Not specified")
    product_usage = inputs.get("product_usage", "Not specified")
    purchase_intent = inputs.get("purchase_intent", "Not specified")

    return f"""Create a detailed audience segmentation analysis for the following business context.

═══════════════════════════════════════════
BUSINESS CONTEXT
═══════════════════════════════════════════
Business / Product Description: {business_desc}
Target Market: {target_market}

═══════════════════════════════════════════
AVAILABLE AUDIENCE DATA
═══════════════════════════════════════════
Demographics: {demographics}
Age Range: {age_range}
Location: {location}
Industry / Vertical: {industry}
Job Roles / Functions: {job_roles}
Company Size: {company_size}
Purchase History: {purchase_history}
Interests / Hobbies: {interests}
Engagement Behaviour: {engagement}
Key Pain Points: {pain_points}
Product Usage Patterns: {product_usage}
Purchase Intent Signals: {purchase_intent}

═══════════════════════════════════════════
REQUIRED OUTPUT (strict JSON)
═══════════════════════════════════════════
{{
  "segmentation_overview": "Brief description of the overall segmentation approach used",
  "total_segments": <number>,
  "segments": [
    {{
      "segment_id": 1,
      "segment_name": "Descriptive segment name (e.g. 'Enterprise Decision Makers')",
      "segment_size_estimate": "Estimated % of total audience this segment represents",
      "priority": "<High|Medium|Low>",
      "description": "2-3 sentence description of this audience segment",
      "demographics": {{
        "age_range": "Age range",
        "location": "Geographic focus",
        "income_level": "Income or budget range",
        "education": "Education level if relevant"
      }},
      "firmographics": {{
        "industry": "Industry or sector",
        "company_size": "Company size range",
        "job_function": "Job function or department",
        "seniority": "Seniority level"
      }},
      "psychographics": {{
        "values": ["Core value 1", "Core value 2"],
        "lifestyle": "Lifestyle description",
        "personality_traits": ["Trait 1", "Trait 2"],
        "decision_style": "How they make purchase decisions"
      }},
      "needs": [
        "Primary need specific to this segment",
        "Secondary need"
      ],
      "pain_points": [
        "Key pain point 1",
        "Key pain point 2"
      ],
      "motivations": [
        "What motivates their purchase decision",
        "Secondary motivation"
      ],
      "buying_behavior": {{
        "buying_cycle_length": "How long they take to decide",
        "decision_factors": ["Factor 1", "Factor 2"],
        "typical_objections": ["Objection 1", "Objection 2"],
        "preferred_purchase_channels": ["Online", "Sales Rep", etc]
      }},
      "recommended_messaging": {{
        "headline": "Segment-specific headline",
        "key_message": "Primary message that resonates with this segment",
        "tone": "Tone of voice for this segment",
        "what_to_emphasise": ["Feature/benefit to emphasise 1", "Feature 2"],
        "what_to_avoid": ["Message angle that won't work for this segment"]
      }},
      "recommended_channels": [
        {{
          "channel": "Channel name",
          "reason": "Why this channel is effective for this segment",
          "content_type": "Best content format"
        }}
      ],
      "recommended_offers": [
        {{
          "offer_type": "Free trial / Discount / Demo / Case study etc",
          "offer_description": "Specific offer description",
          "objective": "What this offer achieves"
        }}
      ],
      "content_recommendations": [
        "Content topic/format recommendation 1",
        "Content recommendation 2"
      ],
      "engagement_triggers": [
        "What will trigger this segment to engage"
      ]
    }}
  ],
  "cross_segment_insights": [
    "Insight that applies across multiple segments"
  ],
  "prioritisation_recommendation": "Which segment(s) to focus on first and why",
  "assumptions": ["Any assumptions made about the audience"]
}}

Create 3-5 meaningful, distinct segments. Each segment must be genuinely different from the others."""
