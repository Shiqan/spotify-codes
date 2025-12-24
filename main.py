from spotify_codes import Encoder, Decoder, Renderer, Parser
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
    renderer = Renderer(LOGO_PATH, bg_color="#543651")
    parser = Parser()

    for media_ref in examples:
        print(f"Media Reference: {media_ref}")

        # Encode to bar heights
        bar_heights = encoder.encode(media_ref)
        print(f"Bar Heights: {bar_heights}")

        # Render to image
        name = f"{media_ref}_code.png"
        renderer.render(bar_heights, name)
        print(f"Saved to {name}")

        # Parse back from image
        parsed_heights = parser.parse(name)
        print(f"Parsed Bar Heights: {parsed_heights}")
        assert bar_heights == parsed_heights, "Parsed heights do not match original!"

        # Decode back to media reference
        decoded_ref = decoder.decode(bar_heights)
        print(f"Decoded media reference: {decoded_ref}")
        assert media_ref == decoded_ref, "Decoded reference does not match original!"


if __name__ == "__main__":
    main()
