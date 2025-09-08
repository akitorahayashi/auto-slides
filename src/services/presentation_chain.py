"""
プレゼンテーション生成チェーン - olm-api直接使用
"""

import json
import os
import asyncio
from string import Template
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st

from src.models.slide_template import SlideTemplate

try:
    from sdk.olm_api_client import OllamaApiClient, MockOllamaApiClient, OllamaClientProtocol
except ImportError:
    raise ImportError("olm-api package is required")


def get_client() -> OllamaClientProtocol:
    """クライアント取得（olm-api推奨パターン）"""
    debug = st.secrets.get("DEBUG", os.getenv("DEBUG", "true")).lower() == "true"
    
    if debug:
        return MockOllamaApiClient(token_delay=0)
    else:
        api_url = st.secrets.get("OLM_API_ENDPOINT", os.getenv("OLM_API_ENDPOINT"))
        if not api_url:
            print("Warning: OLM_API_ENDPOINT not set, using MockOllamaApiClient")
            return MockOllamaApiClient(token_delay=0)
        return OllamaApiClient(api_url=api_url)


def get_model() -> str:
    """モデル名を取得"""
    return st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen3:0.6b"))


def parse_json_response(text: str) -> Dict[str, Any]:
    """JSON形式のレスポンスをパース"""
    try:
        text = text.strip()
        
        # ```json ブロックがある場合はその中身を抽出
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        
        return json.loads(text)
    except (json.JSONDecodeError, ValueError) as e:
        return {"error": f"JSON parse failed: {str(e)}", "raw_text": text}


async def analyze_slides(client: OllamaClientProtocol, template: SlideTemplate) -> Dict[str, Any]:
    """Stage 1: スライド構造分析"""
    prompts_dir = Path("src/static/prompts")
    prompt_path = prompts_dir / "01_analyze_slides.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    
    prompt_template = prompt_path.read_text(encoding="utf-8")
    template_content = template.read_markdown_content()
    
    filled_prompt = Template(prompt_template).substitute(
        template_content=template_content,
        duration_minutes=template.duration_minutes
    )
    
    response = await client.gen_batch(prompt=filled_prompt, model=get_model())
    return parse_json_response(response)


async def generate_content(client: OllamaClientProtocol, script_content: str, analysis: Dict[str, Any], template: SlideTemplate) -> Dict[str, Any]:
    """Stage 2: コンテンツ生成"""
    prompts_dir = Path("src/static/prompts")
    prompt_path = prompts_dir / "02_generate_content.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    
    prompt_template = prompt_path.read_text(encoding="utf-8")
    
    filled_prompt = Template(prompt_template).substitute(
        script_content=script_content,
        slide_analysis=json.dumps(analysis, ensure_ascii=False, indent=2),
        duration_minutes=template.duration_minutes
    )
    
    response = await client.gen_batch(prompt=filled_prompt, model=get_model())
    return parse_json_response(response)


def ensure_placeholder_defaults(data: Dict[str, Any]) -> Dict[str, str]:
    """プレースホルダーのデフォルト値を確保"""
    defaults = {
        "presentation_title": "プレゼンテーション",
        "author_name": "発表者",
        "presentation_date": "2024-01-01",
        "header_title": "プレゼン",
        "company_name": "会社名",
        "main_topic": "メインテーマ",
        "topic_1": "はじめに",
        "topic_2": "内容",
        "topic_3": "詳細",
        "topic_4": "まとめ",
        "topic_1_content": "- 内容1",
        "topic_2_content": "- 内容2", 
        "topic_3_content": "- 内容3",
        "conclusion_content": "- まとめ",
        "code_example": "print('Hello, World!')",
        "math_description": "数式の例",
        "inline_math": "$x = y + z$",
        "block_math": "E = mc^2"
    }
    
    result = defaults.copy()
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = value
            else:
                result[key] = str(value)
    
    return result


def fill_template(template_content: str, placeholder_data: Dict[str, Any]) -> str:
    """テンプレートにプレースホルダーを埋め込み"""
    try:
        # generated_content キーがある場合はその中身を使用
        if isinstance(placeholder_data, dict) and "generated_content" in placeholder_data:
            placeholder_data = placeholder_data["generated_content"]
        
        template = Template(template_content)
        safe_data = ensure_placeholder_defaults(placeholder_data)
        return template.safe_substitute(safe_data)
        
    except Exception as e:
        print(f"Template filling failed: {e}")
        return template_content


async def run_two_stage_chain(script_content: str, template: SlideTemplate) -> str:
    """2段階チェーンを実行"""
    client = get_client()
    
    # Stage 1: スライド分析
    analysis = await analyze_slides(client, template)
    if "error" in analysis:
        raise RuntimeError(f"Stage 1 failed: {analysis['error']}")
    
    # Stage 2: コンテンツ生成
    content = await generate_content(client, script_content, analysis, template)
    if "error" in content:
        raise RuntimeError(f"Stage 2 failed: {content['error']}")
    
    # テンプレート埋め込み
    template_content = template.read_markdown_content()
    placeholder_data = content.get("generated_content", content)
    
    return fill_template(template_content, placeholder_data)


def generate_presentation(script_content: str, template: SlideTemplate) -> str:
    """メイン関数: プレゼンテーション生成"""
    use_two_stage = st.secrets.get("USE_TWO_STAGE_LLM", os.getenv("USE_TWO_STAGE_LLM", "true")).lower() == "true"
    
    if use_two_stage:
        return asyncio.run(run_two_stage_chain(script_content, template))
    else:
        return asyncio.run(run_simple_chain(script_content, template))


async def run_simple_chain(script_content: str, template: SlideTemplate) -> str:
    """シンプルチェーン（フォールバック）"""
    client = get_client()
    
    simple_prompt = f"""
原稿を基にプレースホルダーの内容を生成してください。

原稿:
{script_content}

以下のJSON形式で出力してください:
{{
  "presentation_title": "タイトル",
  "author_name": "発表者", 
  "main_topic": "メインテーマ",
  "topic_1": "トピック1",
  "topic_1_content": "内容1"
}}
"""
    
    response = await client.gen_batch(prompt=simple_prompt, model=get_model())
    content = parse_json_response(response)
    
    if "error" in content:
        raise RuntimeError(f"Simple generation failed: {content['error']}")
    
    template_content = template.read_markdown_content()
    return fill_template(template_content, content)


