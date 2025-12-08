import pytest
from spotify_codes.renderer import Renderer


class TestRenderer:
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = Renderer()
        self.test_output = "test_output.png"

    def test_render_invalid_bar_count(self):
        """Test that render rejects wrong number of bars."""
        bar_heights = [0, 5, 7]

        with pytest.raises(ValueError, match="Expected 23 bars"):
            self.renderer.render(bar_heights, self.test_output)

    def test_render_invalid_bar_height(self):
        """Test that render rejects invalid bar heights."""
        bar_heights = [
            0,
            5,
            7,
            4,
            1,
            4,
            6,
            6,
            0,
            2,
            4,
            8,
            3,
            4,
            6,
            7,
            5,
            5,
            6,
            0,
            5,
            0,
            0,
        ]

        with pytest.raises(ValueError, match="must be between 0 and 7"):
            self.renderer.render(bar_heights, self.test_output)

    def test_color_to_rgb(self):
        """Test color name to RGB conversion."""
        assert self.renderer._color_to_rgb("black") == (0, 0, 0)
        assert self.renderer._color_to_rgb("white") == (255, 255, 255)
        assert self.renderer._color_to_rgb("red") == (255, 0, 0)

    def test_color_to_rgb_invalid(self):
        """Test that invalid color raises error."""
        with pytest.raises(ValueError, match="Unknown color"):
            self.renderer._color_to_rgb("invalid_color")
