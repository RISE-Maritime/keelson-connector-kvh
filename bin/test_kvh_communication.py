#!/usr/bin/env python3
"""
KVH Device Communication Test

Test if the KVH device responds to various commands and check its status.
"""

import subprocess
import time
import threading
from queue import Queue, Empty

def send_command_and_get_response(command, timeout=3):
    """Send a command and try to get a response"""
    
    device_path = "/dev/cu.usbserial-FT0R4P590"
    
    print(f"\nSending command: {command}")
    
    try:
        # Use expect-like approach with socat
        proc = subprocess.Popen(
            ['socat', '-', f'{device_path},raw,echo=0,ispeed=115200,ospeed=115200'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Send command
        if proc.stdin:
            proc.stdin.write((command + '\r\n').encode())
            proc.stdin.flush()
        
        # Wait a bit for response
        time.sleep(timeout)
        
        # Try to get response
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        
        print(f"Response ({len(stdout)} bytes):")
        if len(stdout) > 0:
            print(f"  Hex: {stdout[:100].hex()}")
            print(f"  ASCII: {repr(stdout[:100])}")
            # Try to decode as ASCII
            try:
                ascii_resp = stdout.decode('ascii', errors='replace')
                printable_chars = ''.join(c for c in ascii_resp if c.isprintable())
                if printable_chars.strip():
                    print(f"  Printable: {printable_chars[:100]}")
            except:
                pass
        else:
            print("  No response")
            
        return stdout
        
    except Exception as e:
        print(f"Error: {e}")
        return b''

def main():
    """Test various KVH commands"""
    
    print("=== KVH Device Communication Test ===")
    
    # Try various commands that KVH devices might respond to
    commands = [
        "=CONFIG,1",      # Enter config mode
        "=STATUS",        # Get status
        "=VERSION",       # Get version
        "=HELP",          # Get help
        "=INFO",          # Get info
        "=ID",            # Get ID
        "=OUTPUTFMT",     # Get current output format
        "=OUTPUTRATE",    # Get current output rate
        "=OUTPUTBAUD",    # Get current baud rate
        "?",              # Generic help
        "*IDN?",          # SCPI identification
        "=RESET",         # Reset device
    ]
    
    responses = {}
    
    for cmd in commands:
        response = send_command_and_get_response(cmd, timeout=2)
        responses[cmd] = response
        time.sleep(0.5)  # Brief pause between commands
    
    # Analyze responses
    print(f"\n=== Response Analysis ===")
    
    meaningful_responses = []
    for cmd, resp in responses.items():
        if len(resp) > 0:
            # Check if response contains ASCII text
            try:
                ascii_resp = resp.decode('ascii', errors='ignore')
                printable_chars = ''.join(c for c in ascii_resp if c.isprintable())
                if printable_chars.strip() and len(printable_chars) > 3:
                    meaningful_responses.append((cmd, printable_chars.strip()))
            except:
                pass
    
    if meaningful_responses:
        print("Commands that got meaningful responses:")
        for cmd, resp in meaningful_responses:
            print(f"  {cmd}: {resp[:100]}")
    else:
        print("No meaningful ASCII responses detected")
    
    # Try to put device in a known state
    print(f"\n=== Attempting to Configure Device ===")
    
    config_commands = [
        "=CONFIG,1",       # Enter config
        "=OUTPUTFMT,A",    # Try ASCII format first
        "=OUTPUTRATE,1",   # Very slow rate for testing
        "=CONFIG,0",       # Exit config
    ]
    
    for cmd in config_commands:
        send_command_and_get_response(cmd, timeout=1)
        time.sleep(1)
    
    print(f"\nWaiting for device output after configuration...")
    time.sleep(2)
    
    # Check output after configuration
    device_path = "/dev/cu.usbserial-FT0R4P590"
    proc = subprocess.Popen(['socat', f'{device_path},raw,echo=0,ispeed=115200,ospeed=115200', '-'], 
                           stdout=subprocess.PIPE)
    time.sleep(5)
    proc.terminate()
    stdout, _ = proc.communicate()
    
    print(f"Device output after configuration ({len(stdout)} bytes):")
    if len(stdout) > 0:
        print(f"First 200 bytes (hex): {stdout[:200].hex()}")
        try:
            ascii_output = stdout.decode('ascii', errors='replace')
            printable_output = ''.join(c for c in ascii_output if c.isprintable() or c in '\n\r')
            if printable_output.strip():
                print(f"ASCII output: {printable_output[:200]}")
        except:
            pass

if __name__ == "__main__":
    main()
