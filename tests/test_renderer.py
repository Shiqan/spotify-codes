import pytest
from pathlib import Path
from spotify_codes import Renderer

LOGO_PATH = Path(__file__).parent.parent / "logo.png"


class TestRenderer:
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = Renderer(str(LOGO_PATH))
        self.test_output = "test_output.png"

    def test_render_invalid_bar_count(self):
        """Test that render rejects wrong number of bars."""
        bar_heights = [0, 5, 7]

        with pytest.raises(ValueError, match="Expected 23 bars"):
            self.renderer.render(bar_heights, self.test_output)

    def test_render_invalid_bar_height(self):
        """Test that render rejects invalid bar heights."""
        bar_heights = [0,5,7,4,1,4,6,6,0,2,4,8,3,4,6,7,5,5,6,0,5,0,0] # fmt: skip

        with pytest.raises(ValueError, match="must be between 0 and 7"):
            self.renderer.render(bar_heights, self.test_output)

    def test_is_hex_color(self):
        """Test is hex color."""
        assert self.renderer._is_hex_color("#000000") == True
        assert self.renderer._is_hex_color("#ffffff") == True
        assert self.renderer._is_hex_color("#ff0000") == True
        assert self.renderer._is_hex_color("#00ff00") == True
        assert self.renderer._is_hex_color("#0000ff") == True

    def test_invalid_is_hex_color(self):
        """Test that invalid hex colors raises error."""
        assert self.renderer._is_hex_color("invalid") == False
        assert self.renderer._is_hex_color("color") == False
        assert self.renderer._is_hex_color("white") == False

    def test_validate_bg_color(self):
        """Test background color validation."""
        colors = [
            "#ffffff",
            "#010101",
            "#3c94f0",
            "#4b23f2",
            "#2a48b4",
            "#1a3366",
            "#8fbbca",
            "#78e9d7",
            "#24e07d",
            "#27ef3a",
            "#368a7d",
            "#0b664f",
            "#afe8bd",
            "#baed54",
            "#fdbc59",
            "#f4dc31",
            "#f88d25",
            "#84482f",
            "#c18b7f",
            "#c87951",
            "#fc572c",
            "#fc2d29",
            "#f40d2f",
            "#8d0732",
            "#fec1c9",
            "#b091c1",
            "#fb6c98",
            "#f91d9f",
            "#b31990",
            "#543651",
        ]

        for color in colors:
            assert self.renderer._validate_bg_color(color) == color

    def test_validate_bar_color(self):
        """Test bar color validation."""
        assert self.renderer._validate_bar_color("#000000") == "#000000"
        assert self.renderer._validate_bar_color("#ffffff") == "#ffffff"
        assert self.renderer._validate_bar_color("#FFFFFF") == "#ffffff"

    def test_validate_bg_color_invalid(self):
        """Test that invalid bg color raises error."""
        with pytest.raises(ValueError, match="Invalid background color"):
            self.renderer._validate_bg_color("invalid")