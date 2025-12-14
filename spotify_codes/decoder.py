from typing import List
import numpy as np


class Decoder:
    """Decodes bar heights back into media reference."""

    # CRC-8 polynomial (x^8 + x^2 + x + 1)
    CRC_POLYNOMIAL = [1, 0, 0, 0, 0, 0, 1, 1, 1]

    # Gray code lookup table (inverse)
    GRAY_CODE = [0, 1, 3, 2, 7, 6, 4, 5]
    GRAY_CODE_INVERSE = {v: i for i, v in enumerate(GRAY_CODE)}

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

    def _int_to_bits(self, value: int, length: int) -> List[int]:
        """Convert integer to binary bit list."""
        bits = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return bits

    def _bits_to_int(self, bits: List[int]) -> int:
        """Convert binary bit list to integer."""
        value = 0
        for bit in bits[: len(bits)]:
            value = (value << 1) | bit
        return value

    def _gray_height_to_bits(self, index: int) -> List[int]:
        """
        Convert Gray code bar height to bits.

        Each bar height (0-7) is converted to its Gray code index,
        which is then represented as a 3-bit binary triplet.
        """
        index = self.GRAY_CODE_INVERSE[index]
        triplet = self._int_to_bits(index, 3)
        return triplet

    def _gray_heights_to_bits(self, heights: List[int]) -> List[int]:
        """
        Convert Gray code bar heights to bits.

        Each bar height (0-7) is converted to its Gray code index,
        which is then represented as a 3-bit binary triplet.
        20 heights produce 60 bits total.
        """
        level_bits = []
        for height in heights:
            index = self.GRAY_CODE_INVERSE[height]
            triplet = self._int_to_bits(index, 3)
            level_bits.extend(triplet)
        return level_bits

    def _unpermute(self, bits: List[int], step: int = 43) -> List[int]:
        """
        Reverse the bit permutation.

        The encoder scattered bits by reading from position (i * step) % len.
        To reverse it, write each bit back to position (i * step) % len.
        """
        len_bits = len(bits)
        return [bits[step * i % len_bits] for i in range(len_bits)]

    def _unpuncture(self, bits: List[int]) -> List[int]:
        """
        Extract the non-punctured bits from the encoded sequence.

        The encoder removed every 3rd bit during puncturing.
        This extracts the bits that were kept (columns where i % 4 != 2).
        Takes 60 bits and returns 45 bits.
        """
        cols = [i for i in range(60) if i % 4 != 2]
        return [bits[c] for c in cols]

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
        """
        Calculate CRC-8 checksum using bit-by-bit polynomial division.

        Process:
        1. Prepend 3 zero bits (so we have 5 bytes)
        2. Reverse byte order (LSB-first within bytes)
        3. Perform polynomial XOR division
        4. Return the 8-bit remainder as the checksum

        Returns:
            List of 8 bits representing the CRC-8 checksum
        """
        # Prepend 3 zero bits
        padded = [0, 0, 0] + bits[::-1]

        # Reverse byte order (reorder 8-bit chunks)
        reversed_data = [
            bit for i in range(len(padded) - 8, -1, -8) for bit in padded[i : i + 8]
        ]

        poly_degree = len(self.CRC_POLYNOMIAL) - 1  # 8 for CRC-8

        # Pad with 8 zero bits for polynomial division
        remainder = reversed_data + [0] * poly_degree

        # Perform polynomial long division (XOR with polynomial on each '1' bit)
        for i in range(len(reversed_data)):
            if remainder[i] == 1:
                for j in range(len(self.CRC_POLYNOMIAL)):
                    remainder[i + j] ^= self.CRC_POLYNOMIAL[j]

        # Extract the 8-bit remainder
        crc = remainder[len(reversed_data) :]
        return crc
