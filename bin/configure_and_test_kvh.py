#!/usr/bin/env python3
"""
KVH P1775 IMU Configuration and Testing Script

This script performs a complete configuration sequence for the KVH P1775 IMU
device and verifies the output format.

Usage:
  ./configure_and_test_kvh.py
"""

import sys
import time
import subprocess
import threading

def send_configuration_commands():
    """Send configuration commands to KVH device via socat"""
    
    # Configuration commands based on OpenDLV implementation
    config_commands = [
        "=CONFIG,1",         # Enter configuration mode
        "=OUTPUTFMT,B",      # Set output format to binary format B  
        "=OUTPUTRATE,200",   # Set output rate to 200Hz
        "=OUTPUTBAUD,115200", # Set baud rate to 115200
        "=CONFIG,0"          # Exit configuration mode, start data output
    ]
    
    print("Sending configuration commands to KVH P1775...")
    
    # Use socat to send commands - use echo to pipe commands
    device_path = "/dev/cu.usbserial-FT0R4P590"
    
    try:
        for i, cmd in enumerate(config_commands):
            print(f"Sending command {i+1}/{len(config_commands)}: {cmd}")
            
            # Send each command individually using echo and socat
            full_cmd = f'echo "{cmd}" | socat - {device_path},raw,echo=0,ispeed=115200,ospeed=115200'
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                print(f"Warning: Command may have failed: {result.stderr}")
            
            time.sleep(0.5)  # Wait between commands
        
        print("Configuration commands sent successfully.")
        return True
        
    except Exception as e:
        print(f"Error sending configuration: {e}")
        return False

def test_device_output():
    """Test the device output to see if it's in binary format"""
    
    print("\nTesting device output format...")
    device_path = "/dev/cu.usbserial-FT0R4P590"
    socat_cmd = f"socat {device_path},raw,echo=0,ispeed=115200,ospeed=115200 -"
    
    try:
        proc = subprocess.Popen(socat_cmd, shell=True, stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        
        # Read data for 3 seconds
        time.sleep(3)
        proc.terminate()
        
        stdout, stderr = proc.communicate()
        
        if stdout:
            print(f"Received {len(stdout)} bytes")
            print(f"First 100 bytes (hex): {stdout[:100].hex()}")
            
            # Look for KVH headers
            headers = [
                (b'\xFE\x81\xFF\x56', "Format B"),
                (b'\xFE\x81\xFF\x55', "Format A"),
                (b'\xFE\x81\xFF\x57', "Format C"),
            ]
            
            found_header = False
            for header_bytes, header_name in headers:
                if header_bytes in stdout:
                    print(f"✓ Found {header_name} header in data!")
                    found_header = True
                    
                    # Find positions of headers
                    pos = 0
                    count = 0
                    while pos < len(stdout) - len(header_bytes):
                        pos = stdout.find(header_bytes, pos)
                        if pos == -1:
                            break
                        count += 1
                        if count <= 3:  # Show first 3 positions
                            print(f"  Header at position {pos}")
                        pos += 1
                    print(f"  Total {header_name} headers found: {count}")
            
            if not found_header:
                print("✗ No KVH binary headers found in data")
                print("Data appears to be ASCII or non-standard format")
                
                # Check if it looks like ASCII
                try:
                    ascii_sample = stdout[:100].decode('ascii', errors='ignore')
                    print(f"ASCII interpretation: {ascii_sample}")
                except:
                    pass
            
            return found_header
        else:
            print("No data received from device")
            return False
            
    except Exception as e:
        print(f"Error testing device output: {e}")
        return False

def main():
    """Main configuration and testing sequence"""
    
    print("=== KVH P1775 IMU Configuration and Test ===")
    
    # Step 1: Send configuration commands
    config_success = send_configuration_commands()
    
    if not config_success:
        print("Configuration failed. Exiting.")
        return False
    
    # Step 2: Wait for device to stabilize
    print("\nWaiting for device to stabilize...")
    time.sleep(2.0)
    
    # Step 3: Test device output
    test_success = test_device_output()
    
    if test_success:
        print("\n✓ Device is configured and outputting binary format!")
        print("You can now run the main connector:")
        print("socat /dev/cu.usbserial-FT0R4P590,raw,echo=0,ispeed=115200,ospeed=115200 - | ./env/bin/python bin/main --publish raw --publish imu --realm test --entity-id kvh_p1775")
    else:
        print("\n✗ Device configuration may have failed or device is not responding properly")
        print("Try running this script again or check device connections")
    
    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
