from typing import List
from .base import BaseCodec


class Decoder(BaseCodec):
    """Decodes bar heights back into media reference."""

    # Convolutional code generators (base polynomials)
    # The following matrix is used to "invert" the convolutional code.
    # In particular, we choose a 45 vector basis for the columns of the
    # generator matrix (by deleting those in positions equal to 2 mod 4)
    # and then inverting the matrix. By selecting the corresponding 45
    # elements of the convolutionally encoded vector and multiplying
    # on the right by this matrix, we get back to the unencoded data,
    # assuming there are no errors.
    CONV_GEN = [
        [0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1] + 31 * [0],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1] + 32 * [0],
        [0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1] + 32 * [0],
    ]

    def decode(self, bar_heights: List[int]) -> int:
        """
        Decode bar heights back into media reference.
        Based on the Spotify bar code format.

        Steps:
        1. Remove reference bars
        2. Convert gray codes to bits
        3. Un-permute bits
        4. Un-puncture bits
        5. Invert convolutional encoding
        6. Verify CRC
        """
        # Step 1: Remove reference bars (first, 11th and last)
        bar_heights = bar_heights[1:11] + bar_heights[12:-1]

        # Step 2: Convert Gray code bar heights to bits (20 heights = 60 bits)
        level_bits = self._gray_heights_to_bits(bar_heights)

        # Step 3: Un-permute bits (reverse of encoder permutation)
        conv_bits = self._unpermute(level_bits, step=43)

        # Step 4: Un-puncture
        conv_bits45 = self._unpuncture(conv_bits)

        # Step 5: Convolutional decode using matrix multiplication
        bin45 = self._matrix_multiply(conv_bits45, self._conv_generator_inv())

        # Step 6: Verify CRC
        if self._check_crc(bin45):
            media_ref = self._bits_to_int(bin45[:37][::-1])
            return media_ref
        else:
            print("Error in levels; Use real decoder!!!")
            return -1

    # Gray code, bit ops, permute/unpermute, puncture/unpuncture provided by BaseCodec.

    def _shift_right(self, row: List[int], shift: int) -> List[int]:
        """Shift a binary row to the right by shift positions."""
        return row[-shift % len(row) : len(row) :] + row[0 : -shift % len(row)]

    def _conv_generator_inv(self) -> List[List[int]]:
        """
        Generate inverse convolutional generator matrix.

        Build the 45x45 convolutional code generator inverse matrix.
        Each row is a shifted version of the base generator polynomials.
        """
        return [
            self._shift_right(self.CONV_GEN[(s - 27) % 3], s) for s in range(27, 72)
        ]

    def _matrix_multiply(
        self, bits: List[int], generator: List[List[int]]
    ) -> List[int]:
        """
        Compute 45-bit convolutional code using the inverse generator matrix.

        Multiplies the input bit vector with each column of the inverse
        convolutional generator matrix, computing the dot product modulo 2
        for each column to produce 45 output bits.

        Args:
            bits: List of 45 input bits for convolutional decoding
            generator: 45x45 inverse convolutional generator matrix

        Returns:
            List of 45 encoded output bits
        """
        return [
            sum(int(a) * int(b) for a, b in zip(bits, col)) % 2
            for col in zip(*generator)
        ]

    def _check_crc(self, bits: List[int]) -> bool:
        """
        Verify CRC-8 checksum.
        bits should be 45 bits total: 37 media bits + 8 CRC bits
        """
        media_bits = bits[:37]
        crc_bits = bits[37:]

        calculated_crc = self._crc8(media_bits)
        return calculated_crc == crc_bits

    def _crc8(self, bits: List[int]) -> List[int]:
        """Decoder variant using shared CRC core with reversed input bits."""
        return self._crc8_core(bits, reverse_input=True)
