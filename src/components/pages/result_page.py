import streamlit as st
from pdf2image import convert_from_bytes

from src.schemas import TemplateFormat
from src.services.template_converter_service import TemplateConverterService

# app_stateの存在を検証
if "app_state" not in st.session_state:
    st.switch_page("src/main.py")

app_state = st.session_state.app_state

# 必須のstateが揃っているか検証
if app_state.selected_template is None or app_state.user_inputs is None:
    st.switch_page("src/main.py")

template = app_state.selected_template
selected_format_enum = app_state.user_inputs.get("selected_format")

if selected_format_enum is None:
    st.error("形式が選択されていません。")
    st.switch_page("src/components/pages/implementation_page.py")


# ナビゲーションボタンをタイトルの上に配置
col1, col2 = st.columns(2, gap="small")

with col1:
    if st.button(
        "← ダウンロード設定に戻る",
        key="back_to_download_top",
        use_container_width=True,
    ):
        st.switch_page("src/components/pages/implementation_page.py")

with col2:
    if st.button(
        "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
    ):
        st.switch_page("src/components/pages/gallery_page.py")

st.title("📄 生成結果")

format_options = {
    TemplateFormat.PDF: {"label": "📄 PDF", "key": "PDF"},
    TemplateFormat.HTML: {"label": "🌐 HTML", "key": "HTML"},
    TemplateFormat.PPTX: {"label": "📊 PPTX", "key": "PPTX"},
}

st.subheader(f"📋 {template.name}")

# 1. 選択した形式を表示
selected_format_info = format_options.get(selected_format_enum)
st.info(f"選択した形式: {selected_format_info['label']}")

converter = TemplateConverterService()

try:
    if selected_format_enum == TemplateFormat.PDF:
        with st.spinner("PDF生成中..."):
            file_data = converter.convert_template_to_pdf(template)
        mime_type = "application/pdf"
    elif selected_format_enum == TemplateFormat.HTML:
        with st.spinner("HTML生成中..."):
            file_data = converter.convert_template_to_html(template)
        mime_type = "text/html"
    elif selected_format_enum == TemplateFormat.PPTX:
        with st.spinner("PPTX生成中..."):
            file_data = converter.convert_template_to_pptx(template)
        mime_type = (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    # 生成されたマークダウン（この場合は変換後のデータ）をapp_stateに保存
    # Note: ユーザーの指示にはgenerated_markdownとあったが、ここでは生成されたファイルデータを指すものと解釈
    st.session_state.app_state.generated_markdown = file_data

    # 2. ダウンロードボタン
    st.download_button(
        label=f"📥 {selected_format_info['label']} ファイルをダウンロード",
        data=file_data,
        file_name=converter.get_filename(template, selected_format_enum),
        mime=mime_type,
        key="download_button",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # 3. プレビュー
    with st.spinner("プレビューを準備中..."):
        if selected_format_enum == TemplateFormat.PDF:
            # 既存のPDFデータをプレビュー用に使用
            preview_data = file_data
        else:
            # HTML/PPTXは一度PDFに変換してからプレビュー
            preview_data = converter.convert_template_to_pdf(template)
        images = convert_from_bytes(preview_data)
    for i, image in enumerate(images):
        st.image(image, caption=f"スライド {i+1}")

except Exception as e:
    st.error(f"❌ {selected_format_info['key']}生成エラー: {str(e)}")
