import streamlit as st

from src.router import Page
from src.schemas import TemplateFormat
from src.services.template_converter_service import TemplateConverterService


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("こちらの実行します\nよろしいですか？")
    col_yes, col_no = st.columns(2, gap="small")
    with col_yes:
        if st.button("はい", use_container_width=True):
            # セッションに選択した形式を保存し、結果ページへ遷移
            selected_format = st.session_state.format_selection
            st.session_state.selected_format = selected_format
            app_router = st.session_state.app_router
            app_router.go_to(Page.RESULT)
            st.rerun()
    with col_no:
        if st.button("いいえ", use_container_width=True):
            # ダイアログを閉じて再描画
            st.rerun()


def render_download_page():
    """
    Renders the download page for slide templates.
    """

    if (
        not hasattr(st.session_state, "app_state")
        or st.session_state.app_state.selected_template is None
    ):
        st.error(
            "テンプレートが選択されていません。ギャラリーに戻ってテンプレートを選択してください。"
        )
        app_router = st.session_state.app_router
        if st.button("ギャラリーに戻る"):
            app_router.go_to(Page.GALLERY)
            st.rerun()
        return

    template = st.session_state.app_state.selected_template

    st.title(f"📄 {template.name}")

    st.subheader(template.description)

    if not template:
        st.error("テンプレートが見つかりません。")
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
            "実行 →", key="execute_download", type="primary", use_container_width=True
        ):
            # 実行確認ダイアログを表示
            confirm_execute_dialog()
