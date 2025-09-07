import re

import streamlit as st

from src.schemas import TemplateFormat

if (
    "app_state" not in st.session_state
    or st.session_state.app_state.selected_template is None
):
    st.switch_page("src/main.py")

template = st.session_state.app_state.selected_template

st.title(f"📄 {template.name}")
st.subheader(template.description)
st.divider()

markdown_template = template.read_markdown_content()
placeholders = sorted(list(set(re.findall(r"\{\{(.*?)\}\}", markdown_template))))

user_inputs = {}
if placeholders:
    st.subheader("📝 プレースホルダーの値を入力")
    for placeholder in placeholders:
        user_inputs[placeholder] = st.text_input(
            f"`{placeholder}` の値:", key=f"placeholder_{placeholder}"
        )
else:
    st.info("このテンプレートに編集可能なプレースホルダーはありません。")

st.divider()

st.subheader("📦 形式を選択")
format_options = {
    "PDF": {"label": "📄 PDF", "format": TemplateFormat.PDF},
    "HTML": {"label": "🌐 HTML", "format": TemplateFormat.HTML},
    "PPTX": {"label": "📊 PPTX", "format": TemplateFormat.PPTX},
}
selected_format_key = st.radio(
    "出力形式を選択してください：",
    options=list(format_options.keys()),
    format_func=lambda x: format_options[x]["label"],
    key="format_selection",
    horizontal=True,
)


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("こちらの実行します\nよろしいですか？")
    col_yes, col_no = st.columns(2, gap="small")
    with col_yes:
        if st.button("はい", use_container_width=True):
            generated_markdown = markdown_template
            for key, value in user_inputs.items():
                generated_markdown = generated_markdown.replace(f"{{{{{key}}}}}", value)

            st.session_state.app_state.user_inputs = user_inputs
            st.session_state.app_state.generated_markdown = generated_markdown
            st.session_state.app_state.selected_format = selected_format_key

            st.switch_page("components/pages/result_page.py")
    with col_no:
        if st.button("いいえ", use_container_width=True):
            st.rerun()


st.divider()

col1, col2 = st.columns(2, gap="small")
with col1:
    if st.button("← ギャラリーに戻る", key="back_to_gallery", use_container_width=True):
        st.switch_page("components/pages/gallery_page.py")
with col2:
    if st.button(
        "実行 →", key="execute_download", type="primary", use_container_width=True
    ):
        confirm_execute_dialog()
