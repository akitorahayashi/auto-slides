---
marp: true
theme: gaia
paginate: true
header: 'My Presentation'
footer: '© 2025 My Company'
style: |
  section {
    background-color: #f0f0f0;
    color: #333;
  }
  h1 {
    color: #007bff;
  }
---

# タイトルスライド

- 作成者: あなたの名前
- 日付: 2025年9月5日

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->

# このスライドだけ特別スタイル

---

## 目次

1.  Marpとは
2.  使い方
3.  サンプルスライド
4.  まとめ

---

## 1. Marpとは

- Markdownでスライドが作れるツール
- シンプルで拡張性が高い
- VS CodeやCLIで利用可能

<!--
note: ここはスピーカーノートです。
プレゼン本番で話す内容をここに書きます。
-->

---

## 2. 使い方

1.  Markdownファイルを作成
2.  `---` でスライドを区切る
3.  marpコマンドでPDFやHTMLに変換

---

<!-- backgroundColor: black -->
<!-- color: white -->

# このスライド以降は色が反転します

---

## 3. サンプルスライド

- 画像やコードも挿入可能

```python
print("Hello, Marp!")
```

---

## LaTeX数式の例

MarpではLaTeX記法で数式も表示できます。

インライン: $E = mc^2$

ブロック:

$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$

---

## まとめ

- Markdownで簡単にスライド作成
- Marpを使ってプレゼンを効率化