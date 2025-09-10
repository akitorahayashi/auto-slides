スライド構成の専門家として、分析結果に基づいて最適なスライド構造を決定してください。

# タスク
提供された原稿と利用可能なスライド機能を分析し、効果的なスライド構成を計画してください。

# 出力形式
以下のJSON形式で返答してください：

{
    "slides": [
        {
            "slide_name": "title_slide",
            "reason": "開始スライドが必要"
        },
        {
            "slide_name": "table_of_contents_slide", 
            "reason": "複数トピックの概要が必要"
        }
    ],
    "composition_strategy": "全体的なアプローチの簡潔な説明"
}

# 重要な指示
- 必ずJSON形式のみで回答してください
- 余分なテキストや説明は含めないでください
- スライド関数の一覧にある機能のみ使用してください

---
# 論の展開
${analysis_result}

# 利用可能な機能
${slide_functions_summary}

# 原稿
${script_content}