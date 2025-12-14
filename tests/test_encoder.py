import pytest
from spotify_codes.encoder import Encoder


class TestEncoder:
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = Encoder()

    def test_int_to_bits(self):
        """Test integer to binary conversion."""
        bits = self.encoder._int_to_bits(5, 4)
        assert bits == [0, 1, 0, 1]

        bits = self.encoder._int_to_bits(15, 4)
        assert bits == [1, 1, 1, 1]

        bits = self.encoder._int_to_bits(5, 10)
        assert bits == [0, 0, 0, 0, 0, 0, 0, 1, 0, 1]

        bits = self.encoder._int_to_bits(15, 10)
        assert bits == [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]

    def test_bits_to_int(self):
        """Test binary to integer conversion."""
        value = self.encoder._bits_to_int([0, 1, 0, 1])
        assert value == 5

        value = self.encoder._bits_to_int([1, 1, 1, 1])
        assert value == 15

        value = self.encoder._bits_to_int([0, 0, 0, 0, 0, 0, 0, 1, 0, 1])
        assert value == 5

        value = self.encoder._bits_to_int([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
        assert value == 15

    @pytest.mark.parametrize(
        "media_ref",
        [
            576391714,
            57639171874,
            67775490487,
            26560102031,
            12345678901,
            999999999999,
        ],
    )
    def test_encode_output_length(self, media_ref):
        """Test that encoding produces correct output length."""
        bar_heights = self.encoder.encode(media_ref)

        # Should have 23 bars (20 data + 3 reference)
        assert len(bar_heights) == 23

    @pytest.mark.parametrize(
        "media_ref",
        [
            0,
            123456789,
            1234567890,
            57639171874,
            67775490487,
            26560102031,
            999999999999,
            99999999999999,
        ],
    )
    def test_encode_bar_range(self, media_ref):
        """Test that all bar heights are in valid range (0-7)."""
        bar_heights = self.encoder.encode(media_ref)

        assert len(bar_heights) > 0, (
            f"No bar heights generated for media_ref {media_ref}"
        )

        assert all(0 <= height <= 7 for height in bar_heights), (
            f"Invalid bar heights {bar_heights} for media_ref {media_ref}"
        )

    @pytest.mark.parametrize(
        "media_ref,expected",
        [
            (
                57639171874,
                [0, 5, 7, 4, 1, 4, 6, 6, 0, 2, 4, 7, 3, 4, 6, 7, 5, 5, 6, 0, 5, 0, 0],
            ),
            (
                57268659651,
                [0, 5, 0, 3, 4, 5, 0, 4, 5, 0, 3, 7, 3, 6, 1, 5, 5, 2, 4, 4, 4, 3, 0],
            ),
            (
                67775490487,
                [0, 6, 6, 7, 1, 7, 3, 0, 0, 3, 4, 7, 1, 4, 3, 4, 1, 7, 4, 6, 5, 7, 0],
            ),
            (
                26560102031,
                [0, 2, 6, 0, 7, 6, 3, 2, 2, 0, 1, 7, 0, 4, 6, 4, 5, 1, 5, 7, 4, 0, 0],
            ),
        ],
    )
    def test_encode_known_values(self, media_ref, expected):
        """Test that reference bars are correct."""
        bar_heights = self.encoder.encode(media_ref)
        assert bar_heights == expected

    @pytest.mark.parametrize(
        "bits,expected_heights",
        [
            ([0, 0, 0], [0]),
            ([0, 0, 1], [1]),
            ([0, 1, 1], [2]),
            ([0, 1, 0], [3]),
            ([1, 1, 1], [5]),
            ([1, 1, 0], [4]),
            ([1, 0, 0], [7]),
            ([1, 0, 1], [6]),
        ],
    )
    def test_bits_to_gray_heights(self, bits, expected_heights):
        """Test Gray code conversion for all 8 possible 3-bit triplets."""
        heights = self.encoder._bits_to_gray_heights(bits)
        assert heights == expected_heights
