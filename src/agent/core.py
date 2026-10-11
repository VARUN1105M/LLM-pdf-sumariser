import logging
from typing import Dict, Any, List, Optional, Tuple
from src.knowledge.retriever import LennyRetriever
from src.agent.llm_provider import get_llm_provider, LLMResponse
from src.agent.skills.ship30_skill import Ship30ContentSkill, SHIP_30_PRINCIPLES
from src.agent.skills.artifact_skill import ArtifactSkill
from src.config import settings

logger = logging.getLogger("lenny_assistant.agent")

SYSTEM_PROMPT_TEMPLATE = """You are "The Lenny Growth Assistant", an elite forward-deployed product and growth intelligence agent.
Your mission is to turn Lenny Rachitsky's podcast interviews into authoritative, grounded, actionable answers and artifacts for product managers, growth leads, and founders.

CORE BEHAVIOR & CONSTRAINTS:
1. GROUNDED IN TRUTH:
   - Base your core answers strictly on the provided Lenny's Podcast transcript excerpts whenever possible.
   - If the provided excerpts do not contain enough facts to answer the question, explicitly state:
     "Based on Lenny's Podcast transcripts currently in my knowledge base, this topic isn't directly covered. Here is related context from verified episodes, or what top operators advise..."
   - Never fabricate guest quotes, episode numbers, or podcast details.

2. CITATION DISCIPLINE:
   - Attribute principles directly to the guest who stated them (e.g., "[1] Shreyas Doshi explained...", "[2] Elena Verna's rule for PLG...").
   - Mention the episode topic and context.

3. SKILLS & ARTIFACTS:
   - When the user asks for a newsletter, atomic essay, or "Ship 30 for 30" piece:
     Apply the Ship 30 for 30 writing framework (strong hook, 1-3-1 rhythm, skimmable headers, bold lead-ins, actionable takeaway).
   - When the user asks for an interactive tool, dashboard, checklist, calculator, or dedicated document:
     Generate a Claude-style Artifact using the <artifact identifier="..." type="markdown|html" title="..."> format.

ARTIFACT GENERATION:
{artifact_guidelines}
"""

class LennyGrowthAgent:
    """
    Agentic orchestrator following the Claude Agent SDK / Pi Coding Agent pattern:
    - Analyzes intent (QA, Ship 30 essay, interactive artifact)
    - Retrieves grounded transcript evidence
    - Dynamically assembles tools and prompt extensions
    - Executes LLM generation with configured provider
    - Parses citations and extracts native visual artifacts
    """
    def __init__(self, retriever: LennyRetriever):
        self.retriever = retriever
        self.ship30_skill = Ship30ContentSkill()
        self.artifact_skill = ArtifactSkill()

    def _detect_intent(self, user_query: str) -> Dict[str, bool]:
        q_lower = user_query.lower()
        is_ship30 = any(k in q_lower for k in [
            "ship 30", "atomic essay", "1250 word", "essay", "newsletter", "write a post", "article"
        ])
        is_artifact_request = any(k in q_lower for k in [
            "artifact", "dashboard", "calculator", "html", "interactive", "checklist", "framework visual", "table"
        ]) or is_ship30
        return {
            "ship30": is_ship30,
            "artifact": is_artifact_request
        }

    async def execute(
        self,
        query: str,
        session_history: List[Dict[str, str]],
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes an agent turn given the user query and previous conversation context.
        """
        provider_name = provider_name or settings.DEFAULT_LLM_PROVIDER
        
        # 1. Retrieve grounded context from Lenny's transcript knowledge base
        context_str, citations = self.retriever.retrieve_grounded_context(
            query, 
            top_k=settings.RETRIEVAL_TOP_K
        )

        # 2. Determine intent and prompt specialization
        intent = self._detect_intent(query)
        
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            artifact_guidelines=self.artifact_skill.ARTIFACT_PROMPT_GUIDELINES
        )

        if intent["ship30"]:
            system_prompt += f"\n\n{self.ship30_skill.get_system_prompt_extension(context_str)}"
        else:
            system_prompt += f"\n\nVERIFIED TRANSCRIPT EXCERPTS:\n{context_str}"

        # 3. Assemble message history
        messages = []
        for msg in session_history[-6:]: # Keep recent conversational context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": query})

        # 4. Invoke LLM provider
        provider = get_llm_provider(provider_name, model_name=model_name)
        llm_response = await provider.generate(system_prompt, messages)

        # 5. Extract and sanitize any generated artifacts
        raw_artifacts = self.artifact_skill.extract_artifacts(llm_response.content)
        sanitized_artifacts = []
        for art in raw_artifacts:
            clean_content = art["content"]
            if art["type"] == "html":
                clean_content = self.artifact_skill.sanitize_html(clean_content)
            
            sanitized_artifacts.append({
                "identifier": art["identifier"],
                "type": art["type"],
                "title": art["title"],
                "content": clean_content
            })

        return {
            "answer": llm_response.content,
            "citations": citations,
            "artifacts": sanitized_artifacts,
            "provider": llm_response.provider,
            "model": llm_response.model,
            "is_ship30": intent["ship30"]
        }
