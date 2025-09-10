import streamlit as st

from src.protocols.schemas.output_format import OutputFormat


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("プレゼンテーションの生成を開始します")
    st.write("よろしいですか？")
    col_no, col_yes = st.columns(2, gap="small")
    with col_no:
        if st.button("いいえ", use_container_width=True):
            # ダイアログを閉じて再描画
            st.rerun()
    with col_yes:
        if st.button("はい", use_container_width=True, type="primary"):
            # ユーザー入力をセッションに保存
            script_content = st.session_state.get("script_content", "")

            # 入力データを検証
            if not script_content.strip():
                st.session_state.generation_error = "原稿を入力してください。"
                st.rerun()
                return

            # ユーザー入力を保存し、結果ページに遷移
            # generated_markdownは結果ページで生成される
            st.session_state.app_state.user_inputs = {
                "format": st.session_state.format_selection,
                "script_content": script_content,
            }
            st.session_state.selected_format = st.session_state.format_selection
            # LLM処理開始フラグを設定
            st.session_state.should_start_generation = True
            st.switch_page("frontend/components/pages/result_page.py")


@st.dialog("エラー", width="medium", dismissible=True)
def show_error_dialog(error_message):
    st.error("プレゼンテーション生成に失敗しました")
    st.write(f"エラーの詳細: {error_message}")
    if st.button("OK", use_container_width=True, type="primary"):
        # エラーメッセージを削除してダイアログを閉じる
        if "generation_error" in st.session_state:
            del st.session_state.generation_error
        st.rerun()


# app_stateまたはselected_templateが存在しない場合、ギャラリーページにリダイレクト
if (
    not hasattr(st.session_state, "app_state")
    or st.session_state.app_state.selected_template is None
):
    st.switch_page("frontend/components/pages/gallery_page.py")

# エラーダイアログの表示処理
if "generation_error" in st.session_state:
    show_error_dialog(st.session_state.generation_error)

template = st.session_state.app_state.selected_template

st.title(f"📄 {template.name}")

st.subheader(template.description)

if not template:
    st.error("テンプレートが見つかりません。")
    st.stop()

st.divider()

# 原稿入力
st.subheader("📝 原稿の入力")

# 原稿入力のテキストエリア
script_content = st.text_area(
    "原稿内容",
    key="script_content",
    height=200,
    placeholder="プレゼンテーションの原稿をここに入力します...",
)

st.divider()
st.subheader("📦 形式を選択")

# MarpService will be used in result page for conversion

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
        st.switch_page("frontend/components/pages/gallery_page.py")

with col2:
    if st.button(
        "実行 →", key="execute_download", type="primary", use_container_width=True
    ):
        # 実行確認ダイアログを表示
        confirm_execute_dialog()
