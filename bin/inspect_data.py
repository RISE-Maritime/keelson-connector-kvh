#!/usr/bin/env python3

"""
Data Inspector - helps debug what type of data is being received from serial devices
"""

import sys
import time
from collections import Counter

def inspect_data():
    """Inspect incoming data to help identify the format"""
    
    print("Data Inspector - Reading from stdin...")
    print("Press Ctrl+C to quit\n")
    
    buffer = b''
    byte_count = 0
    chunk_count = 0
    byte_histogram = Counter()
    
    # Look for common patterns
    patterns_to_check = [
        (b'\xFE\x81\xFF\x56', 'KVH Binary Format B Header'),
        (b'#APIMU', 'KVH Text Format APIMU'),
        (b'#APINS', 'KVH Text Format APINS'),
        (b'$GP', 'NMEA GPS'),
        (b'\r\n', 'CRLF Line endings'),
        (b'\n', 'LF Line endings'),
    ]
    
    pattern_counts = {pattern: 0 for pattern, _ in patterns_to_check}
    
    try:
        while True:
            # Read data in chunks
            chunk = sys.stdin.buffer.read(1024)
            if not chunk:
                break
            
            buffer += chunk
            byte_count += len(chunk)
            chunk_count += 1
            
            # Update byte histogram
            for byte in chunk:
                byte_histogram[byte] += 1
            
            # Check for patterns
            for pattern, description in patterns_to_check:
                count = buffer.count(pattern)
                if count > pattern_counts[pattern]:
                    new_occurrences = count - pattern_counts[pattern]
                    pattern_counts[pattern] = count
                    print(f"Found {new_occurrences} occurrence(s) of {description}")
            
            # Print periodic stats
            if chunk_count % 10 == 0 or byte_count < 2048:
                print(f"\nStats after {byte_count} bytes:")
                print(f"  Chunks received: {chunk_count}")
                
                if byte_count > 0:
                    # Show first 200 bytes as hex
                    sample = buffer[:200]
                    print(f"  First {min(len(sample), 200)} bytes (hex): {sample.hex()}")
                    
                    # Try to show as ASCII
                    ascii_sample = sample.decode('ascii', errors='replace')[:100]
                    print(f"  As ASCII (first 100 chars): {repr(ascii_sample)}")
                    
                    # Show byte distribution
                    printable_count = sum(1 for b in sample if 32 <= b <= 126)
                    null_count = sample.count(0)
                    print(f"  Printable ASCII bytes: {printable_count}/{len(sample)} ({100*printable_count/len(sample):.1f}%)")
                    print(f"  Null bytes: {null_count}")
                    
                    # Show most common bytes
                    print("  Most common bytes:")
                    for byte, count in byte_histogram.most_common(5):
                        char_repr = chr(byte) if 32 <= byte <= 126 else f"\\x{byte:02x}"
                        print(f"    {byte:3d} ('{char_repr}'): {count} times")
                
                print()
            
            # Keep buffer manageable
            if len(buffer) > 10000:
                # Keep last 1000 bytes for pattern detection
                buffer = buffer[-1000:]
            
            time.sleep(0.1)  # Small delay to prevent overwhelming output
                
    except KeyboardInterrupt:
        print(f"\n\nFinal Summary after {byte_count} bytes:")
        print(f"Total chunks: {chunk_count}")
        
        print("\nPattern Detection Results:")
        for pattern, description in patterns_to_check:
            count = pattern_counts[pattern]
            if count > 0:
                print(f"  {description}: {count} occurrences")
            else:
                print(f"  {description}: Not found")
        
        if byte_count > 0:
            print("\nData Analysis:")
            printable_total = sum(count for byte, count in byte_histogram.items() if 32 <= byte <= 126)
            print(f"  Total printable ASCII: {printable_total}/{byte_count} ({100*printable_total/byte_count:.1f}%)")
            print(f"  Total null bytes: {byte_histogram.get(0, 0)}")
            
            print("\n  Top 10 most common bytes:")
            for byte, count in byte_histogram.most_common(10):
                char_repr = chr(byte) if 32 <= byte <= 126 else f"\\x{byte:02x}"
                percent = 100 * count / byte_count
                print(f"    {byte:3d} ('{char_repr}'): {count:6d} times ({percent:5.1f}%)")
        
        print("\nData inspection complete.")

if __name__ == "__main__":
    inspect_data()
