import re
from typing import Any, Dict, Optional


class StructuredResponseParser:
    """Parse structured natural language responses from LLM"""

    def __init__(self):
        pass

    def remove_think_tags(self, text: str) -> str:
        """Remove <think> tags from response"""
        # Use regex for robust removal of content within and including think tags
        return re.sub(r"(?s)<think>.*?</think>\s*", "", text).strip()

    def parse_basic_structure(self, text: str) -> Dict[str, Any]:
        """Parse basic TITLE/POINT/CONCLUSION structure"""
        text = self.remove_think_tags(text)

        result = {}

        # Extract TITLE
        title_match = re.search(r"TITLE:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        result["presentation_title"] = (
            title_match.group(1).strip() if title_match else "デフォルトタイトル"
        )

        # Extract POINTs
        for i in range(1, 6):  # Support up to POINT5
            point_match = re.search(rf"POINT{i}:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
            if point_match:
                result[f"topic_{i}"] = f"ポイント{i}"
                result[f"topic_{i}_content"] = f"- {point_match.group(1).strip()}"

        # Extract CONCLUSION
        conclusion_match = re.search(r"CONCLUSION:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        result["conclusion_content"] = (
            f"- {conclusion_match.group(1).strip()}" if conclusion_match else "- まとめ"
        )

        # Add default values for common placeholders
        result.update(
            {
                "author_name": "発表者",
                "presentation_date": "2024-01-01",
                "header_title": result["presentation_title"],
                "company_name": "会社名",
                "main_topic": result["presentation_title"],
            }
        )

        return result

    def parse_enhanced_structure(
        self, text: str, required_placeholders: Optional[set] = None
    ) -> Dict[str, Any]:
        """Enhanced parser that handles dynamic template requirements"""
        text = self.remove_think_tags(text)
        result = {}

        # Parse all TITLE_X patterns
        title_matches = re.findall(
            r"TITLE(?:_\d+)?:\s*(.+?)(?=\n|$)", text, re.MULTILINE
        )
        if title_matches:
            result["presentation_title"] = title_matches[0].strip()
            result["header_title"] = title_matches[0].strip()
            result["main_topic"] = title_matches[0].strip()
        else:
            default_title = "Default Title"
            result["presentation_title"] = default_title
            result["header_title"] = default_title
            result["main_topic"] = default_title

        # Parse all POINT patterns
        point_matches = re.findall(r"POINT(\d+):\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        for i, content in point_matches:
            result[f"topic_{i}"] = f"ポイント{i}"
            result[f"topic_{i}_content"] = f"- {content.strip()}"

        # Parse CONTENT patterns
        content_matches = re.findall(r"CONTENT:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        if content_matches:
            result["conclusion_content"] = f"- {content_matches[0].strip()}"

        # Parse CONCLUSION
        conclusion_match = re.search(r"CONCLUSION:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        if conclusion_match:
            result["conclusion_content"] = f"- {conclusion_match.group(1).strip()}"
        elif "conclusion_content" not in result:
            result["conclusion_content"] = "- Summary"

        # Parse META information
        author_match = re.search(r"AUTHOR:\s*(.+?)(?=\n|$)", text, re.MULTILINE)
        date_match = re.search(r"DATE:\s*(.+?)(?=\n|$)", text, re.MULTILINE)

        # Add default values
        result.update(
            {
                "author_name": (
                    author_match.group(1).strip() if author_match else "発表者"
                ),
                "presentation_date": (
                    date_match.group(1).strip() if date_match else "2024-01-01"
                ),
                "company_name": "会社名",
                "code_example": "print('Hello, World!')",
                "math_description": "数式の説明",
                "inline_math": "$x = y + z$",
                "block_math": "E = mc^2",
            }
        )

        # Ensure all required placeholders have a default value
        for key in required_placeholders or []:
            result.setdefault(key, "")

        return result

    def test_parser(self):
        """Test the parser with sample data"""
        sample_text = """<think>thinking...</think>
TITLE: Python非同期プログラミングの基礎
POINT1: asyncioライブラリの基本的な使い方
POINT2: async/await構文の理解
POINT3: 実際のコード例と応用
CONCLUSION: 非同期プログラミングでアプリケーションのパフォーマンスを向上させる"""

        result = self.parse_basic_structure(sample_text)
        print("Parsed result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        return result


if __name__ == "__main__":
    parser = StructuredResponseParser()
    parser.test_parser()
