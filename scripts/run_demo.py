"""Call all three weather capabilities and save concise demonstration evidence."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from weather_adapter import OpenMeteoAdapter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence" / "demo_results.md"


def block(question: str, tool: str, arguments: dict, result: dict) -> str:
    return "\n".join(
        [
            f"## {question}",
            "",
            f"Tool call: `{tool}({json.dumps(arguments, ensure_ascii=False)})`",
            "",
            "```json",
            json.dumps(result, indent=2, ensure_ascii=False),
            "```",
        ]
    )


def main() -> None:
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    with OpenMeteoAdapter() as adapter:
        sections = [
            "# Live Weather Tool Demonstration",
            "",
            f"Generated: {date.today().isoformat()}",
            "",
            block(
                "What is the current weather in Toronto?",
                "get_current_weather",
                {"location": "Toronto, Ontario, Canada"},
                adapter.current_weather("Toronto, Ontario, Canada"),
            ),
            "",
            block(
                "Will it rain in Chicago tomorrow?",
                "get_forecast",
                {"location": "Chicago, Illinois, USA", "days": 2},
                adapter.forecast("Chicago, Illinois, USA", 2),
            ),
            "",
            block(
                "Should I bring a jacket or umbrella to Austin tomorrow?",
                "get_travel_recommendation",
                {"location": "Austin, Texas, USA", "date": tomorrow},
                adapter.travel_recommendation("Austin, Texas, USA", tomorrow),
            ),
            "",
            "> These are live API tool results, not screenshots of Agent Bricks. Add Agent Bricks screenshots after deployment.",
        ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
