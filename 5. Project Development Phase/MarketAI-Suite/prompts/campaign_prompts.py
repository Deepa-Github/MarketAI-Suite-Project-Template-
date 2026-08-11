"""
MarketAI Suite — Campaign Prompt Templates
===========================================
Provides system + user prompts for the Marketing Campaign Generator.
"""

from __future__ import annotations


CAMPAIGN_SYSTEM_PROMPT = """You are an expert B2B/B2C marketing strategist and campaign planner with deep expertise in:
- Brand positioning and differentiation
- Multi-channel campaign design (social media, email, paid ads, content)
- Consumer psychology and buyer journey mapping
- Copywriting, content strategy, and persuasion
- KPI definition and marketing measurement

Your role is to create highly specific, actionable marketing campaigns tailored to the exact product, audience, and objectives provided.

CRITICAL RULES:
1. Base every recommendation on the information provided — do not invent company facts.
2. Clearly label any assumptions you make with "ASSUMPTION:" prefix.
3. Avoid generic, cookie-cutter marketing advice.
4. Make every slogan, caption, and recommendation specific to the product and audience.
5. Tailor tone and messaging to the specified brand tone.
6. Return ONLY valid JSON — no preamble, no markdown, no explanation outside the JSON.

OUTPUT FORMAT: Return a single valid JSON object matching the structure requested."""


