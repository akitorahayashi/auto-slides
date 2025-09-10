import tempfile
import time
import traceback
from pathlib import Path

import streamlit as st
from pdf2image import convert_from_bytes

from src.backend.services import MarpService
from src.protocols.schemas import OutputFormat


class TimeoutError(Exception):
    """Custom timeout error"""

    pass


def run_with_simple_timeout(func, timeout_seconds, *args, **kwargs):
    """
    Simple timeout implementation for Streamlit environment.
    Note: This doesn't actually enforce timeout but logs the expectation.
    Real timeout enforcement would require more complex threading which
    may not work well in Streamlit's execution model.
    """
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            st.warning(
                f"⏱️ 処理に{elapsed:.1f}秒かかりました (制限: {timeout_seconds}秒)"
            )
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(
                f"Operation likely timed out after {elapsed:.1f} seconds (limit: {timeout_seconds}s): {str(e)}"
            )
        raise


def get_progress_text(stage: str, dot_count: int = 1) -> str:
    """進捗に応じてテキストを生成"""
    # ドットアニメーション: 1個 → 2個 → 3個 → なし のサイクル
    dot_patterns = [".", "..", "...", ""]
    dots = dot_patterns[dot_count % 4] if dot_count > 0 else "."

    stage_messages = {
        "analyzing": f"📊 スライド内容を分析中{dots}",
        "composing": f"🎯 スライド構成を決定中{dots}",
        "generating": f"✍️ パラメータを生成中{dots}",
        "building": f"🏗️ スライドを構築中{dots}",
        "combining": f"🔗 スライドを統合中{dots}",
        "completed": "✅ スライドの生成が完了しました！",
    }

    return stage_messages.get(stage, f"スライドを生成中{dots}")


def create_animated_progress_display():
    """アニメーション付きプログレス表示を作成"""
    # セッション状態でアニメーション状態を管理
    if "progress_animation_count" not in st.session_state:
        st.session_state.progress_animation_count = 0
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "analyzing"

    # プログレス表示コンテナ
    progress_container = st.empty()
    progress_bar = st.progress(0)

    return progress_container, progress_bar


