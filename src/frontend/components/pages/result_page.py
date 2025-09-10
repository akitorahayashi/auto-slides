import tempfile
from pathlib import Path

import streamlit as st
from pdf2image import convert_from_bytes

from src.backend.services.marp_service import MarpService
from src.protocols.schemas.output_format import OutputFormat


def generate_slides_with_llm():
    """LLMを使用してスライドを生成する"""
    script_content = st.session_state.app_state.user_inputs["script_content"]
    template = st.session_state.app_state.selected_template
    generator = st.session_state.app_state.slide_generator

    try:
        with st.spinner("スライドを生成中..."):
            generated_markdown = generator.invoke_slide_gen_chain(
                script_content, template
            )

        # 生成完了後、セッションに保存
        st.session_state.app_state.generated_markdown = generated_markdown
        # 生成開始フラグをクリア
        if "should_start_generation" in st.session_state:
            del st.session_state.should_start_generation
        st.success("✅ スライドの生成が完了しました！")
        st.rerun()

    except Exception as e:
        st.error(f"❌ プレゼンテーション生成に失敗しました: {str(e)}")
        st.error("設定画面に戻って再度お試しください。")
        if st.button("設定画面に戻る", type="primary"):
            st.switch_page("src/frontend/components/pages/implementation_page.py")


# ナビゲーションボタンをタイトルの上に配置（処理中は非表示）
is_processing = st.session_state.get("should_start_generation", False)

if not is_processing:
    col1, col2 = st.columns(2, gap="small")

    with col1:
        if st.button(
            "← 入力画面に戻る",
            key="back_to_download_top",
            use_container_width=True,
        ):
            st.switch_page("src/frontend/components/pages/implementation_page.py")

    with col2:
        if st.button(
            "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
        ):
            st.switch_page("src/frontend/components/pages/gallery_page.py")
else:
    # 処理中は非表示にして、処理中メッセージを表示
    st.info("⏳ スライドを生成中です。しばらくお待ちください...")

st.title("📄 生成結果")

# 必要なセッション情報が存在しない場合、ギャラリーページにリダイレクト
if (
    not hasattr(st.session_state, "app_state")
    or st.session_state.app_state.selected_template is None
    or "selected_format" not in st.session_state
):
    st.switch_page("src/frontend/components/pages/gallery_page.py")

# LLM処理を開始する必要がある場合
if st.session_state.get("should_start_generation", False):
    generate_slides_with_llm()
    # 関数内でst.rerun()が呼ばれるため、ここで処理は終了

template = st.session_state.app_state.selected_template
selected_format = st.session_state.selected_format

if not template:
    st.error("テンプレートが見つかりません。")
    st.stop()

st.subheader(f"📋 {template.name}")

format_options = {
    "PDF": {"label": "📄 PDF", "format": OutputFormat.PDF},
    "HTML": {"label": "🌐 HTML", "format": OutputFormat.HTML},
    "PPTX": {"label": "📊 PPTX", "format": OutputFormat.PPTX},
}

selected_format_enum = format_options[selected_format]["format"]

try:
    # 生成されたMarkdownコンテンツとCSSを取得
    generated_markdown = st.session_state.app_state.generated_markdown

    # 生成されたMarkdownコンテンツの検証
    if not generated_markdown or generated_markdown.strip() == "":
        st.error("❌ 生成されたMarkdownコンテンツが空です。")
        st.error("設定画面に戻って再度お試しください。")
        if st.button("設定画面に戻る", type="primary"):
            st.switch_page("src/frontend/components/pages/implementation_page.py")
        st.stop()

    css_content = template.read_css_content()

    # CSSコンテンツの検証
    if not css_content:
        st.warning("⚠️ CSSコンテンツが見つかりません。デフォルトスタイルを使用します。")
        css_content = "/* Default CSS */"

    # 一時ファイルを作成してMarpServiceを使用
    temp_dir = Path(tempfile.gettempdir()) / "auto-slides"
    temp_dir.mkdir(exist_ok=True)

    temp_md_path = temp_dir / f"{template.id}.md"
    temp_css_path = temp_dir / f"{template.id}.css"

    # マークダウンファイルを作成
    with open(temp_md_path, "w", encoding="utf-8") as f:
        if generated_markdown is None:
            st.error("❌ 生成されたMarkdownコンテンツがNoneです。")
            st.stop()
        f.write(generated_markdown)

    # CSSファイルを作成
    with open(temp_css_path, "w", encoding="utf-8") as f:
        if css_content is None:
            css_content = "/* Default CSS */"
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

    # ダウンロードボタン
    filename = f"{template.id}.{selected_format_enum.value}"

    if selected_format == "PDF":
        download_label = "PDFファイルをダウンロード"
    elif selected_format == "HTML":
        download_label = "HTMLファイルをダウンロード"
    elif selected_format == "PPTX":
        download_label = "PPTXファイルをダウンロード"

    st.download_button(
        label=download_label,
        data=file_data,
        file_name=filename,
        mime=mime_type,
        key="download_button",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # 生成されたMarkdownコンテンツ表示
    with st.expander("📝 生成されたMarkdownコンテンツ", expanded=False):
        st.code(generated_markdown, language="markdown")

    st.divider()

    # プレビュー
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
