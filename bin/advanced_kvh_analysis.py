#!/usr/bin/env python3
"""
Advanced KVH Data Analysis Script

This script analyzes the binary data coming from the KVH device to understand
its actual format and find any patterns that might indicate message boundaries.
"""

import subprocess
import time
import struct
from collections import Counter

def analyze_data_patterns(data):
    """Analyze binary data for patterns"""
    
    print(f"\n=== Data Pattern Analysis ===")
    print(f"Total bytes: {len(data)}")
    
    # Byte frequency analysis
    byte_counts = Counter(data)
    print(f"\nMost common bytes:")
    for byte_val, count in byte_counts.most_common(10):
        print(f"  0x{byte_val:02X}: {count} times ({count/len(data)*100:.1f}%)")
    
    # Look for potential sync patterns
    print(f"\nLooking for potential sync patterns...")
    
    # Check for common KVH patterns
    kvh_patterns = [
        (b'\xFE\x81\xFF\x56', "KVH Format B"),
        (b'\xFE\x81\xFF\x55', "KVH Format A"),
        (b'\xFE\x81\xFF\x57', "KVH Format C"),
        (b'\xFE\x81', "KVH Header Start"),
        (b'\xFF\xFE', "Possible Header"),
        (b'\x56\xFF\x81\xFE', "Reversed Format B"),
    ]
    
    for pattern, name in kvh_patterns:
        count = data.count(pattern)
        if count > 0:
            print(f"  {name}: {count} occurrences")
            # Show positions
            pos = 0
            positions = []
            while pos < len(data):
                pos = data.find(pattern, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
            print(f"    Positions: {positions[:5]}..." if len(positions) > 5 else f"    Positions: {positions}")
    
    # Look for repeating 4-byte patterns that might be headers
    print(f"\nLooking for repeating 4-byte patterns...")
    four_byte_patterns = Counter()
    for i in range(len(data) - 3):
        pattern = data[i:i+4]
        four_byte_patterns[pattern] += 1
    
    # Show patterns that appear multiple times
    common_patterns = [(pattern, count) for pattern, count in four_byte_patterns.items() if count > 2]
    common_patterns.sort(key=lambda x: x[1], reverse=True)
    
    for pattern, count in common_patterns[:10]:
        print(f"  {pattern.hex()}: {count} times")
        # Check if this could be a message header by looking at spacing
        positions = []
        pos = 0
        while pos < len(data) - 3:
            if data[pos:pos+4] == pattern:
                positions.append(pos)
            pos += 1
        
        if len(positions) >= 2:
            # Calculate intervals between occurrences
            intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            if len(set(intervals)) <= 3:  # If intervals are fairly consistent
                print(f"    Regular intervals: {list(set(intervals))}")

def try_ascii_decode(data):
    """Try to decode parts of the data as ASCII"""
    print(f"\n=== ASCII Analysis ===")
    
    # Try to decode chunks as ASCII
    for i in range(0, min(len(data), 200), 50):
        chunk = data[i:i+50]
        try:
            ascii_text = chunk.decode('ascii', errors='replace')
            if any(c.isprintable() and c not in '\xff\xfe\xfd\xfc' for c in ascii_text):
                print(f"Potential ASCII at position {i}: {ascii_text}")
        except:
            pass

def analyze_as_measurements(data):
    """Try to interpret data as sensor measurements"""
    print(f"\n=== Sensor Data Analysis ===")
    
    # Try different interpretations of the binary data
    interpretations = [
        ('>f', 4, "Big-endian float"),
        ('<f', 4, "Little-endian float"), 
        ('>h', 2, "Big-endian 16-bit int"),
        ('<h', 2, "Little-endian 16-bit int"),
        ('>i', 4, "Big-endian 32-bit int"),
        ('<i', 4, "Little-endian 32-bit int"),
    ]
    
    for fmt, size, desc in interpretations:
        if len(data) >= size * 5:  # Need at least 5 values
            try:
                values = []
                for i in range(0, min(len(data) - size + 1, size * 20), size):
                    value = struct.unpack(fmt, data[i:i+size])[0]
                    values.append(value)
                
                # Check if values look reasonable for IMU data
                if fmt.endswith('f'):  # Float values
                    reasonable = [v for v in values if -100 < v < 100 and abs(v) > 0.001]
                    if len(reasonable) > len(values) * 0.3:  # At least 30% reasonable
                        print(f"{desc}: {len(reasonable)}/{len(values)} reasonable values")
                        print(f"  Sample values: {reasonable[:5]}")
                
            except struct.error:
                pass

def main():
    """Main analysis function"""
    
    print("=== Advanced KVH Data Analysis ===")
    
    # Collect data from device
    print("Collecting data from device...")
    device_path = "/dev/cu.usbserial-FT0R4P590"
    proc = subprocess.Popen(['socat', f'{device_path},raw,echo=0,ispeed=115200,ospeed=115200', '-'], 
                           stdout=subprocess.PIPE)
    time.sleep(5)  # Collect for 5 seconds
    proc.terminate()
    stdout, _ = proc.communicate()
    
    if len(stdout) == 0:
        print("No data received from device!")
        return
    
    print(f"Collected {len(stdout)} bytes")
    
    # Perform various analyses
    analyze_data_patterns(stdout)
    try_ascii_decode(stdout)
    analyze_as_measurements(stdout)
    
    # Save data for manual inspection
    with open('/tmp/kvh_data_sample.bin', 'wb') as f:
        f.write(stdout)
    print(f"\nRaw data saved to /tmp/kvh_data_sample.bin for manual inspection")

if __name__ == "__main__":
    main()
