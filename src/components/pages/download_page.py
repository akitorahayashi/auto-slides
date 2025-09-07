import streamlit as st

from src.services.template_converter_service import TemplateConverterService

# app_stateの存在を検証
if "app_state" not in st.session_state:
    st.switch_page("src/main.py")

app_state = st.session_state.app_state

# 必須のstateが揃っているか検証
if (
    app_state.selected_template is None
    or app_state.user_inputs is None
    or app_state.generated_markdown is None
):
    st.switch_page("src/main.py")

template = app_state.selected_template
selected_format_enum = app_state.user_inputs.get("selected_format")
file_data = app_state.generated_markdown

st.title("⬇️ ダウンロード")
st.write("生成されたファイルをダウンロードします。")

converter = TemplateConverterService()

# MIMEタイプとファイル名を取得
mime_type = ""
if selected_format_enum.value == "pdf":
    mime_type = "application/pdf"
elif selected_format_enum.value == "html":
    mime_type = "text/html"
elif selected_format_enum.value == "pptx":
    mime_type = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

file_name = converter.get_filename(template, selected_format_enum)

st.download_button(
    label="ファイルをダウンロード",
    data=file_data,
    file_name=file_name,
    mime=mime_type,
    type="primary",
    use_container_width=True,
)

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("結果ページに戻る", use_container_width=True):
        st.switch_page("src/components/pages/result_page.py")
with col2:
    if st.button("ギャラリーに戻る", use_container_width=True):
        st.switch_page("src/components/pages/gallery_page.py")
