from typing import List


def title_slide(title: str, author: str, date: str, company: str = "") -> str:
    """
    Generate the opening title slide with presentation metadata.

    Args:
        title: Main presentation title
        author: Presenter's name
        date: Presentation date
        company: Company or organization name (optional)

    Returns:
        Markdown formatted title slide with Marp frontmatter
    """
    company_line = f"- Company: {company}" if company else ""
    footer_text = company if company else author

    return f"""---
marp: true
theme: custom-theme
paginate: true
header: '{title}'
footer: '© 2025 {footer_text}'
---

# {title}

- 作成者: {author}
- 日付: {date}
{company_line}

---"""


def lead_slide(main_topic: str) -> str:
    """
    Generate a large emphasis slide for main topic presentation.

    Args:
        main_topic: Main topic or theme to display prominently

    Returns:
        Markdown formatted lead slide with special styling
    """
    return f"""<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# {main_topic}

---"""


def table_of_contents_slide(topics: List[str]) -> str:
    """
    Generate table of contents slide listing main sections.

    Args:
        topics: List of main topics to be covered

    Returns:
        Markdown formatted table of contents slide
    """
    numbered_topics = [f"{i+1}. {topic}" for i, topic in enumerate(topics)]
    topics_text = "\n".join(numbered_topics)

    return f"""## 目次

{topics_text}

---"""


def content_slide(topic: str, content: str) -> str:
    """
    Generate standard content slide with topic and description.

    Args:
        topic: Section title or topic name
        content: Main content text for the slide

    Returns:
        Markdown formatted content slide
    """
    return f"""## {topic}

{content}

---"""


def code_slide(
    topic: str, content: str, code_example: str, language: str = "python"
) -> str:
    """
    Generate content slide with code example block.

    Args:
        topic: Slide title describing the code topic
        content: Explanatory text about the code
        code_example: Source code to display
        language: Programming language for syntax highlighting

    Returns:
        Markdown formatted slide with code block
    """
    return f"""## {topic}

{content}

```{language}
{code_example}
```

---"""


def math_slide(
    topic: str, math_description: str, inline_math: str, block_math: str
) -> str:
    """
    Generate slide with mathematical formulas using LaTeX notation.

    Args:
        topic: Slide title for the mathematical concept
        math_description: Description of the mathematical concept
        inline_math: LaTeX formula for inline display
        block_math: LaTeX formula for block display

    Returns:
        Markdown formatted slide with LaTeX mathematics
    """
    return f"""## {topic}

{math_description}

インライン: {inline_math}

ブロック:

$$
{block_math}
$$

---"""


def conclusion_slide(content: str) -> str:
    """
    Generate conclusion slide for presentation summary.

    Args:
        content: Concluding remarks or summary content

    Returns:
        Markdown formatted conclusion slide
    """
    return f"""## 結論

{content}

---"""
