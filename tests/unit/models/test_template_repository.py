import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.models.slide_template import SlideTemplate
from src.models.template_repository import TemplateRepository


class TestTemplateRepository:
    """Unit tests for TemplateRepository"""

    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.is_dir")
    def test_get_all_templates_empty_directory(self, mock_is_dir, mock_iterdir):
        """Test get_all_templates with empty templates directory"""
        mock_iterdir.return_value = []

        result = TemplateRepository.get_all_templates()

        assert result == []
        mock_iterdir.assert_called_once()

    @patch("src.models.template_repository.SlideTemplate")
    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.is_dir")
    def test_get_all_templates_with_valid_templates(
        self, mock_is_dir, mock_iterdir, mock_slide_template_class
    ):
        """Test get_all_templates with valid templates"""
        # Setup mock directories
        mock_dir1 = MagicMock()
        mock_dir1.name = "template1"
        mock_dir1.is_dir.return_value = True

        mock_dir2 = MagicMock()
        mock_dir2.name = "template2"
        mock_dir2.is_dir.return_value = True

        mock_iterdir.return_value = [mock_dir1, mock_dir2]

        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.exists.return_value = True

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.exists.return_value = True

        mock_slide_template_class.side_effect = [mock_template1, mock_template2]

        result = TemplateRepository.get_all_templates()

        assert len(result) == 2
        assert result[0] == mock_template1
        assert result[1] == mock_template2

        # Verify SlideTemplate was called with correct parameters
        expected_calls = [
            {
                "id": "template1",
                "name": "Template1",
                "description": "Template: template1",
                "template_dir": mock_dir1,
            },
            {
                "id": "template2",
                "name": "Template2",
                "description": "Template: template2",
                "template_dir": mock_dir2,
            },
        ]

        assert mock_slide_template_class.call_count == 2
        for i, call in enumerate(mock_slide_template_class.call_args_list):
            args, kwargs = call
            assert len(args) == 0  # Should be called with keyword arguments
            assert kwargs == expected_calls[i]

    @patch("src.models.template_repository.SlideTemplate")
    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.is_dir")
    def test_get_all_templates_excludes_invalid_templates(
        self, mock_is_dir, mock_iterdir, mock_slide_template_class
    ):
        """Test get_all_templates excludes templates that don't exist"""
        # Setup mock directories
        mock_dir1 = MagicMock()
        mock_dir1.name = "valid_template"
        mock_dir1.is_dir.return_value = True

        mock_dir2 = MagicMock()
        mock_dir2.name = "invalid_template"
        mock_dir2.is_dir.return_value = True

        mock_iterdir.return_value = [mock_dir1, mock_dir2]

        # Setup mock templates - one valid, one invalid
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.exists.return_value = True

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.exists.return_value = False

        mock_slide_template_class.side_effect = [mock_template1, mock_template2]

        result = TemplateRepository.get_all_templates()

        # Only the valid template should be returned
        assert len(result) == 1
        assert result[0] == mock_template1

    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.is_dir")
    def test_get_all_templates_ignores_files(self, mock_is_dir, mock_iterdir):
        """Test get_all_templates ignores files (only processes directories)"""
        # Setup mock items - some files, some directories
        mock_file = MagicMock()
        mock_file.name = "some_file.txt"
        mock_file.is_dir.return_value = False

        mock_dir = MagicMock()
        mock_dir.name = "template_dir"
        mock_dir.is_dir.return_value = True

        mock_iterdir.return_value = [mock_file, mock_dir]

        with patch(
            "src.models.template_repository.SlideTemplate"
        ) as mock_slide_template_class:
            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.exists.return_value = True
            mock_slide_template_class.return_value = mock_template

            result = TemplateRepository.get_all_templates()

            # Only the directory should be processed
            assert len(result) == 1
            mock_slide_template_class.assert_called_once_with(
                id="template_dir",
                name="Template Dir",
                description="Template: template_dir",
                template_dir=mock_dir,
            )

    def test_name_formatting(self):
        """Test that template names are formatted correctly"""
        with (
            patch("pathlib.Path.iterdir") as mock_iterdir,
            patch(
                "src.models.template_repository.SlideTemplate"
            ) as mock_slide_template_class,
        ):

            # Setup mock directory with underscores in name
            mock_dir = MagicMock()
            mock_dir.name = "my_awesome_template"
            mock_dir.is_dir.return_value = True
            mock_iterdir.return_value = [mock_dir]

            mock_template = MagicMock(spec=SlideTemplate)
            mock_template.exists.return_value = True
            mock_slide_template_class.return_value = mock_template

            TemplateRepository.get_all_templates()

            # Verify the name was formatted correctly (underscores replaced with spaces, title case)
            mock_slide_template_class.assert_called_once_with(
                id="my_awesome_template",
                name="My Awesome Template",
                description="Template: my_awesome_template",
                template_dir=mock_dir,
            )

    @patch("src.models.template_repository.TemplateRepository.get_all_templates")
    def test_get_template_by_id_found(self, mock_get_all_templates):
        """Test get_template_by_id when template exists"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        mock_get_all_templates.return_value = [mock_template1, mock_template2]

        result = TemplateRepository.get_template_by_id("template2")

        assert result == mock_template2
        mock_get_all_templates.assert_called_once()

    @patch("src.models.template_repository.TemplateRepository.get_all_templates")
    def test_get_template_by_id_not_found(self, mock_get_all_templates):
        """Test get_template_by_id when template doesn't exist"""
        # Setup mock templates
        mock_template1 = MagicMock(spec=SlideTemplate)
        mock_template1.id = "template1"

        mock_template2 = MagicMock(spec=SlideTemplate)
        mock_template2.id = "template2"

        mock_get_all_templates.return_value = [mock_template1, mock_template2]

        result = TemplateRepository.get_template_by_id("nonexistent")

        assert result is None
        mock_get_all_templates.assert_called_once()

    @patch("src.models.template_repository.TemplateRepository.get_all_templates")
    def test_get_template_by_id_empty_repository(self, mock_get_all_templates):
        """Test get_template_by_id with empty repository"""
        mock_get_all_templates.return_value = []

        result = TemplateRepository.get_template_by_id("any_id")

        assert result is None
        mock_get_all_templates.assert_called_once()

    def test_integration_with_real_filesystem(self):
        """Integration test with real filesystem"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock templates directory structure
            templates_dir = Path(temp_dir) / "src" / "templates"
            templates_dir.mkdir(parents=True)

            # Create a valid template
            valid_template_dir = templates_dir / "valid_template"
            valid_template_dir.mkdir()
            (valid_template_dir / "content.md").write_text("# Test")
            (valid_template_dir / "theme.css").write_text("body { }")

            # Create an invalid template (missing files)
            invalid_template_dir = templates_dir / "invalid_template"
            invalid_template_dir.mkdir()

            # Create a non-directory item
            (templates_dir / "not_a_template.txt").write_text("test")

            # Patch the templates directory path
            with patch("src.models.template_repository.Path") as mock_path_class:
                mock_path_class.return_value = templates_dir

                result = TemplateRepository.get_all_templates()

                # Should only return the valid template
                assert len(result) == 1
                assert result[0].id == "valid_template"
                assert result[0].name == "Valid Template"
                assert result[0].description == "Template: valid_template"
                assert result[0].template_dir == valid_template_dir

                # Test get_template_by_id
                found_template = TemplateRepository.get_template_by_id("valid_template")
                assert found_template is not None
                assert found_template.id == "valid_template"

                not_found_template = TemplateRepository.get_template_by_id(
                    "invalid_template"
                )
                assert not_found_template is None
