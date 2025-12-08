from spotify_codes.encoder import Encoder
from spotify_codes.renderer import Renderer


def main():
    """Entry point for the application."""
    # Example: encode a media reference to a barcode
    media_ref = 57639171874

    encoder = Encoder()
    bar_heights = encoder.encode(media_ref)

    print(f"Media Reference: {media_ref}")
    print(f"Bar Heights: {bar_heights}")

    # Render to image
    renderer = Renderer()
    name = f"{media_ref}_code.png"
    renderer.render(bar_heights, name)
    print(f"Saved to {name}")


if __name__ == "__main__":
    main()
