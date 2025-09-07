import streamlit as st
from pdf2image import convert_from_bytes

from src.models.slide_template import TemplateFormat, TemplateRepository
from src.router import Page
from src.services.template_converter_service import TemplateConverterService


def render_result_page():
    """
    Renders the result page with download functionality.
    """

    st.empty()

    # ナビゲーションボタンをタイトルの上に配置
    col1, col2 = st.columns(2, gap="small")

    with col1:
        if st.button(
            "← ダウンロード設定に戻る",
            key="back_to_download_top",
            use_container_width=True,
        ):
            app_router = st.session_state.app_router
            app_router.go_to(Page.DOWNLOAD)
            st.rerun()

    with col2:
        if st.button(
            "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
        ):
            app_router = st.session_state.app_router
            app_router.go_to(Page.GALLERY)
            st.rerun()

    st.title("📄 生成結果")

    if (
        "selected_template_id" not in st.session_state
        or "selected_format" not in st.session_state
    ):
        st.error("セッション情報が不足しています。ギャラリーからやり直してください。")
        app_router = st.session_state.app_router
        if st.button("ギャラリーに戻る"):
            app_router.go_to(Page.GALLERY)
            st.rerun()
        return

    template_id = st.session_state.selected_template_id
    selected_format = st.session_state.selected_format

    template = TemplateRepository.get_template_by_id(template_id)
    if not template:
        st.error(f"テンプレート '{template_id}' が見つかりません。")
        return

    format_options = {
        "PDF": {"label": "📄 PDF", "format": TemplateFormat.PDF},
        "HTML": {"label": "🌐 HTML", "format": TemplateFormat.HTML},
        "PPTX": {"label": "📊 PPTX", "format": TemplateFormat.PPTX},
    }

    st.subheader(f"📋 {template.name}")

    # 1. 選択した形式を表示
    st.info(f"選択した形式: {format_options[selected_format]['label']}")

    converter = TemplateConverterService()
    selected_format_enum = format_options[selected_format]["format"]

    try:
        if selected_format == "PDF":
            with st.spinner("PDF生成中..."):
                file_data = converter.convert_template_to_pdf(template)
            mime_type = "application/pdf"
        elif selected_format == "HTML":
            with st.spinner("HTML生成中..."):
                file_data = converter.convert_template_to_html(template)
            mime_type = "text/html"
        elif selected_format == "PPTX":
            with st.spinner("PPTX生成中..."):
                file_data = converter.convert_template_to_pptx(template)
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        # 2. ダウンロードボタン
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

        # 3. プレビュー
        with st.spinner("プレビューを準備中..."):
            if selected_format == "PDF":
                # 既存のPDFデータをプレビュー用に使用
                preview_data = file_data
            else:
                # HTML/PPTXは一度PDFに変換してからプレビュー
                preview_data = converter.convert_template_to_pdf(template)
            images = convert_from_bytes(preview_data)
        for i, image in enumerate(images):
            st.image(image, caption=f"スライド {i+1}")

    except Exception as e:
        st.error(f"❌ {selected_format}生成エラー: {str(e)}")
