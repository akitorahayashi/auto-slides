"""Output parsers for various response formats"""

import json
import re

from langchain_core.output_parsers import JsonOutputParser


class JsonParser(JsonOutputParser):
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
        # Try multiple strategies to find JSON

        # Strategy 1: Look for complete JSON objects with balanced braces
        for i, char in enumerate(text):
            if char == "{":
                brace_count = 0
                for j in range(i, len(text)):
                    if text[j] == "{":
                        brace_count += 1
                    elif text[j] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            candidate = text[i : j + 1]
                            try:
                                return json.loads(candidate.strip())
                            except json.JSONDecodeError:
                                continue
                            break

        # Strategy 2: Look for JSON patterns with regex (fallback)
        json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple nested objects
            r"\{.*?\}",  # Basic object pattern
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, flags=re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # If no valid JSON found, raise error
        raise ValueError(f"Could not extract valid JSON from text: {text[:200]}...")
