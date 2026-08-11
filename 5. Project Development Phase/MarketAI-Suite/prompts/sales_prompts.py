"""
MarketAI Suite — Sales Pitch Prompt Templates
=============================================
"""

from __future__ import annotations


SALES_PITCH_SYSTEM_PROMPT = """You are an elite B2B sales strategist and consultant with 20+ years experience in enterprise sales, solution selling, SPIN selling, and Challenger sales methodologies.

Your expertise covers:
- Consultative selling and customer-centric pitch construction
- Objection handling and competitive differentiation
- Value-based selling and ROI articulation
- Executive communication and C-suite engagement
- Industry-specific sales strategies

CRITICAL RULES:
1. Every element of the pitch must be tied to the customer's specific business context provided.
2. Avoid generic sales clichés. Make every word earn its place.
3. Objection handling must address the specific objections likely for this customer/industry combination.
4. Discovery questions must reveal insights specific to this customer's pain points.
5. The follow-up email must be professional, brief, and reference the pitch conversation.
6. Return ONLY valid JSON — no markdown, no preamble."""


def build_sales_pitch_prompt(inputs: dict) -> str:
    product_name = inputs.get("product_name", "")
    product_description = inputs.get("product_description", "")
    customer_name = inputs.get("customer_name", "")
    customer_industry = inputs.get("customer_industry", "")
    customer_role = inputs.get("customer_role", "Decision maker")
    business_challenges = inputs.get("business_challenges", "Not specified")
    pain_points = inputs.get("pain_points", "")
    usps = inputs.get("unique_selling_points", "Not specified")
    competitors = inputs.get("competitors", "Not specified")
    customer_goals = inputs.get("customer_goals", "Not specified")
    desired_outcome = inputs.get("desired_outcome", "Not specified")
    sales_tone = inputs.get("sales_tone", "Professional and consultative")

    return f"""Create a comprehensive, customer-specific sales pitch for the following scenario.

═══════════════════════════════════════════
PRODUCT / SOLUTION INFORMATION
═══════════════════════════════════════════
Product/Service: {product_name}
Description: {product_description}
Unique Selling Points: {usps}

═══════════════════════════════════════════
CUSTOMER INFORMATION
═══════════════════════════════════════════
Customer/Company Name: {customer_name}
Industry: {customer_industry}
Decision Maker Role: {customer_role}
Known Business Challenges: {business_challenges}
Key Pain Points: {pain_points}
Customer Goals: {customer_goals}
Desired Outcome from this Solution: {desired_outcome}

═══════════════════════════════════════════
COMPETITIVE CONTEXT
═══════════════════════════════════════════
Competitors in Consideration: {competitors}
Sales Tone: {sales_tone}

═══════════════════════════════════════════
REQUIRED OUTPUT (strict JSON)
═══════════════════════════════════════════
Return a JSON object with EXACTLY this structure:
{{
  "executive_summary": "2-3 sentence crisp summary of why this solution is right for {customer_name} right now",
  "value_proposition": "Customer-specific value proposition — why {product_name} for {customer_name} specifically",
  "elevator_pitch": "30-second verbal pitch (3-4 sentences) that hooks the {customer_role} at {customer_name}",
  "detailed_pitch": "Full 2-3 paragraph consultative pitch addressing {customer_name}'s specific situation",
  "talking_points": [
    {{
      "point": "Talking point headline",
      "detail": "Supporting detail that connects to {customer_name}'s context",
      "proof": "Proof point, metric, or example"
    }}
  ],
  "business_benefits": [
    {{
      "benefit": "Specific benefit",
      "impact": "Quantified or qualified impact for {customer_name}",
      "timeline": "When they will see this benefit"
    }}
  ],
  "roi_justification": {{
    "headline": "ROI summary statement",
    "factors": ["ROI factor 1 relevant to their business", "ROI factor 2"],
    "estimated_impact": "Estimated business impact (use ranges if uncertain, label as estimates)"
  }},
  "competitive_differentiation": [
    {{
      "vs_competitor": "Competitor name or 'Status Quo'",
      "our_advantage": "Specific advantage of {product_name}",
      "customer_relevance": "Why this matters to {customer_name}"
    }}
  ],
  "pain_point_mapping": [
    {{
      "pain_point": "Specific pain point from their context",
      "how_we_solve_it": "Specific capability that addresses this pain point",
      "outcome": "The result they will experience"
    }}
  ],
  "objection_handling": [
    {{
      "objection": "Anticipated objection specific to {customer_industry} or {customer_role}",
      "response": "Thoughtful, specific response",
      "reframe": "How to reframe this objection as an opportunity"
    }}
  ],
  "discovery_questions": [
    {{
      "question": "Insightful discovery question",
      "purpose": "What insight this question reveals",
      "follow_up": "Potential follow-up question"
    }}
  ],
  "closing_statement": "Compelling closing that proposes a clear next step aligned with {customer_name}'s goals",
  "next_steps": [
    {{
      "step": "Recommended next step",
      "timeline": "When to do this",
      "owner": "Who is responsible"
    }}
  ],
  "follow_up_email": {{
    "subject": "Professional, specific email subject line",
    "body": "Complete professional follow-up email body (reference the pitch, include next step CTA)",
    "ps_line": "Optional P.S. with an additional value point or urgency"
  }},
  "success_metrics": [
    "What does success look like for {customer_name} 90 days post-implementation"
  ],
  "assumptions": ["Any assumptions made about the customer or their situation"]
}}"""
