#!/usr/bin/env python3

import struct
import sys
import os
import logging

def decode_kvh_binary_format_b(data):
    """
    Decode KVH IMU binary format B message (40 bytes total)
    
    Format B structure (big-endian from device):
    - Header: 4 bytes (0xFE81FF56)
    - Gyro X: 4 bytes (float, rad/s)
    - Gyro Y: 4 bytes (float, rad/s)  
    - Gyro Z: 4 bytes (float, rad/s)
    - Accel X: 4 bytes (float, m/s²)
    - Accel Y: 4 bytes (float, m/s²)
    - Accel Z: 4 bytes (float, m/s²)
    - Timestamp: 4 bytes (uint32, microseconds from 1PPS)
    - Status: 1 byte (sensor validity flags)
    - Sequence: 1 byte (0-127, wrapping counter)
    - Temperature: 2 bytes (int16, degrees C)
    - CRC: 4 bytes (uint32)
    """
    if len(data) != 40:
        print(f"ERROR: Expected 40 bytes, got {len(data)}")
        return None
    
    try:
        # Unpack the entire binary data using big-endian format 
        # Device sends data in big-endian (network byte order)
        # Format: I f f f f f f I B B h I (12 items total)
        unpacked = struct.unpack('>IffffffIBBhI', data)
        
        header = unpacked[0]
        gyro_x = unpacked[1]
        gyro_y = unpacked[2] 
        gyro_z = unpacked[3]
        accel_x = unpacked[4]
        accel_y = unpacked[5]
        accel_z = unpacked[6]
        timestamp_us = unpacked[7]
        status = unpacked[8]
        sequence = unpacked[9]
        temperature_raw = unpacked[10]
        crc = unpacked[11]
        
        # Validate header
        if header != 0xFE81FF56:
            print(f"ERROR: Invalid header 0x{header:08X}, expected 0xFE81FF56")
            return None
            
        # Decode status bits (0 = valid, 1 = invalid per OpenDLV code)
        gyro_x_valid = (status & 0x01) == 0
        gyro_y_valid = (status & 0x02) == 0
        gyro_z_valid = (status & 0x04) == 0
        accel_x_valid = (status & 0x10) == 0
        accel_y_valid = (status & 0x20) == 0
        accel_z_valid = (status & 0x40) == 0
        
        return {
            'header': header,
            'gyro_x': gyro_x,
            'gyro_y': gyro_y,
            'gyro_z': gyro_z,
            'accel_x': accel_x,
            'accel_y': accel_y,
            'accel_z': accel_z,
            'timestamp_us': timestamp_us,
            'status': status,
            'sequence': sequence,
            'temperature_raw': temperature_raw,
            'gyro_x_valid': gyro_x_valid,
            'gyro_y_valid': gyro_y_valid,
            'gyro_z_valid': gyro_z_valid,
            'accel_x_valid': accel_x_valid,
            'accel_y_valid': accel_y_valid,
            'accel_z_valid': accel_z_valid,
            'crc': crc
        }
        
    except struct.error as e:
        print(f"ERROR: Failed to unpack binary data: {e}")
        return None

def create_test_message():
    """
    Create a test KVH binary format B message for testing
    """
    # Test values
    header = 0xFE81FF56
    gyro_x = 0.1      # rad/s
    gyro_y = 0.2      # rad/s  
    gyro_z = 0.3      # rad/s
    accel_x = 1.5     # m/s²
    accel_y = -2.1    # m/s²
    accel_z = 9.81    # m/s²
    timestamp_us = 1234567890  # microseconds
    status = 0x00     # all sensors valid
    sequence = 42     # sequence number
    temperature = 250 # temperature raw value
    crc = 0x12345678  # dummy CRC
    
    # Pack into binary format using BIG-ENDIAN (device format)
    # Format: I f f f f f f I B B h I (12 items total)
    #         header + 6 floats + timestamp + status + sequence + temp + crc
    full_message = struct.pack('>IffffffIBBhI', 
                              header,
                              gyro_x, gyro_y, gyro_z,
                              accel_x, accel_y, accel_z,
                              timestamp_us, status, sequence, temperature,
                              crc)
    
    return full_message

def test_decoder():
    """
    Test the binary decoder with a known message
    """
    print("Testing KVH Binary Format B decoder...")
    
    # Create test message
    test_msg = create_test_message()
    
    print(f"Test message length: {len(test_msg)} bytes")
    print(f"Test message hex: {test_msg.hex()}")
    
    # Test the decoder
    result = decode_kvh_binary_format_b(test_msg)
    
    if result is None:
        print("ERROR: Decoder returned None")
        return False
    
    print("\nDecoded values:")
    print(f"  Gyro X: {result['gyro_x']:.3f} rad/s")
    print(f"  Gyro Y: {result['gyro_y']:.3f} rad/s") 
    print(f"  Gyro Z: {result['gyro_z']:.3f} rad/s")
    print(f"  Accel X: {result['accel_x']:.3f} m/s²")
    print(f"  Accel Y: {result['accel_y']:.3f} m/s²")
    print(f"  Accel Z: {result['accel_z']:.3f} m/s²")
    print(f"  Timestamp: {result['timestamp_us']} μs")
    print(f"  Status: 0x{result['status']:02x}")
    print(f"  Sequence: {result['sequence']}")
    print(f"  Temperature: {result['temperature_raw']}")
    print(f"  CRC: 0x{result['crc']:08x}")
    
    print(f"\nSensor validity:")
    print(f"  Gyro X valid: {result['gyro_x_valid']}")
    print(f"  Gyro Y valid: {result['gyro_y_valid']}")
    print(f"  Gyro Z valid: {result['gyro_z_valid']}")
    print(f"  Accel X valid: {result['accel_x_valid']}")
    print(f"  Accel Y valid: {result['accel_y_valid']}")
    print(f"  Accel Z valid: {result['accel_z_valid']}")
    
    # Verify expected values
    expected_values = {
        'gyro_x': 0.1,
        'gyro_y': 0.2, 
        'gyro_z': 0.3,
        'accel_x': 1.5,
        'accel_y': -2.1,
        'accel_z': 9.81,
        'timestamp_us': 1234567890,
        'status': 0x00,
        'sequence': 42,
        'temperature_raw': 250
    }
    
    success = True
    tolerance = 1e-6
    
    for key, expected in expected_values.items():
        actual = result[key]
        if abs(actual - expected) > tolerance:
            print(f"ERROR: {key} mismatch. Expected: {expected}, Got: {actual}")
            success = False
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        
    return success

def test_invalid_messages():
    """
    Test decoder with invalid messages
    """
    print("\nTesting invalid messages...")
    
    # Test with wrong length
    short_msg = b'\xFE\x81\xFF\x56' + b'x' * 10  # Too short
    result = decode_kvh_binary_format_b(short_msg)
    assert result is None, "Should reject short message"
    print("✓ Short message properly rejected")
    
    # Test with wrong header
    wrong_header = b'\xFF\xFF\xFF\xFF' + b'x' * 36  # Wrong header
    result = decode_kvh_binary_format_b(wrong_header)
    assert result is None, "Should reject wrong header"
    print("✓ Wrong header properly rejected")
    
    print("✓ Invalid message tests passed!")

if __name__ == "__main__":
    test_decoder()
    test_invalid_messages()
    print("\nBinary decoder testing complete!")
