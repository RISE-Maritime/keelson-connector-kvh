#!/usr/bin/env python3
"""
Generic IMU Binary Decoder

This script tries to decode the actual binary data coming from the connected device,
using the patterns we detected rather than assuming it's a KVH P1775.
"""

import subprocess
import time
import struct
from datetime import datetime

def find_message_boundaries(data, sync_pattern):
    """Find positions where sync pattern occurs"""
    positions = []
    search_pos = 0
    
    while search_pos < len(data) - len(sync_pattern):
        pos = data.find(sync_pattern, search_pos)
        if pos == -1:
            break
        positions.append(pos)
        search_pos = pos + 1
    
    return positions

def decode_generic_imu_message(data, start_pos):
    """Try to decode a generic IMU message starting at given position"""
    
    # Try different message lengths
    for msg_len in [16, 20, 24, 32, 40, 48, 64]:
        if start_pos + msg_len > len(data):
            continue
            
        message = data[start_pos:start_pos + msg_len]
        
        try:
            # Try different interpretations
            interpretations = [
                # Format: (struct_format, field_names)
                ('>Iffffff', ['header', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']),
                ('<Iffffff', ['header', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']),
                ('>Ihhhhhhh', ['header', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'temp']),
                ('<Ihhhhhhh', ['header', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'temp']),
            ]
            
            for fmt, fields in interpretations:
                if struct.calcsize(fmt) == msg_len:
                    try:
                        values = struct.unpack(fmt, message)
                        
                        # Check if the values look reasonable for IMU data
                        if len(values) >= 4:  # At least header + 3 values
                            reasonable_count = 0
                            for i, val in enumerate(values[1:]):  # Skip header
                                if isinstance(val, float):
                                    if -100 < val < 100:  # Reasonable range for IMU
                                        reasonable_count += 1
                                elif isinstance(val, int):
                                    if -32000 < val < 32000:  # Reasonable range for 16-bit IMU
                                        reasonable_count += 1
                            
                            if reasonable_count >= len(values) // 2:  # At least half reasonable
                                return {
                                    'format': fmt,
                                    'fields': fields,
                                    'values': values,
                                    'raw': message,
                                    'length': msg_len,
                                    'reasonable_values': reasonable_count
                                }
                    except struct.error:
                        continue
        except:
            continue
    
    return None

def main():
    """Main decoding function"""
    
    print("=== Generic IMU Binary Decoder ===")
    
    # Get data from device at the best baud rate we found
    baud_rate = 460800
    device_path = "/dev/cu.usbserial-FT0R4P590"
    
    print(f"Collecting data at {baud_rate} baud...")
    proc = subprocess.Popen(['socat', f'{device_path},raw,echo=0,ispeed={baud_rate},ospeed={baud_rate}', '-'], 
                           stdout=subprocess.PIPE)
    time.sleep(5)  # Collect for 5 seconds
    proc.terminate()
    data, _ = proc.communicate()
    
    print(f"Collected {len(data)} bytes")
    
    # Look for the sync pattern we found
    sync_pattern = b'\x07\xea\x81\x00'
    positions = find_message_boundaries(data, sync_pattern)
    
    print(f"Found {len(positions)} occurrences of sync pattern {sync_pattern.hex()}")
    
    if len(positions) < 2:
        print("Not enough sync patterns found to determine message structure")
        return
    
    # Analyze message intervals
    intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    print(f"Intervals between sync patterns: {list(set(intervals))}")
    
    # Try to decode messages
    successful_decodes = []
    
    for i, pos in enumerate(positions[:5]):  # Try first 5 messages
        result = decode_generic_imu_message(data, pos)
        if result:
            successful_decodes.append((i, pos, result))
            print(f"\nMessage {i+1} at position {pos}:")
            print(f"  Format: {result['format']} (length {result['length']})")
            print(f"  Fields: {result['fields']}")
            print(f"  Values: {result['values']}")
            print(f"  Reasonable values: {result['reasonable_values']}/{len(result['values'])}")
    
    if successful_decodes:
        print(f"\n=== Successfully decoded {len(successful_decodes)} messages ===")
        # Use the best decoding result
        best_result = max(successful_decodes, key=lambda x: x[2]['reasonable_values'])
        
        print(f"Best decoding format: {best_result[2]['format']}")
        print(f"Message length: {best_result[2]['length']} bytes")
        print(f"Field mapping: {list(zip(best_result[2]['fields'], best_result[2]['values']))}")
        
        # Try to decode a few more messages with this format
        print(f"\nDecoding more messages with best format...")
        for i, pos in enumerate(positions[5:10]):  # Next 5 messages
            if pos + best_result[2]['length'] <= len(data):
                msg_data = data[pos:pos + best_result[2]['length']]
                try:
                    values = struct.unpack(best_result[2]['format'], msg_data)
                    print(f"Message {i+6}: {dict(zip(best_result[2]['fields'], values))}")
                except:
                    print(f"Message {i+6}: decode failed")
    else:
        print("No successful message decodes found")
        print("This device may not be an IMU or may use a different protocol entirely")

if __name__ == "__main__":
    main()
