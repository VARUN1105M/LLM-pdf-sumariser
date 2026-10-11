import re
import html
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("lenny_assistant.artifact")

class ArtifactSkill:
    """
    Skill for recognizing, extracting, and sanitizing generated Claude-style Artifacts
    (Markdown documents, interactive HTML/CSS dashboards/calculators).
    """

    ARTIFACT_PROMPT_GUIDELINES = """
ARTIFACT GENERATION GUIDELINES:
When asked to produce a substantive document, guide, dashboard, playbook, calculator, or essay:
Enclose the standalone deliverable inside an <artifact> XML tag:

<artifact identifier="unique-id" type="markdown|html" title="Human-Readable Title">
...content here...
</artifact>

- For type="html": Provide complete, self-contained HTML with embedded <style> tags and responsive CSS. 
- For type="markdown": Provide rich, formatted Markdown with tables, callouts, and structured sections.
- Accompany the artifact with a short, helpful conversational summary outside the tag.
"""

    @classmethod
    def extract_artifacts(cls, response_text: str) -> List[Dict[str, Any]]:
        """
        Parses <artifact identifier="..." type="..." title="...">...</artifact> tags.
        Falls back to detecting complete ```html ... ``` or ```markdown ... ``` blocks if XML tags are absent.
        """
        artifacts = []
        
        # 1. Match explicit XML artifact tags
        tag_pattern = re.compile(
            r'<artifact\s+identifier="([^"]+)"\s+type="([^"]+)"\s+title="([^"]+)">([\s\S]*?)</artifact>',
            re.IGNORECASE
        )
        
        matches = list(tag_pattern.finditer(response_text))
        for m in matches:
            identifier = m.group(1).strip()
            artifact_type = m.group(2).lower().strip()
            title = m.group(3).strip()
            content = m.group(4).strip()
            
            artifacts.append({
                "identifier": identifier,
                "type": artifact_type,
                "title": title,
                "content": content
            })

        # 2. Fallback heuristic: Detect standalone large HTML or Markdown blocks if no XML tag was used
        if not artifacts:
            html_block_pattern = re.compile(r'```(?:html)\s*([\s\S]*?)```', re.IGNORECASE)
            html_match = html_block_pattern.search(response_text)
            if html_match and len(html_match.group(1).strip()) > 150:
                artifacts.append({
                    "identifier": "extracted-html-artifact",
                    "type": "html",
                    "title": "Interactive Growth Artifact",
                    "content": html_match.group(1).strip()
                })

        return artifacts

    @classmethod
    def sanitize_html(cls, raw_html: str) -> str:
        """
        Server-side hygiene for HTML artifacts.
        While client-side rendering uses an isolated sandbox iframe (sandbox="allow-scripts"),
        we also strip obvious malicious patterns such as cookie access, parent frame hijacking,
        and external tracking beacons on the backend.
        """
        # Block attempts to break out of iframe or access parent window/cookies
        sanitized = re.sub(r'parent\.', '/* blocked */', raw_html, flags=re.IGNORECASE)
        sanitized = re.sub(r'top\.location', '/* blocked */', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'document\.cookie', '/* blocked */', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'window\.opener', '/* blocked */', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'localStorage', '/* blocked */', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'sessionStorage', '/* blocked */', sanitized, flags=re.IGNORECASE)
        
        return sanitized
