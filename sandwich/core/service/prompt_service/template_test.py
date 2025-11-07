from sandwich.core.service.prompt_service.template import template_contents


def test_template_contents():
    assert "I am not a medical professional" in template_contents("system.md")
    assert "Your name is ThriveBot" in template_contents("system.md", "system_chat.md")
