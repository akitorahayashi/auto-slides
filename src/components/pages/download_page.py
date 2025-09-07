import streamlit as st

from src.models.slide_template import TemplateFormat, TemplateRepository
from src.router import Page
from src.services.template_converter_service import TemplateConverterService


def render_download_page():
    """
    Renders the download page for slide templates.
    """

    if "selected_template_id" not in st.session_state:
        st.error(
            "テンプレートが選択されていません。ギャラリーに戻ってテンプレートを選択してください。"
        )
        app_router = st.session_state.app_router
        if st.button("ギャラリーに戻る"):
            app_router.go_to(Page.GALLERY)
            st.rerun()
        return

    template_id = st.session_state.selected_template_id
    template = TemplateRepository.get_template_by_id(template_id)

    st.title(f"📄 {template.name}")

    st.subheader(template.description)

    if not template:
        st.error(f"テンプレート '{template_id}' が見つかりません。")
        return

    st.divider()
    st.subheader("📦 形式を選択")

    converter = TemplateConverterService()

    # 形式選択のラジオボタン
    format_options = {
        "PDF": {"label": "📄 PDF", "format": TemplateFormat.PDF},
        "HTML": {"label": "🌐 HTML", "format": TemplateFormat.HTML},
        "PPTX": {"label": "📊 PPTX", "format": TemplateFormat.PPTX},
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
        if st.button(
            "← ギャラリーに戻る", key="back_to_gallery", use_container_width=True
        ):
            app_router = st.session_state.app_router
            app_router.go_to(Page.GALLERY)
            st.rerun()

    with col2:
        if st.button(
            "進む →", key="execute_download", type="primary", use_container_width=True
        ):
            # セッションに選択した形式を保存
            st.session_state.selected_format = selected_format
            app_router = st.session_state.app_router
            app_router.go_to(Page.RESULT)
            st.rerun()
