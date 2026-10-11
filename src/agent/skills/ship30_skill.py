import logging
from typing import Dict, Any, List

logger = logging.getLogger("lenny_assistant.ship30")

SHIP_30_PRINCIPLES = """
# SHIP 30 FOR 30 WRITING SPECIFICATION & RULES

1. THE HOOK & HEADLINE:
   - Clear > Clever. No vague metaphors or clickbait without substance.
   - The Opening Line must stop the scroll: state a provocative truth, a counter-intuitive observation, or a universal frustration.
   - Use the 1-3-1 rhythm: 1 strong opening sentence. 3 supporting context lines. 1 punchline sentence.

2. NARRATIVE PROGRESSION (The 4-Part Arc):
   - Part 1: The Broken Status Quo (Why conventional wisdom in product/growth is actively harming teams).
   - Part 2: The Core Insight (The paradigm shift revealed in Lenny's podcast transcript).
   - Part 3: The Framework & Playbook (Step-by-step tactical execution steps).
   - Part 4: The Counter-Intuitive Nuance (What amateur operators get wrong when implementing this).

3. SKIMMABLE VISUAL ARCHITECTURE:
   - Use bold lead-in phrasing for every bullet point (**Like this:** follow with punchy explanation).
   - Keep paragraphs under 3 sentences. White space is breathing room for the reader's attention.
   - Use thematic subheaders that convey immediate value (e.g. `### Step 1: Kill Your Perception Backlog`).

4. GROUNDED KNOWLEDGE ATTRIBUTION:
   - Direct attribution to Lenny's guests (e.g. "As Shreyas Doshi pointed out on Lenny's Podcast...", "Elena Verna's golden rule...").
   - Include specific quotes and podcast context.

5. LENGTH & DENSITY:
   - Substantial, deeply actionable long-form essay (~1,000 to 1,250 words).
   - Conclude with a single "One-Line Takeaway" summary.
"""

class Ship30ContentSkill:
    def __init__(self):
        self.name = "ship30_content_skill"
        self.description = "Encodes Ship 30 for 30 atomic essay and long-form writing principles grounded in Lenny's Podcast knowledge base."

    def get_system_prompt_extension(self, context_str: str) -> str:
        return f"""
{SHIP_30_PRINCIPLES}

TASK:
You are equipped with the 'Ship 30 for 30' content creation skill.
Transform the grounded insights from Lenny's Podcast transcripts into a masterclass Ship 30 for 30 style essay.
Ensure all claims, case studies, and frameworks are strictly anchored in the verified transcript excerpts provided below.

GROUNDED TRANSCRIPT KNOWLEDGE:
{context_str}
"""
