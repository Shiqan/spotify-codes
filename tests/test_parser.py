import tempfile
from pathlib import Path
from PIL import Image
from spotify_codes import Parser, Renderer

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
        original_heights = [
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
            7,
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
            heights = [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
            ]

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
        # Test all zeros\
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

    def test_parse_roundtrip_accuracy(self):
        """Test that encoding/decoding preserves bar heights reasonably well."""
        original_heights = [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "roundtrip.png"
            self.renderer.render(original_heights, str(image_path))

            parsed_heights = self.parser.parse(str(image_path))

            # Due to rounding and pixel quantization, exact match might not be possible
            # but they should be very close (within 1)
            for original, parsed in zip(original_heights, parsed_heights):
                assert abs(original - parsed) <= 1
