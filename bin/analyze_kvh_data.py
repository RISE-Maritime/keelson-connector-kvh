#!/usr/bin/env python3
"""
Quick utility to analyze the raw binary data from KVH device 
to look for headers and patterns.
"""

import sys

# Sample data from the connector output (hex format)
sample_data_hex = "fcfffefdf8fffffffcfffefefdfffffcfcfffffcfffefffffffffbfffffffffcfffffffffffffffffefffffcf9fffdfffdff"

def analyze_binary_data(hex_string):
    """Analyze binary data for KVH headers and patterns"""
    
    # Convert hex to bytes
    data = bytes.fromhex(hex_string)
    
    print(f"Data length: {len(data)} bytes")
    print(f"Raw data: {data.hex()}")
    
    # Look for potential headers
    headers_to_check = [
        (0xFE81FF56, "Format B"),
        (0xFE81FF55, "Format A"), 
        (0xFE81FF57, "Format C"),
        (0xFE8100AA, "XBIT"),
        (0xFE8100AB, "XBIT2")
    ]
    
    print("\nSearching for KVH headers...")
    
    for i in range(len(data) - 3):
        # Check 4-byte sequences
        four_bytes = data[i:i+4]
        if len(four_bytes) == 4:
            value = int.from_bytes(four_bytes, byteorder='big')
            value_little = int.from_bytes(four_bytes, byteorder='little')
            
            for header, name in headers_to_check:
                if value == header:
                    print(f"Found {name} header at offset {i}: {value:08X} (big-endian)")
                if value_little == header:
                    print(f"Found {name} header at offset {i}: {value_little:08X} (little-endian)")
    
    print("\nLooking for repeating patterns...")
    # Look for patterns that might indicate packet boundaries
    pattern_counts = {}
    for i in range(len(data) - 1):
        two_bytes = data[i:i+2]
        pattern = two_bytes.hex()
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    # Show most common 2-byte patterns
    common_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Most common 2-byte patterns:")
    for pattern, count in common_patterns:
        print(f"  {pattern}: {count} occurrences")

if __name__ == "__main__":
    # Test with sample data
    samples = [
        "fcfffefdf8fffffffcfffefefdfffffcfcfffffcfffefffffffffbfffffffffcfffffffffffffffffefffffcf9fffdfffdff",
        "d211e34f75cafb33e02dff2b52f45f422a8a6b86ba19ff5f5492fc1b31c7fb6b3080430380fa0b3a3a5bd28e3b4476b1ff2f",
        "2ba93b5fb9f20f6c9e7f83be591f02651b038865ff2f6d8ff60b2d14ff6b125614fb2fd72afe6b233b6376f12f220a0f122f"
    ]
    
    for i, sample in enumerate(samples):
        print(f"\n=== Analyzing Sample {i+1} ===")
        analyze_binary_data(sample)
