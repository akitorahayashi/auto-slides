from string import Template
from typing import Any, Dict

from src.models.slide_template import SlideTemplate


class PlaceholderService:
    """
    テンプレートのplaceholder置換を行うサービスクラス
    将来的にLLMに統合される機能をMockで実装
    """

    def __init__(self):
        pass

    def fill_placeholders(self, template: SlideTemplate, data: Dict[str, Any]) -> str:
        """
        テンプレートのplaceholderをdataで置換したMarkdownコンテンツを返す

        Args:
            template: 置換対象のテンプレート
            data: placeholder名とその値のマッピング

        Returns:
            placeholderが置換されたMarkdownコンテンツ
        """
        markdown_content = template.read_markdown_content()
        template_obj = Template(markdown_content)

        try:
            return template_obj.substitute(data)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise ValueError(f"必要なplaceholder '{missing_key}' が見つかりません")
        except Exception as e:
            raise ValueError(f"テンプレート置換エラー: {str(e)}")

    def get_placeholder_names(self, template: SlideTemplate) -> list[str]:
        """
        テンプレートに含まれるplaceholder名のリストを取得

        Args:
            template: 解析対象のテンプレート

        Returns:
            placeholder名のリスト
        """
        import re

        markdown_content = template.read_markdown_content()

        # ${...} パターンのplaceholderを検出
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, markdown_content)

        # 重複を除いて返す
        return list(set(matches))

    def create_mock_data(self, placeholder_names: list[str]) -> Dict[str, str]:
        """
        placeholderのリストからMockデータを生成
        将来的にはLLMがコンテンツを生成する部分

        Args:
            placeholder_names: placeholder名のリスト

        Returns:
            Mock値のマッピング
        """
        mock_data_map = {
            "presentation_title": "AI技術の現状と未来",
            "author_name": "山田太郎",
            "presentation_date": "2025年9月8日",
            "header_title": "AI技術セミナー",
            "company_name": "テック株式会社",
            "main_topic": "人工知能の可能性を探る",
            "topic_1": "機械学習の基礎",
            "topic_2": "深層学習の応用",
            "topic_3": "実用的なAIサービス",
            "topic_4": "まとめと今後の展望",
            "topic_1_content": "- 教師あり学習\n- 教師なし学習\n- 強化学習の基本概念",
            "topic_2_content": "- ニューラルネットワーク\n- CNNとRNN\n- 画像認識と自然言語処理への応用",
            "topic_3_content": "- チャットボット\n- 画像生成AI\n- 音声認識システム",
            "conclusion_content": "- AI技術は急速に発展中\n- ビジネスへの活用が進む\n- 倫理的な課題も重要",
            "speaker_note_1": "ここで具体例を示しながら説明する",
            "code_example": "import tensorflow as tf\nmodel = tf.keras.Sequential()",
            "math_description": "AIでは様々な数式が使用されます。",
            "inline_math": "$f(x) = wx + b$",
            "block_math": r"\sigma(x) = \frac{1}{1 + e^{-x}}",
        }

        result = {}
        for name in placeholder_names:
            if name in mock_data_map:
                result[name] = mock_data_map[name]
            else:
                # デフォルト値
                result[name] = f"[{name}のサンプル内容]"

        return result
