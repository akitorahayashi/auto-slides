スライド機能のパラメータを原稿から生成してください。

# タスク
指定されたスライド機能に適切なパラメータ値を原稿から抽出・生成してください。

# 出力形式
{
    "slide_name": "${slide_name}",
    "parameters": {
        "arg1": "value1",
        "arg2": "value2"
    }
}

# 重要な指示
- 必ずJSON形式のみで回答してください
- 余分なテキストや説明は含めないでください
- 全ての必須パラメータを提供してください

---
# スライド名
${slide_name}

# スライドの目的
${function_purpose}

# 関数の定義形式
${function_signature}

# 引数情報
${arguments_list}

# 論の展開
${analysis_result}

# 原稿
${script_content}