from typing import List, Optional
from PIL import Image, ImageDraw


class Renderer:
    def __init__(
        self,
        bar_width: int = 8,
        bg_color: str = "black",
        bar_color: str = "white",
        bar_padding: int = 8,
    ):
        """
        Initialize renderer.

        Args:
            bar_width: Width of each bar in pixels (default 20)
            bg_color: Background color (default black)
            bar_color: Bar color (default white)
            bar_padding: Padding between bars in pixels (default 2)
        """
        self.bar_width = bar_width
        self.bg_color = bg_color
        self.bar_color = bar_color
        self.bar_padding = bar_padding

    def render(
        self,
        bar_heights: List[int],
        filename: str = "code.png",
        logo_path: Optional[str] = None,
        logo_padding: int = 10,
    ):
        """
        Render bar heights to a PNG image.

        Args:
            bar_heights: List of bar heights (0-7)
            filename: Output filename
            logo_path: Path to logo image (PNG or SVG)
            logo_padding: Padding between logo and bars in pixels (default 10)
        """
        if len(bar_heights) != 23:
            raise ValueError(f"Expected 23 bars, got {len(bar_heights)}")

        if not all(0 <= h <= 7 for h in bar_heights):
            raise ValueError("Bar heights must be between 0 and 7")

        logo_size = 10 * self.bar_width
        bars_width = (
            len(bar_heights) * self.bar_width
            + (len(bar_heights) - 1) * self.bar_padding
        )
        width = (
            (logo_size + logo_padding + bars_width + 20)
            if logo_path
            else (20 + bars_width + 20)
        )
        height = 10 * self.bar_width + 20
        center_y = height // 2

        img = Image.new("RGB", (width, height), color=self._color_to_rgb(self.bg_color))
        draw = ImageDraw.Draw(img)

        bars_start_x = 0
        if logo_path:
            logo_img = Image.open(logo_path).convert("RGBA")
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            logo_y = (height - logo_size) // 2
            img.paste(logo_img, (0, logo_y), logo_img)
            bars_start_x = logo_size + logo_padding
        else:
            bars_start_x = 20

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
