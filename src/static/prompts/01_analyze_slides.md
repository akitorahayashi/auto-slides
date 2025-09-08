# スライド構造分析プロンプト

あなたは優秀なプレゼンテーション分析専門家です。
提供されたスライドテンプレートの内容を分析し、各スライドの役割とプレースホルダーを特定してください。

## スライドテンプレート内容:
```
${template_content}
```

## 発表目安時間:
${duration_minutes}分

## あなたの任務:
このスライドテンプレートを分析し、以下の情報を抽出してください：

1. **全体構造**: このプレゼンテーションの構成と流れ
2. **各スライド分析**: 各スライドの役割、目的、含まれるプレースホルダー
3. **プレースホルダー一覧**: 全プレースホルダーとその用途

### 分析観点:
- 各スライドの発表での役割（タイトル、導入、本論、結論など）
- プレースホルダーの種類（タイトル、内容、メタ情報など）
- スライド間の論理的なつながり
- 発表時間に対する適切なコンテンツ量

## 出力形式:
以下のJSON形式で出力してください：

```json
{
  "presentation_structure": {
    "total_slides": "スライド総数",
    "presentation_flow": "全体の流れの説明",
    "target_duration": "${duration_minutes}分"
  },
  "slides": [
    {
      "slide_number": 1,
      "role": "title/intro/content/conclusion",
      "purpose": "このスライドの目的",
      "placeholders": [
        {
          "name": "placeholder_name",
          "type": "title/content/meta/code/math",
          "description": "このプレースホルダーの用途",
          "expected_length": "short/medium/long"
        }
      ]
    }
  ],
  "all_placeholders": [
    "placeholder1", "placeholder2", "..."
  ]
}
```

**重要**:
- 必ずJSON形式のみで回答してください
- 他の説明や前置きは含めないでください
- スライドの構造的な役割を重視して分析してください
- プレースホルダーの期待される内容の性質を明確にしてください