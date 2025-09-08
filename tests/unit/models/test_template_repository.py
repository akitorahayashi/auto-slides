from unittest.mock import MagicMock, patch

from src.models.slide_template import SlideTemplate
from src.models.template_repository import TemplateRepository


class TestTemplateRepository:
    """Unit tests for TemplateRepository"""

    def test_get_all_templates_empty_directory(self, mock_template_repository):
        """Test get_all_templates with empty templates directory"""
        result = mock_template_repository.get_all_templates()
        assert result == []

    def test_get_all_templates_with_valid_templates(self):
        """Test get_all_templates with valid templates"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"
        mock_template1.exists.return_value = True

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"
        mock_template2.exists.return_value = True

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template1, mock_template2]

            result = TemplateRepository.get_all_templates()

            assert len(result) == 2
            assert result[0] == mock_template1
            assert result[1] == mock_template2

    def test_get_all_templates_excludes_invalid_templates(self):
        """Test get_all_templates excludes templates that don't exist"""
        # Setup mock templates - one valid, one invalid
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "valid_template"
        mock_template1.exists.return_value = True

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template1]

            result = TemplateRepository.get_all_templates()

            # Only the valid template should be returned
            assert len(result) == 1
            assert result[0] == mock_template1

    def test_get_all_templates_ignores_files(self):
        """Test get_all_templates ignores files (only processes directories)"""
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "template_dir"
        mock_template.exists.return_value = True

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template]

            result = TemplateRepository.get_all_templates()

            # Only the directory should be processed
            assert len(result) == 1
            assert result[0] == mock_template

    def test_name_formatting(self):
        """Test that template names are formatted correctly"""
        mock_template = MagicMock(spec=SlideTemplate)
        mock_template.id = "my_awesome_template"
        mock_template.name = "My Awesome Template"
        mock_template.exists.return_value = True

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template]

            result = TemplateRepository.get_all_templates()

            assert len(result) == 1
            assert result[0].name == "My Awesome Template"

    def test_get_template_by_id_found(self):
        """Test get_template_by_id when template exists"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template1, mock_template2]

            result = TemplateRepository.get_template_by_id("template2")

            assert result == mock_template2

    def test_get_template_by_id_not_found(self):
        """Test get_template_by_id when template doesn't exist"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        with patch(
            "src.models.template_repository.TemplateRepository._get_all_templates"
        ) as mock_get_all:
            mock_get_all.return_value = [mock_template1, mock_template2]

            result = TemplateRepository.get_template_by_id("nonexistent")

            assert result is None

    def test_get_template_by_id_empty_repository(self, mock_template_repository):
        """Test get_template_by_id with empty repository"""
        result = mock_template_repository.get_template_by_id("any_id")
        assert result is None
