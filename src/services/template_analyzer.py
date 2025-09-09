import re
from pathlib import Path
from typing import Dict, List, Set

from src.models.slide_template import SlideTemplate


class TemplateAnalyzer:
    """Analyze templates to detect required placeholders dynamically"""

    def extract_placeholders(self, template_content: str) -> Set[str]:
        """Extract all ${placeholder} variables from template content"""
        # Find all ${variable_name} patterns
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, template_content)
        return set(matches)

    def categorize_placeholders(self, placeholders: Set[str]) -> Dict[str, List[str]]:
        """Categorize placeholders by type for better LLM prompts"""
        categories = {
            "titles": [],
            "content": [],
            "meta": [],
            "topics": [],
            "other": [],
        }

        for placeholder in placeholders:
            lower_name = placeholder.lower()

            if any(word in lower_name for word in ["title", "header"]):
                categories["titles"].append(placeholder)
            elif any(
                word in lower_name for word in ["content", "description", "conclusion"]
            ):
                categories["content"].append(placeholder)
            elif any(word in lower_name for word in ["author", "date", "company"]):
                categories["meta"].append(placeholder)
            elif any(word in lower_name for word in ["topic", "point", "section"]):
                categories["topics"].append(placeholder)
            else:
                categories["other"].append(placeholder)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def create_dynamic_prompt(
        self, script_content: str, template: SlideTemplate, placeholders: Set[str]
    ) -> str:
        """Create a dynamic prompt based on template requirements"""
        categories = self.categorize_placeholders(placeholders)

        prompt_parts = [
            "以下の原稿からスライド用の内容を作成してください。",
            f"発表時間: {template.duration_minutes}分",
            "",
            "原稿:",
            script_content,
            "",
            "以下の形式で返答してください:",
        ]

        # Add dynamic sections based on template requirements
        section_counter = 1

        # Handle titles
        if "titles" in categories:
            for title_var in categories["titles"]:
                prompt_parts.append(f"TITLE_{section_counter}: [{title_var}の内容]")
                section_counter += 1
        else:
            prompt_parts.append("TITLE: [プレゼンテーションのタイトル]")

        # Handle topics/points
        if "topics" in categories:
            topic_vars = sorted(categories["topics"])
            for i, topic_var in enumerate(topic_vars[:5], 1):  # Limit to 5 topics
                prompt_parts.append(f"POINT{i}: [{topic_var}の内容]")
        else:
            # Default points
            for i in range(1, 4):
                prompt_parts.append(f"POINT{i}: [第{i}のポイント]")

        # Handle content sections
        if "content" in categories:
            for content_var in categories["content"]:
                if "conclusion" in content_var.lower():
                    prompt_parts.append(f"CONCLUSION: [{content_var}の内容]")
                else:
                    prompt_parts.append(f"CONTENT: [{content_var}の内容]")
        else:
            prompt_parts.append("CONCLUSION: [まとめ・結論]")

        # Add meta information instructions
        if "meta" in categories:
            prompt_parts.extend(
                ["", "追加情報:", "AUTHOR: [発表者名]", "DATE: [発表日]"]
            )

        prompt_parts.extend(
            [
                "",
                "注意事項:",
                "- 各項目は1行で簡潔に",
                "- 発表時間に適した内容量にしてください",
                "- 聞き手にとって分かりやすい構成にしてください",
            ]
        )

        return "\n".join(prompt_parts)

    def analyze_template(self, template: SlideTemplate) -> Dict[str, any]:
        """Complete template analysis"""
        try:
            content = template.read_markdown_content()
            placeholders = self.extract_placeholders(content)
            categories = self.categorize_placeholders(placeholders)

            return {
                "placeholders": placeholders,
                "categories": categories,
                "total_placeholders": len(placeholders),
                "has_dynamic_content": len(placeholders) > 5,
            }
        except (FileNotFoundError, UnicodeDecodeError, OSError) as e:
            return {
                "error": str(e),
                "placeholders": set(),
                "categories": {},
                "total_placeholders": 0,
                "has_dynamic_content": False,
            }


# Test function
def test_template_analyzer():
    """Test the template analyzer"""
    analyzer = TemplateAnalyzer()

    template = SlideTemplate(
        id="test",
        name="Test Template",
        description="Test Description",
        template_dir=Path("src/templates/k2g4h1x9"),
        duration_minutes=5,
    )

    analysis = analyzer.analyze_template(template)

    print("=== TEMPLATE ANALYSIS ===")
    print(f"Total placeholders: {analysis['total_placeholders']}")
    print(f"Placeholders: {sorted(analysis['placeholders'])}")
    print(f"Categories: {analysis['categories']}")
    print(f"Has dynamic content: {analysis['has_dynamic_content']}")

    print("\n=== DYNAMIC PROMPT ===")
    script = "機械学習の基礎について説明します"
    prompt = analyzer.create_dynamic_prompt(script, template, analysis["placeholders"])
    print(prompt[:300] + "..." if len(prompt) > 300 else prompt)

    return analysis


if __name__ == "__main__":
    test_template_analyzer()
