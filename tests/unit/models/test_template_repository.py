from unittest.mock import MagicMock, patch

from src.models.slide_template import SlideTemplate


class TestTemplateRepository:
    """Unit tests for TemplateRepository using MockTemplateRepository"""

    def test_get_all_templates_empty_repository(self, mock_template_repository):
        """Test get_all_templates with empty templates repository"""
        result = mock_template_repository.get_all_templates()
        assert result == []

    def test_get_all_templates_with_valid_templates(self, mock_template_repository):
        """Test get_all_templates with valid templates"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"
        mock_template1.name = "Template 1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"
        mock_template2.name = "Template 2"

        with patch.object(
            mock_template_repository,
            "get_all_templates",
            return_value=[mock_template1, mock_template2],
        ):
            result = mock_template_repository.get_all_templates()

            assert len(result) == 2
            assert result[0] == mock_template1
            assert result[1] == mock_template2

    def test_get_all_templates_with_real_sample_template(
        self, mock_template_repository_with_sample
    ):
        """Test get_all_templates with the real sample template"""
        result = mock_template_repository_with_sample.get_all_templates()

        assert len(result) == 1
        template = result[0]
        assert template.id == "k2g4h1x9"
        assert template.name == "サンプルテンプレート"
        assert template.description == "4トピック構成のベーシックなプレゼンテーション"
        assert template.duration_minutes == 10

    def test_get_template_by_id_found(self, mock_template_repository):
        """Test get_template_by_id when template exists"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        with patch.object(
            mock_template_repository,
            "get_all_templates",
            return_value=[mock_template1, mock_template2],
        ):
            result = mock_template_repository.get_template_by_id("template2")
            assert result == mock_template2

    def test_get_template_by_id_not_found(self, mock_template_repository):
        """Test get_template_by_id when template doesn't exist"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        with patch.object(
            mock_template_repository,
            "get_all_templates",
            return_value=[mock_template1, mock_template2],
        ):
            result = mock_template_repository.get_template_by_id("nonexistent")
            assert result is None

    def test_get_template_by_id_empty_repository(self, mock_template_repository):
        """Test get_template_by_id with empty repository"""
        result = mock_template_repository.get_template_by_id("any_id")
        assert result is None

    def test_get_template_by_id_with_sample_template(
        self, mock_template_repository_with_sample
    ):
        """Test get_template_by_id with the real sample template"""
        result = mock_template_repository_with_sample.get_template_by_id("k2g4h1x9")

        assert result is not None
        assert result.id == "k2g4h1x9"
        assert result.name == "サンプルテンプレート"

        # Test with non-existent ID
        not_found = mock_template_repository_with_sample.get_template_by_id(
            "nonexistent"
        )
        assert not_found is None
