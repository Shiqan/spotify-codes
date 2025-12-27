from spotify_codes import (
    Encoder,
    Decoder,
    Parser,
    Detector,
    Renderer,
    ACCEPTABLE_BG_COLORS,
    ACCEPTABLE_BAR_COLORS,
)
import cv2
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")


def main():
    """Entry point for the application."""
    examples = [
        57639171874,
        5726865965,
        26560102031,
        57268659651,
        67775490487,
    ]

    encoder = Encoder()
    decoder = Decoder()
    parser = Parser()
    detector = Detector(LOGO_PATH)

    if False:
        for bg_color in ACCEPTABLE_BG_COLORS:
            for bar_color in ACCEPTABLE_BAR_COLORS:
                try:
                    renderer = Renderer(
                        LOGO_PATH, bg_color=bg_color, bar_color=bar_color
                    )
                except ValueError as e:
                    print(
                        f"Skipping invalid color combination bg:{bg_color} bar:{bar_color}: {e}"
                    )
                    continue

                for media_ref in examples:
                    try:
                        # Encode to bar heights
                        bar_heights = encoder.encode(media_ref)

                        # Render to image
                        name = f"{media_ref}_{bg_color}_code.png"
                        renderer.render(bar_heights, name)

                        # Parse back from image
                        parsed_heights = parser.parse(name)
                        assert (
                            bar_heights == parsed_heights
                        ), "Parsed heights do not match original!"

                        # Decode back to media reference
                        decoded_ref = decoder.decode(bar_heights)
                        assert (
                            media_ref == decoded_ref
                        ), "Decoded reference does not match original!"
                    except Exception as e:
                        print(
                            f"Error processing media reference {media_ref} with bg {bg_color}: {e}"
                        )

    # Detect barcode region (logo + bars) and parse/decode from the ROI
    name = "5726865965_screenshot_dark_purple.png"
    # name = "67775490487_screenshot_solarized_purple.png"

    ref = name.split("_", maxsplit=1)[0]
    result = detector.detect_barcode(name)
    if result.found and result.position:
        x, y, w, h = result.position
        img = cv2.imread(name)
        roi = img[y : y + h, x : x + w]
        roi_path = name.replace(".png", "_roi.png")
        cv2.imwrite(roi_path, roi)
        print(f"Detected barcode ROI: {(x, y, w, h)} -> {roi_path}")

        parsed_heights = parser.parse(roi_path)
        print(f"Parsed Bar Heights (ROI): {parsed_heights}")
        decoded_ref = decoder.decode(parsed_heights)
        print(f"Decoded media reference (ROI): {decoded_ref}")
        assert ref != decoded_ref, "Decoded reference does not match original!"
    else:
        raise ValueError(f"Could not detect barcode in {name}: {result.error_message}")


if __name__ == "__main__":
    main()
