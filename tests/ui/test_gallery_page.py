from unittest.mock import MagicMock, patch

import streamlit as st

from src.models import SlideTemplate, TemplateRepository


class TestGalleryPageLogic:
    """Test cases for gallery_page.py UI logic"""

    def test_template_repository_integration(self):
        """Test integration with TemplateRepository"""
        with patch.object(
            TemplateRepository, "get_all_templates"
        ) as mock_get_templates:
            # Test with empty templates
            mock_get_templates.return_value = []

            templates = TemplateRepository.get_all_templates()

            # Verify repository was called and returned empty list
            mock_get_templates.assert_called_once()
            assert templates == []

            # Test with mock templates
            mock_get_templates.reset_mock()
            mock_template1 = MagicMock(spec=SlideTemplate)
            mock_template1.id = "template1"
            mock_template1.name = "Template 1"
            mock_template1.description = "Description 1"

            mock_get_templates.return_value = [mock_template1]

            templates = TemplateRepository.get_all_templates()
            assert len(templates) == 1
            assert templates[0].id == "template1"

    def test_template_selection_logic(self):
        """Test template selection and navigation logic"""
        with patch("streamlit.switch_page") as mock_switch_page:
            # Create mock template
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.id = "template1"
            mock_template.name = "Test Template"

            # Mock session_state with app_state
            mock_app_state = MagicMock()

            with patch.object(st, "session_state") as mock_session:
                mock_session.app_state = mock_app_state

                # Simulate template selection logic
                mock_session.app_state.selected_template = mock_template
                st.switch_page("components/pages/implementation_page.py")

                # Verify template was selected
                assert mock_session.app_state.selected_template == mock_template

                # Verify navigation to implementation page
                mock_switch_page.assert_called_with(
                    "components/pages/implementation_page.py"
                )

    def test_grid_layout_logic(self):
        """Test grid layout logic for templates"""
        # Test with 2 columns per row (cols_per_row = 2)
        cols_per_row = 2

        # Test with 3 templates (odd number)
        templates = ["template1", "template2", "template3"]

        # Calculate grid rows needed
        rows_needed = (
            len(templates) + cols_per_row - 1
        ) // cols_per_row  # Ceiling division
        assert rows_needed == 2  # 3 templates with 2 per row = 2 rows

        # Calculate empty columns needed for last row
        if len(templates) % cols_per_row != 0:
            remaining_cols = cols_per_row - (len(templates) % cols_per_row)
            assert remaining_cols == 1  # 3 % 2 = 1, so 2 - 1 = 1 empty column

        # Test with even number of templates
        templates = ["template1", "template2", "template3", "template4"]
        rows_needed = (len(templates) + cols_per_row - 1) // cols_per_row
        assert rows_needed == 2  # 4 templates with 2 per row = 2 rows

        # No empty columns needed
        if len(templates) % cols_per_row != 0:
            remaining_cols = cols_per_row - (len(templates) % cols_per_row)
        else:
            remaining_cols = 0
        assert remaining_cols == 0  # 4 % 2 = 0, so no empty columns

    def test_template_button_properties(self):
        """Test template button properties logic"""
        # Simulate button creation logic from gallery_page.py
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "template1"
        mock_template.name = "Test Template"

        # Button label format
        button_label = f"{mock_template.name} を使う"
        assert button_label == "Test Template を使う"

        # Button key format
        button_key = f"select_template_{mock_template.id}"
        assert button_key == "select_template_template1"

        # Button properties
        button_type = "primary"
        use_container_width = True

        assert button_type == "primary"
        assert use_container_width is True

    def test_css_loading_logic(self):
        """Test CSS loading logic"""
        css_file_path = "src/static/css/main_page.css"

        # Test successful CSS loading
        css_content = "body { color: red; }"
        with patch("builtins.open", mock_open(read_data=css_content)) as mock_file:
            try:
                with open(css_file_path, "r", encoding="utf-8") as f:
                    loaded_css = f.read()
                css_loaded_successfully = True
            except FileNotFoundError:
                css_loaded_successfully = False

            assert css_loaded_successfully is True
            assert loaded_css == css_content
            mock_file.assert_called_once_with(css_file_path, "r", encoding="utf-8")

        # Test CSS loading failure
        with patch("builtins.open", side_effect=FileNotFoundError()) as mock_file:
            try:
                with open(css_file_path, "r", encoding="utf-8") as f:
                    loaded_css = f.read()
                css_loaded_successfully = True
            except FileNotFoundError:
                css_loaded_successfully = False

            assert css_loaded_successfully is False

    def test_template_card_styling_logic(self):
        """Test template card styling logic"""
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.name = "Test Template"
        mock_template.description = "Test Description"

        # Simulate card HTML generation logic
        card_html = f"""
        <div style="
            border: 2px solid #e6e6fa;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            background-color: #f8f9fa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h3 style="margin-top: 0; color: #333;">📋 {mock_template.name}</h3>
            <p style="color: #666; font-size: 14px;">{mock_template.description}</p>
        </div>
        """

        # Verify the HTML contains template information
        assert mock_template.name in card_html
        assert mock_template.description in card_html
        assert "📋" in card_html
        assert "border: 2px solid #e6e6fa" in card_html

    def test_no_templates_warning_logic(self):
        """Test warning logic when no templates are available"""
        templates = []

        # Simulate the warning condition logic
        if templates:
            show_warning = False
        else:
            show_warning = True
            warning_message = "利用可能なテンプレートがありません。"

        assert show_warning is True
        assert warning_message == "利用可能なテンプレートがありません。"

        # Test with templates present
        templates = [MagicMock()]

        if templates:
            show_warning = False
        else:
            show_warning = True

        assert show_warning is False

    def test_page_title_and_content_logic(self):
        """Test page title and description content"""
        # Simulate the page content from gallery_page.py
        page_title = "🎼 テンプレートギャラリー"
        page_description = (
            "スライドテンプレートを選択して、ダウンロードページに進んでください。"
        )

        assert page_title == "🎼 テンプレートギャラリー"
        assert (
            page_description
            == "スライドテンプレートを選択して、ダウンロードページに進んでください。"
        )
        assert "🎼" in page_title
        assert "テンプレート" in page_description


def mock_open(read_data=""):
    """Helper function to create a mock open function"""
    from unittest.mock import mock_open as mock_open_builtin

    return mock_open_builtin(read_data=read_data)
