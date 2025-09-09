import streamlit as st

from src.schemas import OutputFormat
from src.services import TemplateConverterService
from src.services.slide_generator import SlideGenerator


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("こちらの実行します")
    st.write("よろしいですか？")
    col_yes, col_no = st.columns(2, gap="small")
    with col_yes:
        if st.button("はい", use_container_width=True):
            # ユーザー入力と生成されたマークダウンをセッションに保存
            script_content = st.session_state.get("script_content", "")
            template = st.session_state.app_state.selected_template

            # LLMサービスを使用してプレゼンテーションを生成
            try:
                with st.spinner("LLMがプレゼンテーションを生成中..."):
                    generator = SlideGenerator()
                    generated_markdown = generator.generate(
                        script_content=script_content, template=template
                    )
            except Exception as e:
                st.error(f"プレゼンテーション生成に失敗しました: {str(e)}")
                # フォールバック用の基本的なMarkdown
                generated_markdown = f"""---
marp: true
theme: default
---

# プレゼンテーション

エラーが発生しました。以下は原稿の内容です:

{script_content}

---

# 終わり

ありがとうございました。
"""

            st.session_state.app_state.user_inputs = {
                "format": st.session_state.format_selection,
                "script_content": script_content,
            }
            st.session_state.app_state.generated_markdown = generated_markdown

            # 選択した形式を保存し、結果ページへ遷移
            st.session_state.selected_format = st.session_state.format_selection
            st.switch_page("components/pages/result_page.py")
    with col_no:
        if st.button("いいえ", use_container_width=True):
            # ダイアログを閉じて再描画
            st.rerun()


# app_stateまたはselected_templateが存在しない場合、ギャラリーページにリダイレクト
if (
    not hasattr(st.session_state, "app_state")
    or st.session_state.app_state.selected_template is None
):
    st.switch_page("components/pages/gallery_page.py")

template = st.session_state.app_state.selected_template

st.title(f"📄 {template.name}")

st.subheader(template.description)

if not template:
    st.error("テンプレートが見つかりません。")
    st.stop()

st.divider()

# 原稿入力
st.subheader("📝 原稿の入力")
st.write(
    "プレゼンテーションの原稿を入力してください。LLMが内容を解析してスライドを生成します："
)

# 原稿入力のテキストエリア
script_content = st.text_area(
    "原稿内容",
    key="script_content",
    height=200,
    placeholder="プレゼンテーションの原稿をここに入力してください...\n\n例：\n今日は弊社の新製品についてご紹介いたします。\n\n1. 製品の概要\n新製品は...\n\n2. 主な機能\n- 機能A\n- 機能B\n\n3. まとめ\nこの製品により...",
)

st.divider()
st.subheader("📦 形式を選択")

converter = TemplateConverterService()

# 形式選択のラジオボタン
format_options = {
    "PDF": {"label": "📄 PDF", "format": OutputFormat.PDF},
    "HTML": {"label": "🌐 HTML", "format": OutputFormat.HTML},
    "PPTX": {"label": "📊 PPTX", "format": OutputFormat.PPTX},
}

selected_format = st.radio(
    "出力形式を選択してください：",
    options=list(format_options.keys()),
    format_func=lambda x: format_options[x]["label"],
    key="format_selection",
    horizontal=True,
)

st.divider()

# 実行ボタンとナビゲーションボタンを並べる
col1, col2 = st.columns(2, gap="small")

with col1:
    if st.button("← ギャラリーに戻る", key="back_to_gallery", use_container_width=True):
        st.switch_page("components/pages/gallery_page.py")

with col2:
    if st.button(
        "実行 →", key="execute_download", type="primary", use_container_width=True
    ):
        # 実行確認ダイアログを表示
        confirm_execute_dialog()
