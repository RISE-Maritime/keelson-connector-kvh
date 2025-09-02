#!/usr/bin/env python3
"""
Simple KVH device reset and configuration script
"""

import subprocess
import time

def send_single_command(cmd):
    """Send a single command to the KVH device"""
    device_path = "/dev/cu.usbserial-FT0R4P590"
    
    print(f"Sending: {cmd}")
    
    # Use printf to send command with proper line endings
    full_cmd = f'printf "{cmd}\\r\\n" | socat - {device_path},raw,echo=0,ispeed=115200,ospeed=115200,bs1,cs8,cstopb=1'
    
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"  ✓ Command sent successfully")
        else:
            print(f"  ✗ Command failed: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ✓ Command sent (timeout expected)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main configuration sequence"""
    
    print("=== KVH P1775 Reset and Configuration ===")
    
    # Try to stop any current data output first
    print("\n1. Attempting to stop current data output...")
    send_single_command("=CONFIG,1")  # Enter config mode
    time.sleep(1)
    
    print("\n2. Sending reset command...")
    send_single_command("=RESET")
    time.sleep(2)  # Wait for reset
    
    print("\n3. Configuring device...")
    commands = [
        "=CONFIG,1",         # Enter configuration mode
        "=OUTPUTFMT,B",      # Set output format to binary format B
        "=OUTPUTRATE,10",    # Set lower output rate first (10Hz)  
        "=OUTPUTBAUD,115200", # Set baud rate to 115200
        "=CONFIG,0"          # Exit configuration mode
    ]
    
    for cmd in commands:
        send_single_command(cmd)
        time.sleep(1)  # Wait between commands
    
    print("\n4. Waiting for device to stabilize...")
    time.sleep(3)
    
    print("\n5. Testing output...")
    proc = subprocess.Popen(['socat', '/dev/cu.usbserial-FT0R4P590,raw,echo=0,ispeed=115200,ospeed=115200', '-'], 
                           stdout=subprocess.PIPE)
    time.sleep(5)  # Collect data for 5 seconds
    proc.terminate()
    stdout, _ = proc.communicate()
    
    print(f"Received {len(stdout)} bytes")
    print(f"First 100 bytes (hex): {stdout[:100].hex()}")
    
    # Look for KVH headers
    headers = [
        (b'\xFE\x81\xFF\x56', "Format B"),
        (b'\xFE\x81\xFF\x55', "Format A"), 
        (b'\xFE\x81\xFF\x57', "Format C"),
    ]
    
    found = False
    for header_bytes, header_name in headers:
        if header_bytes in stdout:
            print(f"✓ Found {header_name} header!")
            found = True
            break
    
    if not found:
        print("✗ No KVH headers found. Device may not be in binary format.")
        print("Trying to detect any patterns...")
        
        # Check for repeating patterns that might indicate message boundaries
        if len(stdout) >= 40:
            for i in range(min(len(stdout) - 40, 100)):
                chunk = stdout[i:i+4]
                if chunk == b'\xFE\x81' or chunk == b'\x81\xFE':
                    print(f"Potential header pattern at position {i}: {chunk.hex()}")

if __name__ == "__main__":
    main()
