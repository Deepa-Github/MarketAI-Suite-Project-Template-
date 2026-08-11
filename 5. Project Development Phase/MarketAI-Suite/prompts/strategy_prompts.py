"""
MarketAI Suite — Marketing Strategy Prompt Templates
=====================================================
"""

from __future__ import annotations


STRATEGY_SYSTEM_PROMPT = """You are a Chief Marketing Officer (CMO) and senior marketing strategist with expertise in:
- Go-to-market strategy and market positioning
- Full-funnel marketing strategy (acquisition, activation, retention, referral, revenue)
- Competitive analysis and strategic differentiation
- Marketing mix optimisation and budget allocation
- Growth strategy and customer lifetime value maximisation

CRITICAL RULES:
1. Strategy must be specific to the business, industry, and objectives provided.
2. Avoid generic strategic frameworks presented without customisation.
3. Every recommendation must include a clear rationale tied to the business context.
4. Budget allocation percentages should add up to 100%.
5. Risks must be genuine and actionable — not generic warnings.
6. Return ONLY valid JSON."""


def build_strategy_prompt(inputs: dict) -> str:
    business_name = inputs.get("business_name", "")
    industry = inputs.get("industry", "")
    target_market = inputs.get("target_market", "")
    objective = inputs.get("marketing_objective", "")
    business_goals = inputs.get("business_goals", "Not specified")
    competitors = inputs.get("competitors", "Not specified")
    budget = inputs.get("budget", "Not specified")
    channels = inputs.get("channels", "Not specified")
    pain_points = inputs.get("customer_pain_points", "Not specified")
    current_situation = inputs.get("current_situation", "Not specified")
    usp = inputs.get("unique_selling_points", "Not specified")
    timeframe = inputs.get("timeframe", "12 months")

    channels_str = ", ".join(channels) if isinstance(channels, list) else str(channels)

    return f"""Develop a comprehensive marketing strategy for the following business.

═══════════════════════════════════════════
BUSINESS CONTEXT
═══════════════════════════════════════════
Business / Product: {business_name}
Industry: {industry}
Target Market: {target_market}
Unique Selling Points: {usp}
Current Situation: {current_situation}

═══════════════════════════════════════════
STRATEGIC PARAMETERS
═══════════════════════════════════════════
Marketing Objective: {objective}
Business Goals: {business_goals}
Key Competitors: {competitors}
Marketing Budget: {budget}
Preferred Channels: {channels_str}
Customer Pain Points: {pain_points}
Strategy Timeframe: {timeframe}

═══════════════════════════════════════════
REQUIRED OUTPUT (strict JSON)
═══════════════════════════════════════════
{{
  "strategy_title": "Strategy title for {business_name}",
  "executive_summary": "2-3 sentence strategic summary",
  "market_analysis": {{
    "market_opportunity": "Assessment of the market opportunity",
    "target_market_size": "Estimated market size or TAM/SAM/SOM if inferable",
    "market_trends": ["Relevant trend 1", "Relevant trend 2", "Relevant trend 3"],
    "competitive_landscape": "Assessment of the competitive environment"
  }},
  "market_positioning": {{
    "positioning_statement": "Brand positioning statement",
    "differentiators": ["Key differentiator 1", "Key differentiator 2"],
    "brand_promise": "The promise made to customers",
    "positioning_vs_competitors": "How to position against {competitors}"
  }},
  "marketing_objectives": [
    {{
      "objective": "SMART marketing objective",
      "metric": "How it will be measured",
      "target": "Specific target (number or %)",
      "timeline": "By when"
    }}
  ],
  "audience_strategy": {{
    "primary_audience": "Description of primary target audience",
    "secondary_audience": "Description of secondary audience",
    "audience_insights": ["Key insight about the audience", "Another insight"],
    "audience_approach": "How to reach and engage them"
  }},
  "messaging_strategy": {{
    "core_message": "The single most important message",
    "message_pillars": [
      {{
        "pillar": "Message pillar name",
        "message": "Core message for this pillar",
        "proof_points": ["Supporting evidence", "Data point or claim"]
      }}
    ],
    "tone_of_voice": "Recommended tone for {business_name}",
    "content_themes": ["Theme 1", "Theme 2", "Theme 3"]
  }},
  "channel_strategy": [
    {{
      "channel": "Channel name",
      "role": "Awareness|Consideration|Conversion|Retention",
      "budget_allocation_pct": 0,
      "tactics": ["Specific tactic 1", "Specific tactic 2"],
      "kpi": "Primary KPI for this channel",
      "rationale": "Why this channel for this audience"
    }}
  ],
  "content_strategy": {{
    "content_pillars": ["Pillar 1", "Pillar 2", "Pillar 3"],
    "content_formats": ["Format 1", "Format 2"],
    "publishing_cadence": "Recommended publishing frequency per channel",
    "thought_leadership_topics": ["Topic 1", "Topic 2"]
  }},
  "customer_acquisition_strategy": {{
    "acquisition_channels": ["Primary channel 1", "Channel 2"],
    "lead_generation_tactics": ["Tactic 1", "Tactic 2"],
    "conversion_strategy": "How to convert leads to customers",
    "cac_target": "Target Customer Acquisition Cost (estimate or range)"
  }},
  "retention_strategy": {{
    "retention_tactics": ["Tactic 1", "Tactic 2"],
    "loyalty_program": "Recommendation for loyalty/retention program",
    "upsell_cross_sell": "Upsell/cross-sell strategy",
    "churn_reduction": "Approach to reducing churn"
  }},
  "campaign_strategy": {{
    "campaign_themes": ["Campaign idea 1", "Campaign idea 2"],
    "campaign_cadence": "Recommended campaign frequency",
    "hero_campaign_concept": "The flagship campaign concept"
  }},
  "kpis": [
    {{
      "kpi": "KPI name",
      "baseline": "Current baseline (if known)",
      "target": "Target value",
      "measurement_tool": "How to measure",
      "review_frequency": "Daily|Weekly|Monthly"
    }}
  ],
  "measurement_strategy": {{
    "reporting_cadence": "How often to review results",
    "attribution_model": "Recommended attribution model",
    "key_dashboards": ["Dashboard 1", "Dashboard 2"],
    "optimisation_triggers": ["Trigger that would prompt strategy adjustment"]
  }},
  "implementation_roadmap": [
    {{
      "phase": "Phase 1",
      "timeline": "Month 1-3",
      "focus": "Phase focus area",
      "key_actions": ["Action 1", "Action 2"],
      "milestones": ["Milestone 1"]
    }},
    {{
      "phase": "Phase 2",
      "timeline": "Month 4-8",
      "focus": "Phase focus area",
      "key_actions": ["Action 1", "Action 2"],
      "milestones": ["Milestone 1"]
    }},
    {{
      "phase": "Phase 3",
      "timeline": "Month 9-12",
      "focus": "Scale and optimise",
      "key_actions": ["Action 1", "Action 2"],
      "milestones": ["Milestone 1"]
    }}
  ],
  "risks": [
    {{
      "risk": "Specific risk",
      "likelihood": "High|Medium|Low",
      "impact": "High|Medium|Low",
      "mitigation": "Specific mitigation strategy"
    }}
  ],
  "optimization_recommendations": [
    "Specific, actionable optimisation recommendation"
  ],
  "quick_wins": [
    "Tactic that can deliver results within 30 days"
  ],
  "budget_allocation": {{
    "total_budget": "{budget}",
    "breakdown": [
      {{"category": "Category", "percentage": 0, "rationale": "Why"}}
    ]
  }},
  "assumptions": ["Any assumption made about the business"]
}}"""


