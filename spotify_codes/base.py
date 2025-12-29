from typing import List


class BaseCodec:
    """Shared helpers for Spotify code encoding/decoding."""

    # CRC-8 polynomial (x^8 + x^2 + x + 1)
    CRC_POLYNOMIAL = [1, 0, 0, 0, 0, 0, 1, 1, 1]

    # Gray code lookup table and inverse
    GRAY_CODE = [0, 1, 3, 2, 7, 6, 4, 5]
    GRAY_CODE_INVERSE = {v: i for i, v in enumerate(GRAY_CODE)}

    def _int_to_bits(self, value: int, length: int) -> List[int]:
        """Convert integer to binary bit list (MSB-first)."""
        bits = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return bits

    def _bits_to_int(self, bits: List[int]) -> int:
        """Convert binary bit list (MSB-first) to integer."""
        value = 0
        for bit in bits:
            value = (value << 1) | bit
        return value

    def _permute(self, bits: List[int], step: int = 7) -> List[int]:
        """Permute bits by selecting every step-th bit (mod length)."""
        permuted = [0] * len(bits)
        for i in range(len(bits)):
            permuted[i] = bits[(i * step) % len(bits)]
        return permuted

    def _unpermute(self, bits: List[int], step: int = 43) -> List[int]:
        """Reverse the bit permutation used by `_permute`.

        For a given length L and step s, choose s' such that s * s' ≡ 1 (mod L).
        For encoder/decoder we use L=60, s=7, s'=43.
        """
        len_bits = len(bits)
        return [bits[(step * i) % len_bits] for i in range(len_bits)]

    def _puncture(self, bits: List[int]) -> List[int]:
        """Puncture the code by removing every 3rd bit (1-based index)."""
        return [bit for i, bit in enumerate(bits) if (i + 1) % 3 != 0]

    def _unpuncture(self, bits: List[int]) -> List[int]:
        """Inverse of `_puncture` for 60→45 mapping used here.

        Extract columns where i % 4 != 2 over 60 positions.
        """
        return [bits[i] for i in range(60) if i % 4 != 2]

    def _bits_to_gray_heights(self, bits: List[int]) -> List[int]:
        """Convert bit triplets to Gray code bar heights (0-7)."""
        heights = []
        for i in range(0, len(bits), 3):
            triplet = bits[i : i + 3]
            while len(triplet) < 3:
                triplet.append(0)
            index = self._bits_to_int(triplet)
            heights.append(self.GRAY_CODE[index])

        return heights

    def _gray_height_to_bits(self, value: int) -> List[int]:
        """Convert a Gray-code encoded height (0-7) to a 3-bit list."""
        index = self.GRAY_CODE_INVERSE[value]
        return self._int_to_bits(index, 3)

    def _gray_heights_to_bits(self, heights: List[int]) -> List[int]:
        """Convert list of heights (0-7) to concatenated 3-bit groups."""
        bits: List[int] = []
        for h in heights:
            bits.extend(self._gray_height_to_bits(h))

        return bits

    def _crc8_core(self, bits: List[int], *, reverse_input: bool) -> List[int]:
        """CRC-8 (x^8 + x^2 + x + 1) over 37 data bits.

        The encoder variant uses the bits as-is; the decoder variant needs
        `reverse_input=True` to match historical bit ordering in that path.
        Returns 8 CRC bits (MSB-first in the algorithm's remainder order).
        """
        padded = [0, 0, 0] + (bits[::-1] if reverse_input else bits)
        # Reverse byte order (reorder 8-bit chunks)
        reversed_data = [
            bit for i in range(len(padded) - 8, -1, -8) for bit in padded[i : i + 8]
        ]

        poly_degree = len(self.CRC_POLYNOMIAL) - 1

        remainder = reversed_data + [0] * poly_degree

        for i in range(len(reversed_data)):
            if remainder[i] == 1:
                for j in range(len(self.CRC_POLYNOMIAL)):
                    remainder[i + j] ^= self.CRC_POLYNOMIAL[j]

        return remainder[len(reversed_data) :]