def generate_slides_with_llm():
    """LLMを使用してスライドを生成する"""
    script_content = st.session_state.app_state.user_inputs["script_content"]
    template = st.session_state.app_state.selected_template
    generator = st.session_state.app_state.slide_generator

    # タイムアウト設定を読み取り
    chain_timeout = getattr(st.secrets, "CHAIN_TIMEOUT", 600)  # デフォルト10分

    # プログレス表示用のコンテナとプログレスバー
    progress_container = st.empty()
    progress_bar_container = st.empty()

    def progress_callback(stage: str, current: int = 0, total: int = 1):
        """進捗を更新するコールバック"""
        # LLMリクエスト数ベースの進捗計算
        if total > 0:
            progress_value = min(current / total, 1.0)
        else:
            # フォールバック: 従来の段階ベース
            progress_values = {
                "analyzing": 0.2,
                "composing": 0.4,
                "generating": 0.6,
                "building": 0.8,
                "combining": 0.9,
                "completed": 1.0,
            }
            progress_value = progress_values.get(stage, 0.1)

        # アニメーションカウンターを更新
        if "progress_animation_count" not in st.session_state:
            st.session_state.progress_animation_count = 0
        st.session_state.progress_animation_count += 1

        # プログレステキストを更新
        progress_text = get_progress_text(
            stage, st.session_state.progress_animation_count
        )

        progress_container.info(progress_text)
        progress_bar_container.progress(progress_value)

    try:
        # ジェネレーターにコールバックを設定
        try:
            from src.backend.chains.slide_gen_chain import SlideGenChain
        except Exception as import_error:
            st.error(f"❌ Failed to import SlideGenChain: {import_error}")
            raise

        def execute_generation():
            """生成処理を実行する関数"""
            try:
                if hasattr(generator, "llm"):
                    # SlideGenChainの場合、コールバック付きで再作成
                    generator_with_callback = SlideGenChain(
                        generator.llm, progress_callback
                    )

                    # 生成実行
                    return generator_with_callback.invoke_slide_gen_chain(
                        script_content, template
                    )
                else:
                    # モックの場合はそのまま使用（段階的な表示をシミュレート）
                    # モック用の想定LLMリクエスト数
                    mock_total_requests = 5

                    progress_callback("analyzing", 1, mock_total_requests)
                    time.sleep(0.5)
                    progress_callback("composing", 2, mock_total_requests)
                    time.sleep(0.5)
                    progress_callback("generating", 3, mock_total_requests)
                    time.sleep(0.5)
                    progress_callback("building", 4, mock_total_requests)
                    time.sleep(0.5)
                    progress_callback("combining", 5, mock_total_requests)
                    time.sleep(0.5)

                    result = generator.invoke_slide_gen_chain(script_content, template)
                    progress_callback(
                        "completed", mock_total_requests, mock_total_requests
                    )
                    return result
            except Exception as gen_error:
                raise gen_error

        # タイムアウト付きで実行
        generated_markdown = run_with_simple_timeout(execute_generation, chain_timeout)

        # 生成完了後、セッションに保存
        st.session_state.app_state.generated_markdown = generated_markdown

        # 完了メッセージを表示
        progress_container.success("✅ スライドの生成が完了しました！")
        progress_bar_container.progress(1.0)

        # セッション状態をクリア
        if "should_start_generation" in st.session_state:
            del st.session_state.should_start_generation
        if "progress_animation_count" in st.session_state:
            del st.session_state.progress_animation_count

        time.sleep(1)  # 完了メッセージを少し表示
        st.rerun()

    except Exception as e:
        progress_container.empty()
        progress_bar_container.empty()

        # 開発者向け詳細エラー情報
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()

        st.error(f"🚨 **{error_type}**: プレゼンテーション生成に失敗")

        # エラーの詳細情報を表示
        with st.expander("🔍 詳細エラー情報", expanded=True):
            st.code(
                f"Error Type: {error_type}\n\nMessage: {error_message}", language="text"
            )

            # 特定のエラータイプに応じた対処法を表示
            if (
                "timeout" in error_message.lower()
                or "timed out" in error_message.lower()
                or isinstance(e, TimeoutError)
            ):
                st.warning(
                    f"⏱️ **タイムアウトエラー**: LLMの応答に時間がかかりすぎています (制限時間: {chain_timeout}秒)"
                )
                st.info(
                    f"""**対処法:**
- Ollamaサーバーが正常に動作していることを確認してください
- より軽量なモデルを使用することを検討してください  
- `.streamlit/secrets.toml`でCHAIN_TIMEOUT={chain_timeout}を調整してください
- スクリプトの内容を短くすることを検討してください"""
                )
            elif "connection" in error_message.lower():
                st.warning("🔌 **接続エラー**: LLMサービスに接続できません")
                st.info(
                    "- Ollamaが起動していることを確認してください\n- ネットワーク設定を確認してください"
                )
            elif "json" in error_message.lower() or "parse" in error_message.lower():
                st.warning("📄 **解析エラー**: LLMの応答が期待された形式ではありません")
                st.info(
                    "- モデルが適切なJSON形式で応答していない可能性があります\n- プロンプトの調整が必要かもしれません"
                )
            elif (
                "slide_name" in error_message.lower()
                or "keyerror" in error_type.lower()
            ):
                st.warning("🔧 **構造エラー**: LLMの応答に必要なキーが不足しています")
                st.info(
                    """**考えられる原因:**
- LLMが期待されたJSON構造を生成していない
- `slide_name`などの必須フィールドが欠落している
- より具体的なプロンプトが必要な可能性があります
- モデルの能力不足の可能性があります"""
                )
            else:
                st.warning("❓ **不明なエラー**: 予期しない問題が発生しました")

        # トレースバック情報（折りたたみ）
        with st.expander("📋 スタックトレース", expanded=False):
            st.code(error_traceback, language="python")

        # セッション状態情報
        with st.expander("🔧 デバッグ情報", expanded=False):
            debug_info = {
                "Template ID": template.id if template else "None",
                "Script Content Length": len(script_content) if script_content else 0,
                "Generator Type": type(generator).__name__ if generator else "None",
                "Session State Keys": (
                    list(st.session_state.keys())
                    if hasattr(st, "session_state")
                    else []
                ),
                "Timeout Settings": {
                    "Chain Timeout": chain_timeout,
                    "LLM Timeout": getattr(st.secrets, "LLM_TIMEOUT", 300),
                    "Marp Timeout": getattr(st.secrets, "MARP_TIMEOUT", 120),
                },
            }
            st.json(debug_info)

        if st.button(
            "🔄 設定画面に戻って再試行",
            type="primary",
            key="back_to_settings_llm_error",
        ):
            st.switch_page("frontend/components/pages/implementation_page.py")

        # エラーが発生した場合は後続の処理をスキップ
        st.stop()


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
            st.switch_page("frontend/components/pages/implementation_page.py")

    with col2:
        if st.button(
            "🏠 ギャラリーに戻る", key="back_to_gallery_top", use_container_width=True
        ):
            st.switch_page("frontend/components/pages/gallery_page.py")
