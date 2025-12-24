from typing import List
from PIL import Image, ImageDraw, ImageOps

ACCEPTABLE_BG_COLORS = {
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
}

ALLOWED_BAR_COLORS = {"#000000", "#ffffff"}


class Renderer:

    def __init__(
        self,
        logo_path: str,
        bar_width: int = 8,
        bg_color: str = "#010101",
        bar_color: str = "#ffffff",
        bar_padding: int = 8,
        height: int = 100,
    ):
        """
        Initialize renderer.

        Args:
            logo_path: Path to logo image (PNG or SVG) - required
            bar_width: Width of each bar in pixels (default 8)
            bg_color: Background color in hex (default "#000000")
            bar_color: Bar color in hex (default "#ffffff")
            bar_padding: Padding between bars in pixels (default 8)
            height: Height of the output image in pixels (default 100)
        """
        self.logo_path = logo_path
        self.bar_width = bar_width
        # Validate and normalize colors
        self.bg_color = self._validate_bg_color(bg_color)
        self.bar_color = self._validate_bar_color(bar_color)
        self.bar_padding = bar_padding
        self.height = height

    def render(
        self,
        bar_heights: List[int],
        filename: str = "code.png",
        logo_padding: int = 10,
    ):
        """
        Render bar heights to a PNG image.

        Args:
            bar_heights: List of bar heights (0-7)
            filename: Output filename
            logo_padding: Padding between logo and bars in pixels (default 10)
        """
        if len(bar_heights) != 23:
            raise ValueError(f"Expected 23 bars, got {len(bar_heights)}")

        if not all(0 <= h <= 7 for h in bar_heights):
            raise ValueError("Bar heights must be between 0 and 7")

        if not self.logo_path:
            raise ValueError("Logo path must be provided")

        logo_img = Image.open(self.logo_path)
        # Recolor logo background (black) to bg_color and logo (white) to bar_color
        logo_img = self._recolor_logo_background(logo_img)
        # Logo height equals max bar height (7 + 1) * bar_width
        logo_size = logo_img.height

        bars_width = (
            len(bar_heights) * self.bar_width
            + (len(bar_heights) - 1) * self.bar_padding
        )
        width = logo_size + logo_padding + bars_width + 20
        center_y = self.height // 2

        img = Image.new("RGB", (width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)

        logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        logo_y = (self.height - logo_size) // 2
        img.paste(logo_img, (0, logo_y), logo_img)

        bars_start_x = logo_size + logo_padding
        bar_heights = [h + 1 for h in bar_heights]
        for i, bar_height in enumerate(bar_heights):
            x0 = bars_start_x + i * (self.bar_width + self.bar_padding)
            bar_half_height = (bar_height * self.bar_width) // 2
            y0 = center_y - bar_half_height
            x1 = x0 + self.bar_width
            y1 = center_y + bar_half_height

            draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=self.bar_color)

        img.save(filename)

    def _recolor_logo_background(self, logo_img: Image.Image) -> Image.Image:
        """Map black background to bg_color and white logo to bar_color.

        Assumes the logo image is a white shape on a black background.
        Uses ImageOps.colorize for clean anti-aliased recoloring.
        """
        gray = logo_img.convert("L")
        colored = ImageOps.colorize(gray, black=self.bg_color, white=self.bar_color)
        return colored.convert("RGBA")

    def _is_hex_color(self, color: str) -> bool:
        """Return True if color is a valid #RRGGBB hex string."""
        if not isinstance(color, str):
            return False

        if len(color) != 7 or not color.startswith("#"):
            return False

        hex_str = color[1:]
        try:
            int(hex_str, 16)
            return True
        except ValueError:
            return False

    def _validate_bg_color(self, color: str) -> str:
        """Validate background color against acceptable list.

        Accepts hex values from ACCEPTABLE_BG_COLORS (case-insensitive) and
        also 'black'/'white' names for backward compatibility.
        Returns the original string (possibly lowercased for hex) if valid.
        """
        if not isinstance(color, str):
            raise ValueError("Background color must be a string")

        lower = color.lower()
        if self._is_hex_color(color) and lower in ACCEPTABLE_BG_COLORS:
            return lower

        raise ValueError(
            "Invalid background color. Must be one of the accepted hex colors."
        )

    def _validate_bar_color(self, color: str) -> str:
        """Validate bar color: only black or white (hex)."""
        if not isinstance(color, str):
            raise ValueError("Bar color must be a string")

        lower = color.lower()
        if self._is_hex_color(color) and lower in ALLOWED_BAR_COLORS:
            return lower

        raise ValueError("Invalid bar color. Only black or white are allowed.")
