from typing import List


class Encoder:
    """Encodes media reference into bar heights."""

    # CRC-8 polynomial (x^8 + x^2 + x + 1)
    CRC_POLYNOMIAL = [1, 0, 0, 0, 0, 0, 1, 1, 1]

    # Convolutional code generators
    G0 = [1, 1, 0, 1, 1, 0, 1]
    G1 = [1, 0, 0, 1, 1, 1, 1]

    # Gray code lookup table
    GRAY_CODE = [0, 1, 3, 2, 7, 6, 4, 5]

    def encode(self, media_ref: int) -> List[int]:
        """
        Encode a media reference into bar heights.

        Steps:
        1. Convert media reference to 37-bit binary
        2. Calculate CRC-8 check bits
        3. Convolutionally encode (with tail biting)
        4. Interleave parity bits
        5. Puncture code (increase rate from 1/2 to 3/4)
        6. Permute bits to spread errors
        7. Map to Gray code bar heights
        8. Add reference bars
        """
        # Step 1: Media reference to binary
        media_bits = self._int_to_bits(media_ref, 37)

        # Step 2: CRC calculation
        check_bits = self._crc8(media_bits)
        data_with_crc = media_bits[::-1] + check_bits

        # Step 3: Convolutional encoding with tail biting
        parity0 = self._convolutional_encode(data_with_crc, self.G0)
        parity1 = self._convolutional_encode(data_with_crc, self.G1)

        # Step 4: Interleave parity bits (a0, b0, a1, b1, ...)
        interleaved = self._interleave(parity0, parity1)

        # Step 5: Puncture (remove every 3rd bit to increase rate to 3/4)
        punctured = self._puncture(interleaved)

        # Step 6: Permute bits (every 7th bit mod 60)
        permuted = self._permute(punctured)

        # Step 7: Convert to Gray code bar heights
        bar_heights = self._bits_to_gray_heights(permuted)

        # Step 8: Add reference bars (0 at start, 7 at position 11, 0 at end)
        bar_heights = [0] + bar_heights[:10] + [7] + bar_heights[10:] + [0]

        return bar_heights

    def _int_to_bits(self, value: int, length: int) -> List[int]:
        """Convert integer to binary bit list."""
        bits = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)

        return bits

    def _bits_to_int(self, bits: List[int]) -> int:
        """Convert binary bit list to integer."""
        value = 0
        for bit in bits:
            value = (value << 1) | bit

        return value

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
        padded = [0, 0, 0] + bits

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

    def _convolutional_encode(
        self, bits: List[int], polynomial: List[int]
    ) -> List[int]:
        """
        Convolutionally encode data using the given generator polynomial.

        Uses tail biting: prepend the last (len(poly)-1) bits to the data
        instead of padding with zeros.
        """
        tail = bits[-(len(polynomial) - 1) :]

        full = tail + bits
        parity_bits = []

        for i in range(len(bits)):
            parity = 0
            for j in range(len(polynomial)):
                parity ^= full[i + j] * polynomial[j]
            parity_bits.append(parity)

        return parity_bits

    def _interleave(self, bits0: List[int], bits1: List[int]) -> List[int]:
        """Interleave two bit sequences (a0, b0, a1, b1, ...)."""
        interleaved = []
        for a, b in zip(bits0, bits1):
            interleaved.append(a)
            interleaved.append(b)

        return interleaved

    def _puncture(self, bits: List[int]) -> List[int]:
        """
        Puncture the code by removing every 3rd bit.
        Increases code rate from 1/2 to 3/4.
        """
        return [bit for i, bit in enumerate(bits) if (i + 1) % 3 != 0]

    def _permute(self, bits: List[int], step: int = 7) -> List[int]:
        """
        Permute bits by selecting every step-th bit (mod length).
        Spreads errors to improve FEC resilience.
        """
        permuted = [0] * len(bits)
        for i in range(len(bits)):
            permuted[i] = bits[(i * step) % len(bits)]

        return permuted

    def _bits_to_gray_heights(self, bits: List[int]) -> List[int]:
        """Convert bit triplets to Gray code bar heights (0-7)."""
        heights = []
        for i in range(0, len(bits), 3):
            triplet = bits[i : i + 3]
            # Pad if necessary
            while len(triplet) < 3:
                triplet.append(0)

            # Convert triplet to index
            index = self._bits_to_int(triplet)
            # Use Gray code table
            heights.append(self.GRAY_CODE[index])

        return heights
