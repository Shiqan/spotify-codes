"""Integration tests for the complete barcode pipeline."""

import random
import tempfile
from pathlib import Path
import pytest
from spotify_codes import Encoder, Decoder, Renderer, Parser
from spotify_codes.renderer import ACCEPTABLE_BG_COLORS


def _is_dark(hex_color: str) -> bool:
    """Check if a hex color is dark."""
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return lum < 140


LOGO_PATH = Path(__file__).parent.parent / "logo.png"
DARK_BACKGROUNDS = [c for c in ACCEPTABLE_BG_COLORS if _is_dark(c)]
LIGHT_BACKGROUNDS = [c for c in ACCEPTABLE_BG_COLORS if not _is_dark(c)]


class TestIntegration:
    """Integration tests for encoding/rendering/parsing/decoding pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = Encoder()
        self.decoder = Decoder()
        self.parser = Parser()

    @pytest.mark.parametrize("bg_color", DARK_BACKGROUNDS, ids=DARK_BACKGROUNDS)
    def test_encode_render_parse_decode_dark_background(self, bg_color: str):
        """
        Full pipeline integration test with dark backgrounds using white bars.

        For every dark background color, verify we can:
        1. Generate a random media reference ID
        2. Encode it to bar heights
        3. Render to an image with white bars on the dark background
        4. Parse the image back to bar heights
        5. Decode back to the original media reference ID
        """
        # Generate random media reference ID (must be 11 digits)
        media_ref = random.randint(10000000000, 99999999999)

        # Encode to bar heights
        bar_heights = self.encoder.encode(media_ref)
        assert len(bar_heights) == 23, "Encoder should produce 23 bar heights"

        # Create renderer with white bars on dark background
        renderer = Renderer(str(LOGO_PATH), bg_color=bg_color, bar_color="#ffffff")

        # Render to image
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / f"test_{media_ref}_{bg_color[1:]}.png"
            renderer.render(bar_heights, str(image_path))

            # Verify image was created
            assert image_path.exists(), f"Image not created at {image_path}"

            # Parse back from image
            parsed_heights = self.parser.parse(str(image_path))
            assert len(parsed_heights) == 23, "Parser should extract 23 bar heights"

            # Verify parsed heights match original (with small tolerance for rounding)
            for original, parsed in zip(bar_heights, parsed_heights):
                assert abs(original - parsed) <= 1, (
                    f"Bar height mismatch for {bg_color} with white bars: "
                    f"expected {original}, got {parsed}"
                )

            # Decode back to media reference
            decoded_ref = self.decoder.decode(parsed_heights)
            assert decoded_ref == media_ref, (
                f"Decoded reference mismatch for {bg_color}: "
                f"expected {media_ref}, got {decoded_ref}"
            )

    @pytest.mark.parametrize("bg_color", LIGHT_BACKGROUNDS, ids=LIGHT_BACKGROUNDS)
    def test_encode_render_parse_decode_light_background(self, bg_color: str):
        """
        Full pipeline integration test with light backgrounds using black bars.

        For every light background color, verify we can:
        1. Generate a random media reference ID
        2. Encode it to bar heights
        3. Render to an image with black bars on the light background
        4. Parse the image back to bar heights
        5. Decode back to the original media reference ID
        """
        # Generate random media reference ID (must be 11 digits)
        media_ref = random.randint(10000000000, 99999999999)

        # Encode to bar heights
        bar_heights = self.encoder.encode(media_ref)
        assert len(bar_heights) == 23, "Encoder should produce 23 bar heights"

        # Create renderer with black bars on light background
        renderer = Renderer(str(LOGO_PATH), bg_color=bg_color, bar_color="#000000")

        # Render to image
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / f"test_{media_ref}_{bg_color[1:]}.png"
            renderer.render(bar_heights, str(image_path))

            # Verify image was created
            assert image_path.exists(), f"Image not created at {image_path}"

            # Parse back from image
            parsed_heights = self.parser.parse(str(image_path))
            assert len(parsed_heights) == 23, "Parser should extract 23 bar heights"

            # Verify parsed heights match original (with small tolerance for rounding)
            for original, parsed in zip(bar_heights, parsed_heights):
                assert abs(original - parsed) <= 1, (
                    f"Bar height mismatch for {bg_color} with black bars: "
                    f"expected {original}, got {parsed}"
                )

            # Decode back to media reference
            decoded_ref = self.decoder.decode(parsed_heights)
            assert decoded_ref == media_ref, (
                f"Decoded reference mismatch for {bg_color}: "
                f"expected {media_ref}, got {decoded_ref}"
            )