else:
    # 処理中はナビゲーションボタンを非表示にする
    pass

st.title("📄 生成結果")

# 必要なセッション情報が存在しない場合、ギャラリーページにリダイレクト
if (
    not hasattr(st.session_state, "app_state")
    or st.session_state.app_state.selected_template is None
    or "selected_format" not in st.session_state
):
    st.switch_page("frontend/components/pages/gallery_page.py")

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
        st.error("🚨 **ValidationError**: 生成されたMarkdownコンテンツが空です")

        with st.expander("🔍 詳細エラー情報", expanded=True):
            st.code(f"Generated Markdown: {repr(generated_markdown)}", language="text")
            st.warning(
                "📄 **コンテンツ生成エラー**: LLMが有効なコンテンツを生成できませんでした"
            )
            st.info(
                """**考えられる原因:**
- LLMの応答がタイムアウトした
- スクリプトの内容が短すぎるまたは不明確
- テンプレート関数が正しく実行されなかった
- ネットワークエラーで途中で処理が中断された"""
            )

        # デバッグ情報
        with st.expander("🔧 デバッグ情報", expanded=False):
            debug_info = {
                "Template ID": template.id if template else "None",
                "Template Name": template.name if template else "None",
                "Script Content Length": (
                    len(
                        st.session_state.app_state.user_inputs.get("script_content", "")
                    )
                    if hasattr(st.session_state, "app_state")
                    else 0
                ),
                "Generated Markdown Type": type(generated_markdown).__name__,
                "Generated Markdown Length": (
                    len(generated_markdown) if generated_markdown else 0
                ),
                "Session State Has Generated Markdown": (
                    hasattr(st.session_state.app_state, "generated_markdown")
                    if hasattr(st.session_state, "app_state")
                    else False
                ),
            }
            st.json(debug_info)

        if st.button(
            "🔄 設定画面に戻って再試行",
            type="primary",
            key="back_to_settings_empty_content",
        ):
            st.switch_page("frontend/components/pages/implementation_page.py")
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
    marp_timeout = getattr(st.secrets, "MARP_TIMEOUT", 120)  # デフォルト2分
    pdf_timeout = getattr(st.secrets, "PDF_CONVERSION_TIMEOUT", 60)  # デフォルト1分

    # Marp変換処理を関数として定義
    def generate_file():
        if selected_format == "PDF":
            output_path = marp_service.generate_pdf(f"{template.id}.pdf")
            with open(output_path, "rb") as f:
                return f.read(), "application/pdf"
        elif selected_format == "HTML":
            output_path = marp_service.generate_html(f"{template.id}.html")
            with open(output_path, "rb") as f:
                return f.read(), "text/html"
        elif selected_format == "PPTX":
            output_path = marp_service.generate_pptx(f"{template.id}.pptx")
            with open(output_path, "rb") as f:
                return (
                    f.read(),
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )

    # タイムアウト付きで実行
    with st.spinner(f"{selected_format}生成中..."):
        file_data, mime_type = run_with_simple_timeout(generate_file, marp_timeout)

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
    def generate_preview():
        if selected_format == "PDF":
            # 既存のPDFデータをプレビュー用に使用
            preview_data = file_data
        else:
            # HTML/PPTXは一度PDFに変換してからプレビュー
            preview_path = marp_service.generate_pdf(f"preview_{template.id}.pdf")
            with open(preview_path, "rb") as f:
                preview_data = f.read()

        # PDF to Image変換
        return convert_from_bytes(preview_data)

    with st.spinner("プレビューを準備中..."):
        images = run_with_simple_timeout(generate_preview, pdf_timeout)

    for i, image in enumerate(images):
        st.image(image, caption=f"スライド {i+1}")

