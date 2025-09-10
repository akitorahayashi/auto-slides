あなたはスライド作成の専門家です。以下の原稿を分析してください。

# 原稿
${script_content}

# 分析タスク
以下の項目について分析し、JSON形式で返答してください：

1. **main_theme**: この原稿の中心的なテーマ
2. **key_points**: 聞き手に伝えるべき重要なポイント（配列形式）
3. **target_audience**: 想定される聞き手
4. **presentation_style**: 推奨プレゼンテーション形式
5. **content_structure**: コンテンツの構造と順序

# 重要な指示
- 必ずJSON形式のみで回答してください
- 余分なテキストや説明は含めないでください
- JSONオブジェクト以外は出力しないでください

# 出力形式
{
  "main_theme": "中心的なテーマ",
  "key_points": ["ポイント1", "ポイント2", "ポイント3"],
  "target_audience": "想定される聞き手",
  "presentation_style": "推奨スタイル",
  "content_structure": "構造と順序の説明"
}