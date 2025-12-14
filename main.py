from spotify_codes.encoder import Encoder
from spotify_codes.decoder import Decoder
from spotify_codes.renderer import Renderer

import os

logo_path = os.path.join(os.path.dirname(__file__), "logo.png")


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
    renderer = Renderer()
    name = f"{media_ref}_code.png"
    renderer.render(bar_heights, name, logo_path=logo_path)
    print(f"Saved to {name}")


if __name__ == "__main__":
    main()
