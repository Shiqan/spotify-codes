from typing import Optional, Tuple
from dataclasses import dataclass
import cv2
import numpy as np
from .renderer import ACCEPTABLE_BG_COLORS


@dataclass
class BarcodeResult:
    """Result of barcode detection and parsing."""

    found: bool
    position: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
    logo_confidence: float = 0.0
    error_message: str = ""


class Detector:
    """Detects and extracts Spotify barcodes from images."""

    def __init__(
        self,
        logo_path: str,
        min_logo_confidence: float = 0.4,
    ):
        """
        Initialize detector with logo template.

        Args:
            logo_path: Path to the Spotify logo image
            min_logo_confidence: Minimum confidence threshold for logo detection (0-1)
        """
        self.logo_template = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
        if self.logo_template is None:
            raise ValueError(f"Could not load logo from {logo_path}")

        self.min_logo_confidence = min_logo_confidence

    def detect_barcode(
        self,
        image_path: str,
    ) -> BarcodeResult:
        """
        Detect and parse a barcode from an image.

        Args:
            image_path: Path to the image file

        Returns:
            BarcodeResult containing detection status and data
        """
        try:
            # Read image
            image_cv = cv2.imread(image_path)
            if image_cv is None:
                return BarcodeResult(
                    found=False,
                    error_message=f"Could not load image from {image_path}",
                )

            # Step 1: Locate logo
            logo_pos, logo_confidence = self._locate_logo(image_cv)
            if logo_pos is None:
                return BarcodeResult(
                    found=False,
                    logo_confidence=0.0,
                    error_message="Logo not detected in image",
                )

            # Step 2: Extract candidate region
            candidate_region = self._extract_candidate_region(image_cv, logo_pos)
            if candidate_region is None:
                return BarcodeResult(
                    found=False,
                    logo_confidence=logo_confidence,
                    error_message="Could not extract candidate region",
                )

            # Step 3: Validate background color
            bg_color = self._validate_background_color(candidate_region)
            if bg_color is None:
                return BarcodeResult(
                    found=False,
                    logo_confidence=logo_confidence,
                    error_message="Background color not in acceptable list",
                )

            # Barcode considered found based on logo + background
            x, y, w, h = logo_pos
            return BarcodeResult(
                found=True,
                position=(x, y, w + candidate_region.shape[1], h),
                logo_confidence=logo_confidence,
            )

        except Exception as e:
            return BarcodeResult(
                found=False,
                error_message=f"Unexpected error: {str(e)}",
            )

    def _locate_logo(
        self, image: np.ndarray
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Locate the Spotify logo in the image using template matching.

        Returns:
            Tuple of (position, confidence) where position is (x, y, w, h)
            or (None, 0) if not found with sufficient confidence
        """
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Search across the full image; barcode can appear anywhere
        roi_gray = image_gray

        # Try matching at a range of scales with normalized correlation
        best_val = -1.0
        best_loc = None
        best_scale = 1.0

        for scale in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            logo_scaled = cv2.resize(
                self.logo_template,
                (
                    int(self.logo_template.shape[1] * scale),
                    int(self.logo_template.shape[0] * scale),
                ),
            )

            if (
                logo_scaled.shape[0] > roi_gray.shape[0]
                or logo_scaled.shape[1] > roi_gray.shape[1]
            ):
                continue

            result = cv2.matchTemplate(roi_gray, logo_scaled, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_scale = scale

        # With TM_CCOEFF_NORMED, max_val is already in [-1, 1]; use it directly
        confidence = best_val if best_val is not None else 0.0

        if best_loc is None or confidence < self.min_logo_confidence:
            return None, 0.0

        # Variance gate: matched patch must have texture/contrast
        px, py = best_loc
        ph = int(self.logo_template.shape[0] * best_scale)
        pw = int(self.logo_template.shape[1] * best_scale)
        patch = roi_gray[py : py + ph, px : px + pw]
        if patch.size == 0 or float(patch.std()) < 10.0:
            return None, 0.0

        # Convert ROI-relative location to full-image coordinates
        x = px
        y = py
        w_box = pw
        h_box = ph

        return (x, y, w_box, h_box), confidence

    def _extract_candidate_region(
        self, image: np.ndarray, logo_pos: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Extract the barcode region to the right of the logo.

        Args:
            image: OpenCV image
            logo_pos: (x, y, w, h) of detected logo

        Returns:
            Cropped image containing the barcode, or None if invalid
        """
        x, y, w, h = logo_pos
        height, width = image.shape[:2]

        # Estimate barcode region: starts after logo, extends to the right
        crop_x = x + w + 5  # Small margin after logo
        crop_y = max(0, y)

        # Barcode height should be similar to logo; width roughly several times logo width
        crop_h = h
        estimated_bar_width = min(width - crop_x - 10, max(100, w * 6))
        crop_w = estimated_bar_width

        # Validate dimensions
        if crop_x >= width or crop_y >= height or crop_w <= 0 or crop_h <= 0:
            return None

        # Ensure we don't go out of bounds
        crop_w = min(crop_w, width - crop_x)
        crop_h = min(crop_h, height - crop_y)

        # if crop_w < 20 or crop_h < 15:
        #     return None

        return image[crop_y : crop_y + crop_h, crop_x : crop_x + crop_w]

    def _validate_background_color(self, region: np.ndarray) -> Optional[str]:
        """
        Validate that the background color matches acceptable colors.

        Args:
            region: Cropped barcode region (BGR)

        Returns:
            The detected background color hex string, or None if invalid
        """
        h, w = region.shape[:2]
        edge_samples = []

        # Sample edges more comprehensively
        margin = min(w // 8, h // 8, 15)

        # Sample top edge
        for y in range(0, min(margin, h)):
            for x in range(0, w, max(1, w // 8)):
                edge_samples.append(region[y, x])

        # Sample bottom edge
        for y in range(max(0, h - margin), h):
            for x in range(0, w, max(1, w // 8)):
                edge_samples.append(region[y, x])

        # Sample left edge
        for y in range(0, h, max(1, h // 8)):
            for x in range(0, min(margin, w)):
                edge_samples.append(region[y, x])

        # Sample right edge
        for y in range(0, h, max(1, h // 8)):
            for x in range(max(0, w - margin), w):
                edge_samples.append(region[y, x])

        if len(edge_samples) == 0:
            return None

        edge_samples = np.array(edge_samples)
        dominant_color_bgr = edge_samples.mean(axis=0).astype(int)

        # Convert BGR to RGB
        r, g, b = dominant_color_bgr[2], dominant_color_bgr[1], dominant_color_bgr[0]

        # Convert to hex
        detected_hex = f"#{r:02x}{g:02x}{b:02x}"

        # Check if it matches any acceptable color with generous tolerance
        for acceptable_color in ACCEPTABLE_BG_COLORS:
            if self._hex_color_distance(detected_hex, acceptable_color) < 80:
                return acceptable_color

        return None

    def _hex_color_distance(self, hex1: str, hex2: str) -> float:
        """Calculate Euclidean distance between two hex colors."""
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
        return np.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
