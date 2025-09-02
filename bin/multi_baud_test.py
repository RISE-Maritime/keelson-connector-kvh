#!/usr/bin/env python3
"""
Multi-baud Rate Device Detection Script

Try different baud rates and communication settings to identify the connected device.
"""

import subprocess
import time

def test_baud_rate(baud_rate, device_path):
    """Test communication at a specific baud rate"""
    
    print(f"\n=== Testing {baud_rate} baud ===")
    
    # Try to get data at this baud rate
    try:
        proc = subprocess.Popen(
            ['socat', f'{device_path},raw,echo=0,ispeed={baud_rate},ospeed={baud_rate}', '-'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(2)  # Collect for 2 seconds
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=3)
        
        if len(stdout) > 0:
            print(f"Received {len(stdout)} bytes at {baud_rate} baud")
            print(f"First 50 bytes (hex): {stdout[:50].hex()}")
            
            # Check for ASCII content
            try:
                ascii_data = stdout.decode('ascii', errors='ignore')
                printable_chars = ''.join(c for c in ascii_data if c.isprintable())
                if len(printable_chars) > 10:  # If we have decent ASCII content
                    print(f"ASCII content: {printable_chars[:100]}")
            except:
                pass
            
            # Look for patterns that might indicate structured data
            if len(stdout) >= 10:
                # Check byte distribution
                unique_bytes = len(set(stdout[:100]))
                if unique_bytes < 20:  # If very few unique bytes, might be noise
                    print(f"Low entropy data (only {unique_bytes} unique bytes in first 100)")
                else:
                    print(f"Higher entropy data ({unique_bytes} unique bytes in first 100)")
            
            return True
        else:
            print(f"No data received at {baud_rate} baud")
            return False
            
    except Exception as e:
        print(f"Error testing {baud_rate} baud: {e}")
        return False

def test_command_response(command, baud_rate, device_path):
    """Test if device responds to a command at specific baud rate"""
    
    print(f"Testing command '{command}' at {baud_rate} baud...")
    
    try:
        # Send command
        cmd = f'echo "{command}" | socat - {device_path},raw,echo=0,ispeed={baud_rate},ospeed={baud_rate}'
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
        
        time.sleep(1)  # Wait for response
        
        # Read response
        proc = subprocess.Popen(
            ['socat', f'{device_path},raw,echo=0,ispeed={baud_rate},ospeed={baud_rate}', '-'], 
            stdout=subprocess.PIPE
        )
        time.sleep(1)
        proc.terminate()
        stdout, _ = proc.communicate(timeout=2)
        
        if len(stdout) > 0:
            print(f"  Response: {len(stdout)} bytes")
            # Check for meaningful ASCII response
            try:
                ascii_resp = stdout.decode('ascii', errors='ignore')
                printable_resp = ''.join(c for c in ascii_resp if c.isprintable()).strip()
                if len(printable_resp) > 3:
                    print(f"  ASCII response: {printable_resp[:50]}")
                    return True
            except:
                pass
        
        return False
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Test different communication parameters"""
    
    device_path = "/dev/cu.usbserial-FT0R4P590"
    
    print("=== Multi-Baud Rate Device Detection ===")
    print(f"Testing device: {device_path}")
    
    # Common baud rates for various devices
    baud_rates = [
        9600,    # Very common default
        19200,   # Common
        38400,   # Common
        57600,   # Common
        115200,  # What we've been using
        230400,  # High speed
        460800,  # Very high speed
        4800,    # Older devices
        2400,    # Very old devices
    ]
    
    working_rates = []
    
    for baud_rate in baud_rates:
        if test_baud_rate(baud_rate, device_path):
            working_rates.append(baud_rate)
    
    print(f"\n=== Summary ===")
    if working_rates:
        print(f"Baud rates with data: {working_rates}")
    else:
        print("No baud rates produced data")
    
    # Test some common device commands at working baud rates
    if working_rates:
        print(f"\n=== Testing Commands ===")
        test_commands = [
            "AT",           # Modem commands
            "AT+ID=?",      # Some IoT devices
            "?",            # Generic help
            "VER",          # Version command
            "ID",           # ID command
            "*IDN?",        # SCPI identification
            "INFO",         # Info command
            "\r\n",         # Just newlines
        ]
        
        for baud_rate in working_rates[:2]:  # Test top 2 working rates
            print(f"\nTesting commands at {baud_rate} baud:")
            for cmd in test_commands:
                if test_command_response(cmd, baud_rate, device_path):
                    print(f"  ✓ '{cmd}' got response at {baud_rate} baud!")
                    break

if __name__ == "__main__":
    main()