RECOMMENDATION_SYSTEM_PROMPT = """You are an AI-powered revenue intelligence engine that analyses marketing and sales data to generate the next best actions for each lead or account.

Your recommendations must be:
1. Specific and actionable — not generic advice
2. Prioritised by urgency and expected impact
3. Channel-specific with recommended timing
4. Grounded in the data provided
5. Return ONLY valid JSON."""


def build_recommendation_prompt(inputs: dict) -> str:
    context = inputs.get("context", "")
    leads_summary = inputs.get("leads_summary", "")
    campaigns_summary = inputs.get("campaigns_summary", "")
    segments_summary = inputs.get("segments_summary", "")
    business_objective = inputs.get("business_objective", "Increase sales and revenue")

    return f"""Generate next best action recommendations based on the following marketing and sales context.

BUSINESS OBJECTIVE: {business_objective}

CONTEXT PROVIDED:
{context}

LEAD INTELLIGENCE:
{leads_summary}

CAMPAIGN PERFORMANCE:
{campaigns_summary}

AUDIENCE SEGMENTS:
{segments_summary}

Return a JSON object:
{{
  "priority_actions": [
    {{
      "action": "Specific action to take",
      "reason": "Why this action is recommended now",
      "priority": "Immediate|High|Medium|Low",
      "channel": "Email|Phone|LinkedIn|Retargeting|In-App|SMS",
      "timing": "When to execute",
      "expected_outcome": "What result this action should produce",
      "target_segment": "Who this applies to"
    }}
  ],
  "campaign_recommendations": [
    {{
      "recommendation": "Campaign recommendation",
      "rationale": "Business rationale",
      "expected_impact": "Expected result"
    }}
  ],
  "lead_actions": [
    {{
      "lead_segment": "High/Medium/Low priority leads",
      "recommended_action": "Specific action",
      "timing": "When",
      "message_angle": "What message to lead with"
    }}
  ],
  "quick_wins": [
    "Quick win that can be implemented immediately"
  ],
  "strategic_recommendations": [
    "Longer-term strategic recommendation"
  ],
  "expected_outcomes": {{
    "30_days": "Expected result in 30 days",
    "90_days": "Expected result in 90 days"
  }}
}}"""
