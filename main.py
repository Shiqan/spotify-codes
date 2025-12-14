from spotify_codes import Encoder, Decoder, Renderer, Parser
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")


def main():
    """Entry point for the application."""
    # Example: encode a media reference to a barcode
    # media_ref = 57639171874
    media_ref = 57268659651

    encoder = Encoder()
    bar_heights = encoder.encode(media_ref)

    decoder = Decoder()
    decoded_ref = decoder.decode(bar_heights)

    print(f"Media Reference: {media_ref}")
    print(f"Bar Heights: {bar_heights}")
    print(f"Decoded media reference: {decoded_ref}")
    assert media_ref == decoded_ref, "Decoded reference does not match original!"

    # Render to image
    renderer = Renderer(LOGO_PATH)
    name = f"{media_ref}_code.png"
    renderer.render(bar_heights, name)
    print(f"Saved to {name}")

    parser = Parser()
    parsed_heights = parser.parse(name)
    print(f"Parsed Bar Heights: {parsed_heights}")
    assert bar_heights == parsed_heights, "Parsed heights do not match original!"


if __name__ == "__main__":
    main()
