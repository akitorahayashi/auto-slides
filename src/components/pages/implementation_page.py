import streamlit as st

from src.schemas import TemplateFormat
from src.services.template_converter_service import TemplateConverterService


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("こちらの実行します\nよろしいですか？")
    col_yes, col_no = st.columns(2, gap="small")
    with col_yes:
        if st.button("はい", use_container_width=True):
            # ユーザー入力と生成されたマークダウンをセッションに保存
            template = st.session_state.app_state.selected_template
            st.session_state.app_state.user_inputs = {
                "format": st.session_state.format_selection
            }
            st.session_state.app_state.generated_markdown = (
                template.read_markdown_content()
            )

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
    st.error("テンプレートが選択されていません。")
    st.info("ギャラリーページに戻って、使用するテンプレートを選択してください。")
    if st.button("ギャラリーに戻る"):
        st.switch_page("src/main.py")
    st.stop()

template = st.session_state.app_state.selected_template

st.title(f"📄 {template.name}")

st.subheader(template.description)

if not template:
    st.error("テンプレートが見つかりません。")
    st.stop()

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
    if st.button("← ギャラリーに戻る", key="back_to_gallery", use_container_width=True):
        st.switch_page("components/pages/gallery_page.py")

with col2:
    if st.button(
        "実行 →", key="execute_download", type="primary", use_container_width=True
    ):
        # 実行確認ダイアログを表示
        confirm_execute_dialog()
