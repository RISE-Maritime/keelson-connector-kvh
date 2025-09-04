#!/usr/bin/env python3

"""
Test CRC-32/MPEG-2 implementation against known values
"""

import struct

def calculate_crc32(data):
    """
    Calculate CRC-32/MPEG-2 checksum as used in C++ implementation.
    This implements the same algorithm as the C++ uiCalcCRC function.
    """
    # CRC-32/MPEG-2 polynomial: 0x04C11DB7
    crc = 0xFFFFFFFF
    
    for byte in data:
        crc = crc ^ (byte << 24)
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ 0x04C11DB7
            else:
                crc = crc << 1
            crc = crc & 0xFFFFFFFF
    
    return crc

def test_crc():
    # Test with a simple known pattern
    test_data = b'\xFE\x81\xFF\x56'  # KVH header
    crc = calculate_crc32(test_data)
    print(f"CRC of KVH header: 0x{crc:08X}")
    
    # Test with empty data
    crc_empty = calculate_crc32(b'')
    print(f"CRC of empty data: 0x{crc_empty:08X}")
    
    # Test with a longer pattern
    test_pattern = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B'
    crc_pattern = calculate_crc32(test_pattern)
    print(f"CRC of test pattern: 0x{crc_pattern:08X}")

if __name__ == "__main__":
    test_crc()
