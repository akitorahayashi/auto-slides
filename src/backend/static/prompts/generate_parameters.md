${slide_name}スライドのパラメータを生成してください。

必須パラメータ：${arguments_list}

原稿から抽出してJSON出力（パラメータ名は完全一致必須）：

例1：パラメータが"title, content"の場合
```json
{
    "slide_name": "${slide_name}",
    "parameters": {
        "title": "抽出したタイトル",
        "content": "抽出した内容"
    }
}
```

例2：パラメータが"topic, content"の場合
```json
{
    "slide_name": "${slide_name}",
    "parameters": {
        "topic": "抽出したトピック",
        "content": "抽出した内容"
    }
}
```

注意：パラメータ名は必要とされているものから絶対に変更しないでください（topic≠topics）

## 参考情報

### 論の展開
${analysis_result}

### 原稿
${script_content}