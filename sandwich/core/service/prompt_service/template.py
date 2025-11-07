from pathlib import Path

TEMPLATES_PATH = Path(__file__).parent / "templates"


def template_contents(*paths: str | Path) -> str:
    output = []
    for path in paths:
        template_path = TEMPLATES_PATH / path
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        output.append(template_path.read_text())
    return "\n".join(output)
