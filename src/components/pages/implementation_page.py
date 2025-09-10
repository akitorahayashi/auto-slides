import streamlit as st

from src.chains.slide_gen_chain import SlideGenChain
from src.schemas import OutputFormat


@st.dialog("実行確認", width="small", dismissible=True)
def confirm_execute_dialog():
    st.write("こちらの実行します")
    st.write("よろしいですか？")
    col_no, col_yes = st.columns(2, gap="small")
    with col_no:
        if st.button("いいえ", use_container_width=True):
            # ダイアログを閉じて再描画
            st.rerun()
    with col_yes:
        if st.button("はい", use_container_width=True, type="primary"):
            # ユーザー入力と生成されたマークダウンをセッションに保存
            script_content = st.session_state.get("script_content", "")
            template = st.session_state.app_state.selected_template

            # LLMサービスを使用してプレゼンテーションを生成
            try:
                with st.spinner("LLMがプレゼンテーションを生成中..."):
                    chain = SlideGenChain()

                    # Phase 1: Script Analysis
                    with st.spinner("原稿を解析中..."):
                        analysis_result = chain.analysis_chain.invoke(
                            {"script_content": script_content}
                        )

                    # Phase 2: Content Planning
                    with st.spinner("コンテンツを計画中..."):
                        placeholders = list(template.extract_placeholders())
                        planning_result = chain.planning_chain.invoke(
                            {
                                "script_content": script_content,
                                "analysis_result": analysis_result,
                                "placeholders": placeholders,
                                "template": template,
                            }
                        )

                    # Phase 3: Content Generation
                    with st.spinner("スライドを生成中..."):
                        generation_result = chain.generation_chain.invoke(
                            {
                                "script_content": script_content,
                                "analysis_result": analysis_result,
                                "planning_result": planning_result,
                                "placeholders": placeholders,
                                "template": template,
                            }
                        )

                    # Phase 4: Content Validation
                    with st.spinner("コンテンツを検証中..."):
                        validation_result = chain.validation_chain.invoke(
                            {
                                "script_content": script_content,
                                "analysis_result": analysis_result,
                                "content_plan": planning_result,
                                "generated_content": generation_result,
                                "template": template,
                            }
                        )

                    generated_markdown = validation_result.get(
                        "final_markdown", generation_result.get("markdown", "")
                    )
                    
                    # 成功時のみ結果ページに遷移
                    st.session_state.app_state.user_inputs = {
                        "format": st.session_state.format_selection,
                        "script_content": script_content,
                    }
                    st.session_state.app_state.generated_markdown = generated_markdown
                    st.session_state.selected_format = st.session_state.format_selection
                    st.switch_page("components/pages/result_page.py")
                    
            except Exception as e:
                # エラーが発生した場合はセッション状態にエラーメッセージを保存
                st.session_state.generation_error = str(e)
                st.rerun()


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
    st.switch_page("components/pages/gallery_page.py")

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
        st.switch_page("components/pages/gallery_page.py")

with col2:
    if st.button(
        "実行 →", key="execute_download", type="primary", use_container_width=True
    ):
        # 実行確認ダイアログを表示
        confirm_execute_dialog()
