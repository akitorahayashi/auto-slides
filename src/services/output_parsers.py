"""Output parsers for various response formats"""

import json
import re

from langchain_core.output_parsers import JsonOutputParser


class RobustJsonOutputParser(JsonOutputParser):
    """JSON Output Parser that can handle text with thinking tags and extra content"""

    def parse(self, text: str) -> dict:
        """Parse JSON from text, handling <think> tags and other artifacts"""
        try:
            # First try standard JSON parsing
            return super().parse(text)
        except Exception:
            # If that fails, try to extract JSON from the text
            return self._extract_json_from_text(text)

    def _extract_json_from_text(self, text: str) -> dict:
        """Extract JSON object from text that may contain other content"""
        # Look for JSON object patterns
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.findall(json_pattern, text, flags=re.DOTALL)

        for match in matches:
            try:
                # Try to parse each potential JSON object
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # If no valid JSON found, return empty dict
        raise ValueError(f"Could not extract valid JSON from text: {text[:200]}...")
