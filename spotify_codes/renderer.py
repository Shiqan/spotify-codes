from typing import List
from PIL import Image, ImageDraw


class Renderer:
    def __init__(
        self,
        logo_path: str,
        bar_width: int = 8,
        bg_color: str = "black",
        bar_color: str = "white",
        bar_padding: int = 8,
        height: int = 100,
    ):
        """
        Initialize renderer.

        Args:
            logo_path: Path to logo image (PNG or SVG) - required
            bar_width: Width of each bar in pixels (default 8)
            bg_color: Background color (default black)
            bar_color: Bar color (default white)
            bar_padding: Padding between bars in pixels (default 8)
            height: Height of the output image in pixels (default 100)
        """
        self.logo_path = logo_path
        self.bar_width = bar_width
        self.bg_color = bg_color
        self.bar_color = bar_color
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

        logo_img = Image.open(self.logo_path).convert("RGBA")
        # Logo height equals max bar height (7 + 1) * bar_width
        logo_size = logo_img.height

        bars_width = (
            len(bar_heights) * self.bar_width
            + (len(bar_heights) - 1) * self.bar_padding
        )
        width = logo_size + logo_padding + bars_width + 20
        center_y = self.height // 2

        img = Image.new(
            "RGB", (width, self.height), color=self._color_to_rgb(self.bg_color)
        )
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

            draw.rounded_rectangle(
                [x0, y0, x1, y1], radius=4, fill=self._color_to_rgb(self.bar_color)
            )

        img.save(filename)

    def _color_to_rgb(self, color: str) -> tuple:
        """Convert color name to RGB tuple."""
        colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
        }

        if color in colors:
            return colors[color]

        raise ValueError(f"Unknown color: {color}")