except Exception as e:
    error_type = type(e).__name__
    error_message = str(e)
    error_traceback = traceback.format_exc()

    st.error(f"🚨 **{error_type}**: {selected_format}ファイル生成に失敗")

    # エラーの詳細情報を表示
    with st.expander("🔍 詳細エラー情報", expanded=True):
        st.code(
            f"Error Type: {error_type}\n\nMessage: {error_message}", language="text"
        )

        # 特定のエラータイプに応じた対処法を表示
        if (
            "timeout" in error_message.lower()
            or "timed out" in error_message.lower()
            or isinstance(e, TimeoutError)
        ):
            st.warning(
                "⏱️ **タイムアウトエラー**: ファイル変換に時間がかかりすぎています"
            )
            st.info(
                f"""**対処法:**
- `.streamlit/secrets.toml`でMARP_TIMEOUT={marp_timeout}を調整してください
- `.streamlit/secrets.toml`でPDF_CONVERSION_TIMEOUT={pdf_timeout}を調整してください
- より高速なマシンでの実行を検討してください
- Markdownの内容を簡略化することを検討してください"""
            )
        elif "marp" in error_message.lower():
            st.warning("🔧 **Marpエラー**: Marpサービスでファイル変換に失敗")
            st.info(
                "- Marpが正しくインストールされているか確認してください\n- Markdownの構文に問題がないか確認してください"
            )
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            st.warning("🔒 **権限エラー**: ファイルアクセスに失敗")
            st.info(
                "- 一時ディレクトリへの書き込み権限を確認してください\n- ディスクの容量を確認してください"
            )
        elif "pdf2image" in error_message.lower():
            st.warning("🖼️ **PDF変換エラー**: PDFから画像への変換に失敗")
            st.info(
                "- pdf2imageライブラリが正しくインストールされているか確認してください\n- Popplerがインストールされているか確認してください"
            )
        else:
            st.warning("❓ **ファイル変換エラー**: 予期しない問題が発生しました")

    # トレースバック情報（折りたたみ）
    with st.expander("📋 スタックトレース", expanded=False):
        st.code(error_traceback, language="python")

    # デバッグ情報
    with st.expander("🔧 デバッグ情報", expanded=False):
        debug_info = {
            "Selected Format": selected_format,
            "Template ID": template.id if template else "None",
            "Generated Markdown Length": (
                len(generated_markdown) if generated_markdown else 0
            ),
            "CSS Content Length": len(css_content) if css_content else 0,
            "Temp Directory Available": (
                temp_dir.exists() if "temp_dir" in locals() else "Unknown"
            ),
            "Timeout Settings": {
                "Marp Timeout": (
                    marp_timeout if "marp_timeout" in locals() else "Not set"
                ),
                "PDF Conversion Timeout": (
                    pdf_timeout if "pdf_timeout" in locals() else "Not set"
                ),
            },
        }
        st.json(debug_info)
