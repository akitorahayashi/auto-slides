import streamlit as st
from pdf2image import convert_from_bytes

from src.schemas import TemplateFormat
from src.services.template_converter_service import TemplateConverterService

# 1. Validation check
if (
    "app_state" not in st.session_state
    or st.session_state.app_state.generated_markdown is None
):
    st.switch_page("src/main.py")

# 2. Get data from app_state
app_state = st.session_state.app_state
template = app_state.selected_template
selected_format = app_state.selected_format
generated_markdown = app_state.generated_markdown


# Navigation buttons
col1, col2 = st.columns(2, gap="small")
with col1:
    if st.button(
        "← 入力ページに戻る",
        key="back_to_implementation",
        use_container_width=True,
    ):
        st.switch_page("components/pages/implementation_page.py")
with col2:
    if st.button(
        "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
    ):
        st.switch_page("src/main.py")  # Go to main page

st.title("📄 生成結果")

format_options = {
    "PDF": {"label": "📄 PDF", "format": TemplateFormat.PDF},
    "HTML": {"label": "🌐 HTML", "format": TemplateFormat.HTML},
    "PPTX": {"label": "📊 PPTX", "format": TemplateFormat.PPTX},
}

st.subheader(f"📋 {template.name}")
st.info(f"選択した形式: {format_options[selected_format]['label']}")

converter = TemplateConverterService()
selected_format_enum = format_options[selected_format]["format"]

try:
    # 3. Call converter with generated_markdown
    if selected_format == "PDF":
        with st.spinner("PDF生成中..."):
            file_data = converter.convert_template_to_pdf(template, generated_markdown)
        mime_type = "application/pdf"
    elif selected_format == "HTML":
        with st.spinner("HTML生成中..."):
            file_data = converter.convert_template_to_html(template, generated_markdown)
        mime_type = "text/html"
    elif selected_format == "PPTX":
        with st.spinner("PPTX生成中..."):
            file_data = converter.convert_template_to_pptx(template, generated_markdown)
        mime_type = (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    st.download_button(
        label=f"📥 {format_options[selected_format]['label']} ファイルをダウンロード",
        data=file_data,
        file_name=converter.get_filename(template, selected_format_enum),
        mime=mime_type,
        key="download_button",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # 4. Update preview logic
    with st.spinner("プレビューを準備中..."):
        if selected_format == "PDF":
            preview_data = file_data
        else:
            preview_data = converter.convert_template_to_pdf(
                template, generated_markdown
            )
        images = convert_from_bytes(preview_data)
    for i, image in enumerate(images):
        st.image(image, caption=f"スライド {i+1}")

except Exception as e:
    st.error(f"❌ {selected_format}生成エラー: {str(e)}")
