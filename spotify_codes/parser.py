from PIL import Image
from typing import List


class Parser:
    def _otsu_threshold(self, histogram: List[int]) -> int:
        """Calculate Otsu's threshold from histogram."""
        total = sum(histogram)
        sum_val = sum(i * histogram[i] for i in range(len(histogram)))

        sum_b = 0
        w_b = 0
        max_var = 0
        threshold = 0

        for t in range(len(histogram)):
            w_b += histogram[t]
            if w_b == 0:
                continue

            w_f = total - w_b
            if w_f == 0:
                break

            sum_b += t * histogram[t]
            mu_b = sum_b / w_b
            mu_f = (sum_val - sum_b) / w_f

            var = w_b * w_f * (mu_b - mu_f) ** 2
            if var > max_var:
                max_var = var
                threshold = t

        return threshold

    def parse(self, image_path: str) -> List[int]:
        """
        Extract bar heights from the Spotify Code (23 bars encoded as 0-7).

        Args:
            image_path: Path to the Spotify Code image

        Returns:
            List of 23 encoded bar heights (0-7), relative to the logo height
        """
        img = Image.open(image_path).convert("L")
        width, height = img.size

        # Calculate Otsu threshold
        histogram = img.histogram()
        threshold = self._otsu_threshold(histogram)

        # Try both: bars as white and bars as dark; pick the better result
        bar_heights_white = self._extract_bars(
            img, threshold, invert=False, width=width, height=height
        )
        bar_heights_dark = self._extract_bars(
            img, threshold, invert=True, width=width, height=height
        )

        # Choose the polarity that yields valid bars (prefer one with 24+ detected bars)
        if len(bar_heights_white) >= len(bar_heights_dark):
            bar_heights = bar_heights_white
        else:
            bar_heights = bar_heights_dark

        if not bar_heights:
            raise ValueError("No bars found in image")

        # First bar is the Spotify logo (reference height)
        logo_height = bar_heights[0]

        # Encode bars relative to logo (should be 23 bars total)
        sequence = []
        for bar_height in bar_heights[1:]:
            ratio = bar_height / logo_height
            ratio *= 8
            ratio //= 1
            sequence.append(int(ratio - 1))

        return sequence

    def _extract_bars(
        self, img: Image.Image, threshold: int, invert: bool, width: int, height: int
    ) -> List[int]:
        """Extract bar heights using a specific threshold polarity.

        Args:
            img: Grayscale image
            threshold: Otsu threshold value
            invert: If True, bars are dark (< threshold); else bars are white (> threshold)
            width: Image width
            height: Image height

        Returns:
            List of detected bar heights
        """
        if invert:
            # Bars are dark: pixels < threshold become white (255)
            binary_im = img.point(lambda p: 255 if p < threshold else 0)
        else:
            # Bars are white: pixels > threshold become white (255)
            binary_im = img.point(lambda p: 255 if p > threshold else 0)

        bar_heights = []
        in_bar = False
        current_bar_min = height
        current_bar_max = -1

        for x in range(width):
            # Find top and bottom of white pixels in this column
            min_row = height
            max_row = -1

            for y in range(height):
                pixel = binary_im.getpixel((x, y))
                if pixel > 128:  # White pixel (bar)
                    min_row = min(min_row, y)
                    max_row = max(max_row, y)

            # Check if we have a bar in this column
            has_bar = max_row >= 0

            if has_bar:
                if not in_bar:
                    # Starting a new bar
                    in_bar = True
                    current_bar_min = min_row
                    current_bar_max = max_row
                else:
                    # Continue bar
                    current_bar_min = min(current_bar_min, min_row)
                    current_bar_max = max(current_bar_max, max_row)
            else:
                if in_bar:
                    # Ending a bar
                    bar_height = current_bar_max - current_bar_min
                    bar_heights.append(bar_height)
                    in_bar = False

        return bar_heights