def build_campaign_prompt(inputs: dict) -> str:
    """Build the user prompt for campaign generation."""
    product_name = inputs.get("product_name", "")
    description = inputs.get("product_description", "")
    features = inputs.get("key_features", "Not specified")
    benefits = inputs.get("benefits", "Not specified")
    audience = inputs.get("target_audience", "")
    age_range = inputs.get("age_range", "Not specified")
    location = inputs.get("location", "Not specified")
    industry = inputs.get("industry", "Not specified")
    pain_points = inputs.get("pain_points", "Not specified")
    objective = inputs.get("campaign_objective", "")
    channels = inputs.get("channels", [])
    duration = inputs.get("campaign_duration", "Not specified")
    budget = inputs.get("budget", "Not specified")
    tone = inputs.get("brand_tone", "Professional")
    competitors = inputs.get("competitors", "Not specified")
    additional = inputs.get("additional_requirements", "")

    channels_str = ", ".join(channels) if isinstance(channels, list) else str(channels)

    return f"""Create a comprehensive, production-ready marketing campaign for the following product and context.

═══════════════════════════════════════════
PRODUCT INFORMATION
═══════════════════════════════════════════
Product/Service Name: {product_name}
Description: {description}
Key Features: {features}
Benefits: {benefits}

═══════════════════════════════════════════
TARGET AUDIENCE
═══════════════════════════════════════════
Primary Audience: {audience}
Age Range: {age_range}
Location/Market: {location}
Industry/Sector: {industry}
Customer Pain Points: {pain_points}

═══════════════════════════════════════════
CAMPAIGN PARAMETERS
═══════════════════════════════════════════
Campaign Objective: {objective}
Marketing Channels: {channels_str}
Campaign Duration: {duration}
Budget: {budget}
Brand Tone: {tone}
Competitors to Differentiate From: {competitors}
Additional Requirements: {additional if additional else "None"}

═══════════════════════════════════════════
REQUIRED OUTPUT (strict JSON)
═══════════════════════════════════════════
Return a JSON object with EXACTLY this structure:
{{
  "campaign_name": "Creative, memorable campaign name",
  "tagline": "Short campaign tagline",
  "objective": "Clear, measurable campaign objective",
  "target_audience": {{
    "primary_segment": "Description of primary audience",
    "demographics": "Age, location, income level etc.",
    "psychographics": "Values, interests, lifestyle",
    "pain_points": ["Pain point 1", "Pain point 2", "Pain point 3"],
    "buying_motivations": ["Motivation 1", "Motivation 2"]
  }},
  "customer_persona": {{
    "name": "Persona name (e.g. 'Tech-Savvy Taylor')",
    "age": "Age or range",
    "role": "Job title or life role",
    "goals": "What they want to achieve",
    "frustrations": "What frustrates them",
    "media_habits": "Where they spend time online"
  }},
  "value_proposition": "The core value this product delivers to this specific audience",
  "positioning_statement": "For [audience], [product] is the [category] that [key benefit] because [reason to believe]",
  "slogans": [
    "Slogan 1 — specific and memorable",
    "Slogan 2 — specific and memorable",
    "Slogan 3 — specific and memorable",
    "Slogan 4 — specific and memorable",
    "Slogan 5 — specific and memorable"
  ],
  "key_messages": [
    "Primary message 1",
    "Primary message 2",
    "Primary message 3"
  ],
  "promotional_content": [
    {{
      "type": "Hero Ad",
      "headline": "Headline text",
      "body": "Body copy (2-3 sentences)",
      "cta": "Call to action text"
    }},
    {{
      "type": "Secondary Ad",
      "headline": "Headline text",
      "body": "Body copy",
      "cta": "Call to action text"
    }}
  ],
  "social_media": [
    {{
      "platform": "Instagram",
      "caption": "Full Instagram caption with hashtags",
      "content_idea": "Visual content suggestion",
      "best_time": "Best posting time"
    }},
    {{
      "platform": "LinkedIn",
      "caption": "LinkedIn-appropriate post copy",
      "content_idea": "Content format suggestion",
      "best_time": "Best posting time"
    }}
  ],
  "email_campaign": [
    {{
      "sequence_name": "Welcome / Awareness",
      "subject_line": "Email subject line",
      "preview_text": "Email preview text",
      "email_body_outline": "Key sections and messaging for this email"
    }},
    {{
      "sequence_name": "Consideration / Nurture",
      "subject_line": "Email subject line",
      "preview_text": "Email preview text",
      "email_body_outline": "Key sections and messaging"
    }},
    {{
      "sequence_name": "Conversion / Offer",
      "subject_line": "Urgency-driven subject line",
      "preview_text": "Email preview text",
      "email_body_outline": "Key sections, offer details, CTA"
    }}
  ],
  "content_strategy": [
    {{
      "content_type": "Blog / Article",
      "topic": "Specific topic title",
      "objective": "Awareness / SEO / Thought leadership",
      "frequency": "Posting frequency recommendation"
    }},
    {{
      "content_type": "Video",
      "topic": "Video concept",
      "objective": "Engagement / Demo",
      "frequency": "Frequency"
    }},
    {{
      "content_type": "Infographic",
      "topic": "Infographic concept",
      "objective": "Shareability",
      "frequency": "Frequency"
    }}
  ],
  "channels": [
    {{
      "channel": "Channel name",
      "role_in_campaign": "Awareness / Consideration / Conversion",
      "budget_allocation_pct": 0,
      "tactics": ["Tactic 1", "Tactic 2"]
    }}
  ],
  "campaign_timeline": [
    {{
      "phase": "Phase 1 — Launch",
      "duration": "Weeks 1-2",
      "activities": ["Activity 1", "Activity 2"],
      "focus": "Awareness"
    }},
    {{
      "phase": "Phase 2 — Amplification",
      "duration": "Weeks 3-6",
      "activities": ["Activity 1", "Activity 2"],
      "focus": "Engagement & Lead Gen"
    }},
    {{
      "phase": "Phase 3 — Conversion",
      "duration": "Weeks 7-end",
      "activities": ["Activity 1", "Activity 2"],
      "focus": "Conversion & Retention"
    }}
  ],
  "cta_options": [
    "Primary CTA text",
    "Secondary CTA text",
    "Soft CTA text"
  ],
  "kpis": [
    {{
      "metric": "KPI name",
      "target": "Specific numeric target or improvement %",
      "measurement_method": "How to measure it"
    }}
  ],
  "success_metrics": {{
    "primary_kpi": "Most important success metric",
    "secondary_kpis": ["KPI 2", "KPI 3"],
    "review_cadence": "Weekly / Monthly review schedule"
  }},
  "optimization_recommendations": [
    "Specific, actionable optimization recommendation 1",
    "Specific, actionable optimization recommendation 2",
    "Specific, actionable optimization recommendation 3"
  ],
  "competitive_differentiation": "How this campaign positions against {competitors}",
  "assumptions": [
    "Any assumption made about the product/audience that was not explicitly provided"
  ]
}}

QUALITY REQUIREMENTS:
- Every slogan must be specific to '{product_name}' — no generic phrases
- Social media captions must be platform-appropriate and ready to use
- Email subjects must be specific and compelling, not generic
- KPI targets must be specific numbers or percentages, not vague language
- Channel recommendations must align with the channels: {channels_str}"""
