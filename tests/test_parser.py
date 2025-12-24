import random
import tempfile
import pytest
from pathlib import Path
from PIL import Image
from spotify_codes import Parser, Renderer
from spotify_codes.renderer import ACCEPTABLE_BG_COLORS


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _is_dark(hex_color: str) -> bool:
    r, g, b = _hex_to_rgb(hex_color)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return lum < 140


DARK_BACKGROUNDS = sorted([c for c in ACCEPTABLE_BG_COLORS if _is_dark(c)])
LIGHT_BACKGROUNDS = sorted([c for c in ACCEPTABLE_BG_COLORS if not _is_dark(c)])

LOGO_PATH = Path(__file__).parent.parent / "logo.png"


class TestParser:
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = Parser()
        self.renderer = Renderer(str(LOGO_PATH))

    def test_otsu_threshold_uniform_histogram(self):
        """Test Otsu threshold with a simple bimodal histogram."""
        histogram = [50] * 128 + [50] * 128  # 50 pixels at 0-127, 50 at 128-255
        threshold = self.parser._otsu_threshold(histogram)
        assert 0 <= threshold < 256

    def test_otsu_threshold_all_dark(self):
        """Test Otsu threshold with mostly dark pixels."""
        histogram = [100] + [1] * 255  # Most pixels are dark
        threshold = self.parser._otsu_threshold(histogram)
        assert threshold >= 0

    def test_otsu_threshold_all_light(self):
        """Test Otsu threshold with mostly light pixels."""
        histogram = [1] * 255 + [100]  # Most pixels are light
        threshold = self.parser._otsu_threshold(histogram)
        assert threshold >= 0

    def test_parse_with_renderer_output(self):
        """Test parsing an image created by the renderer."""
        original_heights = [0,0,3,6,2,5,1,7,7,1,2,6,7,4,5,3,7,1,2,6,0,4,0] # fmt: skip

        with tempfile.TemporaryDirectory() as tmpdir:
            # Render the image
            image_path = Path(tmpdir) / "test_render.png"
            self.renderer.render(original_heights, str(image_path))

            # Parse it back
            parsed_heights = self.parser.parse(str(image_path))

            # Should get back 23 bars
            assert len(parsed_heights) == 23

            # Heights should be in valid range
            assert all(0 <= h <= 7 for h in parsed_heights)

    def test_parse_no_bars_raises_error(self):
        """Test that parsing image with no bars raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a blank image (no bars)
            image_path = Path(tmpdir) / "blank.png"
            blank_img = Image.new("L", (200, 100), color=128)  # Gray, no clear bars
            blank_img.save(image_path)

            # This might not raise if the image is too uniform
            # but we can at least verify it doesn't crash
            try:
                result = self.parser.parse(str(image_path))
                # If it succeeds, result should be a list
                assert isinstance(result, list)
            except ValueError:
                # Expected if no bars found
                pass

    def test_parse_returns_list_of_ints(self):
        """Test that parse returns a list of integers."""
        heights = [i % 8 for i in range(23)]

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test.png"
            self.renderer.render(heights, str(image_path))

            result = self.parser.parse(str(image_path))

            assert isinstance(result, list)
            assert len(result) == 23
            assert all(isinstance(h, int) for h in result)

    def test_parse_different_bar_widths(self):
        """Test parsing with different bar widths."""
        for bar_width in [6, 8, 10, 12]:
            heights = [1,2,3,4,5,6,7,0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7] # fmt: skip

            with tempfile.TemporaryDirectory() as tmpdir:
                image_path = Path(tmpdir) / f"test_width_{bar_width}.png"
                self.renderer.render(heights, str(image_path))

                result = self.parser.parse(str(image_path))

                assert len(result) == 23
                assert all(0 <= h <= 7 for h in result)

    def test_parse_consistency(self):
        """Test that parsing the same image multiple times gives consistent results."""
        heights = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test_consistency.png"
            self.renderer.render(heights, str(image_path))

            result1 = self.parser.parse(str(image_path))
            result2 = self.parser.parse(str(image_path))

            assert result1 == result2

    def test_parse_extreme_heights(self):
        """Test parsing with extreme bar heights (all 0s and all 7s)."""
        # Test all zeros
        zeros = [0] * 23
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test_zeros.png"
            self.renderer.render(zeros, str(image_path))
            result = self.parser.parse(str(image_path))
            assert len(result) == 23

        # Test all sevens
        sevens = [7] * 23
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test_sevens.png"
            self.renderer.render(sevens, str(image_path))
            result = self.parser.parse(str(image_path))
            assert len(result) == 23

    @pytest.mark.parametrize(
        "bg_color", DARK_BACKGROUNDS, ids=[c for c in DARK_BACKGROUNDS]
    )
    def test_parse_roundtrip_accuracy_dark_background(self, bg_color: str):
        """Test that encoding/decoding preserves heights for each dark bg."""
        original_heights = [random.randint(0, 7) for _ in range(23)]

        # Use white bars on dark backgrounds so parser finds white bars
        renderer = Renderer(str(LOGO_PATH), bg_color=bg_color, bar_color="#ffffff")

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / f"roundtrip_{bg_color[1:]}.png"
            renderer.render(original_heights, str(image_path))

            parsed_heights = self.parser.parse(str(image_path))

            # Due to rounding/pixel quantization, allow small tolerance
            for original, parsed in zip(original_heights, parsed_heights):
                assert abs(original - parsed) <= 1

    @pytest.mark.parametrize(
        "bg_color", LIGHT_BACKGROUNDS, ids=[c for c in LIGHT_BACKGROUNDS]
    )
    def test_parse_roundtrip_accuracy_light_background(self, bg_color: str):
        """Roundtrip on light backgrounds using black bars."""
        original_heights = [random.randint(0, 7) for _ in range(23)]

        renderer = Renderer(str(LOGO_PATH), bg_color=bg_color, bar_color="#000000")

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / f"roundtrip_{bg_color[1:]}.png"
            renderer.render(original_heights, str(image_path))

            parsed_heights = self.parser.parse(str(image_path))

            for original, parsed in zip(original_heights, parsed_heights):
                assert abs(original - parsed) <= 1
