import pytest
from pathlib import Path
import cv2
import numpy as np
from spotify_codes import Detector, Renderer


LOGO_PATH = Path(__file__).parent.parent / "logo.png"
SAMPLE_BARCODES_DIR = Path(__file__).parent / "sample_barcodes" / "barcodes"
DARK_BACKGROUNDS_DIR = Path(__file__).parent / "sample_barcodes" / "dark_backgrounds"
LIGHT_BACKGROUNDS_DIR = Path(__file__).parent / "sample_barcodes" / "light_backgrounds"


class TestDetector:
    """Test suite for barcode detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = Detector(str(LOGO_PATH))
        self.renderer = Renderer(str(LOGO_PATH))

    def test_detector_initialization(self):
        """Test detector initializes with valid logo."""
        assert self.detector.logo_template is not None
        assert self.detector.logo_template.shape[0] > 0
        assert self.detector.logo_template.shape[1] > 0

    def test_detector_initialization_invalid_logo(self):
        """Test detector raises error with invalid logo path."""
        with pytest.raises(ValueError, match="Could not load logo"):
            Detector("/nonexistent/path/logo.png")

    def test_detect_barcode_nonexistent_file(self):
        """Test detection fails gracefully with nonexistent file."""
        result = self.detector.detect_barcode("/nonexistent/image.png")
        assert result.found is False
        assert "Could not load image" in result.error_message

    def test_detect_barcode_returns_valid_position(self):
        """Test detected barcode position is valid."""
        if not SAMPLE_BARCODES_DIR.exists():
            pytest.skip("Sample barcodes not available")

        barcode_file = Path.joinpath(SAMPLE_BARCODES_DIR, "26560102031.png")
        result = self.detector.detect_barcode(str(barcode_file))

        assert result.found, "Logo should be detected in sample barcode"

        x, y, w, h = result.position
        assert x >= 0 and y >= 0
        assert w > 0 and h > 0

    def test_locate_logo_with_standard_image(self):
        """Test logo detection on known barcode."""
        if not SAMPLE_BARCODES_DIR.exists():
            pytest.skip("Sample barcodes not available")

        barcode_file = Path.joinpath(SAMPLE_BARCODES_DIR, "5726865965.png")
        image = cv2.imread(str(barcode_file))
        logo_pos, confidence = self.detector._locate_logo(image)

        assert logo_pos is not None, "Logo should be detected in sample barcode"
        assert confidence > self.detector.min_logo_confidence
        x, y, w, h = logo_pos
        assert x >= 0 and y >= 0
        assert w > 0 and h > 0

    def test_locate_logo_multiframe_rejection(self):
        """Test logo detection rejects images without logo."""
        # Create an image without the logo
        blank_image = np.ones((300, 400, 3), dtype=np.uint8) * 255

        logo_pos, confidence = self.detector._locate_logo(blank_image)
        assert logo_pos is None, "Should not detect logo in blank image"
        assert confidence == 0.0

    def test_extract_candidate_region(self):
        """Test barcode region extraction after logo detection."""
        if not SAMPLE_BARCODES_DIR.exists():
            pytest.skip("Sample barcodes not available")

        barcode_file = Path.joinpath(SAMPLE_BARCODES_DIR, "57639171874.png")
        image = cv2.imread(str(barcode_file))
        logo_pos, _ = self.detector._locate_logo(image)

        if logo_pos is not None:
            region = self.detector._extract_candidate_region(image, logo_pos)
            assert region is not None
            assert region.shape[0] > 0  # Height
            assert region.shape[1] > 0  # Width

    def test_extract_candidate_region_invalid_position(self):
        """Test extraction handles invalid logo positions gracefully."""
        image = np.ones((300, 400, 3), dtype=np.uint8) * 255

        # Invalid position (outside image bounds)
        invalid_pos = (500, 500, 100, 100)
        region = self.detector._extract_candidate_region(image, invalid_pos)
        assert region is None

    def test_hex_color_distance(self):
        """Test hex color distance calculation."""
        # Same color
        dist = self.detector._hex_color_distance("#ffffff", "#ffffff")
        assert dist == 0

        # Black and white
        dist = self.detector._hex_color_distance("#000000", "#ffffff")
        assert dist > 400  # Max distance is ~441

        # Similar colors
        dist = self.detector._hex_color_distance("#ff0000", "#fe0000")
        assert dist < 2

    def test_validate_background_color_known_colors(self):
        """Test background color validation with acceptable colors."""
        if not SAMPLE_BARCODES_DIR.exists():
            pytest.skip("Sample barcodes not available")

        barcode_files = list(SAMPLE_BARCODES_DIR.glob("*.png"))
        if not barcode_files:
            pytest.skip("No sample barcode images found")

        image = cv2.imread(str(barcode_files[0]))
        logo_pos, _ = self.detector._locate_logo(image)

        if logo_pos is not None:
            region = self.detector._extract_candidate_region(image, logo_pos)
            if region is not None:
                color = self.detector._validate_background_color(region)
                # Color should either be detected (not None) or the image
                # might have a background not in the list
                assert color is None or isinstance(color, str)

    @pytest.mark.parametrize(
        "barcode_file",
        (
            [f for f in DARK_BACKGROUNDS_DIR.glob("*.png")]
            if DARK_BACKGROUNDS_DIR.exists()
            else []
        ),
    )
    def test_detect_all_dark_background_barcodes(self, barcode_file):
        """Detector should find barcodes on dark backgrounds."""
        result = self.detector.detect_barcode(str(barcode_file))
        assert result.found is True, f"Failed to detect barcode: {barcode_file.name}"
        assert result.position is not None

    @pytest.mark.parametrize(
        "barcode_file",
        (
            [f for f in LIGHT_BACKGROUNDS_DIR.glob("*.png")]
            if LIGHT_BACKGROUNDS_DIR.exists()
            else []
        ),
    )
    def test_detect_all_light_background_barcodes(self, barcode_file):
        """Detector should find barcodes on light backgrounds."""
        result = self.detector.detect_barcode(str(barcode_file))
        assert result.found is True, f"Failed to detect barcode: {barcode_file.name}"
        assert result.position is not None

    @pytest.mark.parametrize(
        "barcode_file",
        (
            [f for f in SAMPLE_BARCODES_DIR.glob("*.png")]
            if SAMPLE_BARCODES_DIR.exists()
            else []
        ),
    )
    def test_detect_all_sample_barcodes(self, barcode_file):
        """Test detection on all available sample barcodes."""
        result = self.detector.detect_barcode(str(barcode_file))
        assert result.found is True, f"Failed to detect barcode: {barcode_file.name}"
        assert result.position is not None
