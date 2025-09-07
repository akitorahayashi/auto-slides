import streamlit as st

from src.models import TemplateRepository

# Load and apply custom CSS for this component
try:
    with open("src/static/css/main_page.css", "r", encoding="utf-8") as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    # Continue without custom styling if the CSS file is not found
    pass

st.title("🎼 テンプレートギャラリー")

st.write("スライドテンプレートを選択して、ダウンロードページに進んでください。")

templates = TemplateRepository.get_all_templates()
if templates:
    # カードをグリッドで表示
    cols_per_row = 2
    for i in range(0, len(templates), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, template in enumerate(templates[i : i + cols_per_row]):
            with cols[j]:
                # カードスタイルのコンテナ
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #e6e6fa;
                            border-radius: 10px;
                            padding: 20px;
                            margin: 10px 0;
                            background-color: #f8f9fa;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                            <h3 style="margin-top: 0; color: #333;">📋 {template.name}</h3>
                            <p style="color: #666; font-size: 14px;">{template.description}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # テンプレート選択ボタン
                    if st.button(
                        f"{template.name} を使う",
                        type="primary",
                        key=f"select_template_{template.id}",
                        use_container_width=True,
                    ):
                        st.session_state.app_state.selected_template = template
                        st.switch_page("src/components/pages/implementation_page.py")

    # テンプレートが奇数の場合、空のカラムを埋める
    if len(templates) % cols_per_row != 0:
        remaining_cols = cols_per_row - (len(templates) % cols_per_row)
        for _ in range(remaining_cols):
            st.empty()
else:
    st.warning("利用可能なテンプレートがありません。")

st.divider()
