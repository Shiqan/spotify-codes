from typing import List
import pytest
from spotify_codes.decoder import Decoder


class TestDecoder:
    def setup_method(self):
        """Set up test fixtures."""
        self.decoder = Decoder()

    def test_int_to_bits(self):
        """Test integer to binary conversion."""
        bits = self.decoder._int_to_bits(5, 4)
        assert bits == [0, 1, 0, 1]

        bits = self.decoder._int_to_bits(15, 4)
        assert bits == [1, 1, 1, 1]

        bits = self.decoder._int_to_bits(5, 10)
        assert bits == [0, 0, 0, 0, 0, 0, 0, 1, 0, 1]

        bits = self.decoder._int_to_bits(15, 10)
        assert bits == [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]

    def test_bits_to_int(self):
        """Test binary to integer conversion."""
        value = self.decoder._bits_to_int([0, 1, 0, 1])
        assert value == 5

        value = self.decoder._bits_to_int([1, 1, 1, 1])
        assert value == 15

        value = self.decoder._bits_to_int([0, 0, 0, 0, 0, 0, 0, 1, 0, 1])
        assert value == 5

        value = self.decoder._bits_to_int([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
        assert value == 15

    @pytest.mark.parametrize(
        "index,expected_bits",
        [
            (0, [0, 0, 0]),
            (1, [0, 0, 1]),
            (2, [0, 1, 1]),
            (3, [0, 1, 0]),
            (5, [1, 1, 1]),
            (4, [1, 1, 0]),
            (7, [1, 0, 0]),
            (6, [1, 0, 1]),
        ],
    )
    def test_gray_height_to_bits(self, index: int, expected_bits: List[int]):
        """Test Gray code conversion for all 8 possible 3-bit triplets."""
        result = self.decoder._gray_height_to_bits(index)
        assert result == expected_bits

    @pytest.mark.parametrize(
        "heights,expected_bits",
        [
            ([0], [0, 0, 0]),
            ([1], [0, 0, 1]),
            ([2], [0, 1, 1]),
            ([3], [0, 1, 0]),
            ([5], [1, 1, 1]),
            ([4], [1, 1, 0]),
            ([7], [1, 0, 0]),
            ([6], [1, 0, 1]),
        ],
    )
    def test_gray_heights_to_bits(self, heights: List[int], expected_bits: List[int]):
        """Test Gray code conversion for all 8 possible 3-bit triplets."""
        result = self.decoder._gray_heights_to_bits(heights)
        assert result == expected_bits
