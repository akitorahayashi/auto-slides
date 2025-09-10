import tempfile
from pathlib import Path

import streamlit as st
from pdf2image import convert_from_bytes

from src.schemas import OutputFormat
from src.services.marp_service import MarpService

# ナビゲーションボタンをタイトルの上に配置
col1, col2 = st.columns(2, gap="small")

with col1:
    if st.button(
        "← ダウンロード設定に戻る",
        key="back_to_download_top",
        use_container_width=True,
    ):
        st.switch_page("components/pages/implementation_page.py")

with col2:
    if st.button(
        "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
    ):
        st.switch_page("components/pages/gallery_page.py")

st.title("📄 生成結果")

# 必要なセッション情報が存在しない場合、ギャラリーページにリダイレクト
if (
    not hasattr(st.session_state, "app_state")
    or st.session_state.app_state.selected_template is None
    or st.session_state.app_state.generated_markdown is None
    or "selected_format" not in st.session_state
):
    st.switch_page("components/pages/gallery_page.py")

template = st.session_state.app_state.selected_template
selected_format = st.session_state.selected_format

if not template:
    st.error("テンプレートが見つかりません。")
    st.stop()

format_options = {
    "PDF": {"label": "📄 PDF", "format": OutputFormat.PDF},
    "HTML": {"label": "🌐 HTML", "format": OutputFormat.HTML},
    "PPTX": {"label": "📊 PPTX", "format": OutputFormat.PPTX},
}

st.subheader(f"📋 {template.name}")

# 1. 選択した形式を表示
st.info(f"選択した形式: {format_options[selected_format]['label']}")

selected_format_enum = format_options[selected_format]["format"]

try:
    # 生成されたMarkdownコンテンツとCSSを取得
    generated_markdown = st.session_state.app_state.generated_markdown
    css_content = template.read_css_content()

    # 一時ファイルを作成してMarpServiceを使用
    temp_dir = Path(tempfile.gettempdir()) / "auto-slides"
    temp_dir.mkdir(exist_ok=True)

    temp_md_path = temp_dir / f"{template.id}.md"
    temp_css_path = temp_dir / f"{template.id}.css"

    # マークダウンファイルを作成
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(generated_markdown)

    # CSSファイルを作成
    with open(temp_css_path, "w", encoding="utf-8") as f:
        f.write(css_content)

    # MarpServiceを使用して変換
    marp_service = MarpService(str(temp_md_path), str(temp_dir))

    if selected_format == "PDF":
        with st.spinner("PDF生成中..."):
            output_path = marp_service.generate_pdf(f"{template.id}.pdf")
            with open(output_path, "rb") as f:
                file_data = f.read()
        mime_type = "application/pdf"
    elif selected_format == "HTML":
        with st.spinner("HTML生成中..."):
            output_path = marp_service.generate_html(f"{template.id}.html")
            with open(output_path, "rb") as f:
                file_data = f.read()
        mime_type = "text/html"
    elif selected_format == "PPTX":
        with st.spinner("PPTX生成中..."):
            output_path = marp_service.generate_pptx(f"{template.id}.pptx")
            with open(output_path, "rb") as f:
                file_data = f.read()
        mime_type = (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    # 2. ダウンロードボタン
    filename = f"{template.id}.{selected_format_enum.value}"
    st.download_button(
        label=f"📥 {format_options[selected_format]['label']} ファイルをダウンロード",
        data=file_data,
        file_name=filename,
        mime=mime_type,
        key="download_button",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # 3. 生成されたMarkdownコンテンツ表示
    with st.expander("📝 生成されたMarkdownコンテンツ", expanded=False):
        st.code(generated_markdown, language="markdown")

    st.divider()

    # 4. プレビュー
    with st.spinner("プレビューを準備中..."):
        if selected_format == "PDF":
            # 既存のPDFデータをプレビュー用に使用
            preview_data = file_data
        else:
            # HTML/PPTXは一度PDFに変換してからプレビュー
            preview_path = marp_service.generate_pdf(f"preview_{template.id}.pdf")
            with open(preview_path, "rb") as f:
                preview_data = f.read()
        images = convert_from_bytes(preview_data)
    for i, image in enumerate(images):
        st.image(image, caption=f"スライド {i+1}")

except Exception as e:
    st.error(f"❌ {selected_format}生成エラー: {str(e)}")
