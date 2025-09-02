#!/usr/bin/env python3
"""
KVH P1775 IMU Device Configuration Utility

This script sends configuration commands to a KVH P1775 IMU device to set it 
to binary format B output mode.

Usage:
  # Send configuration to stdout (for use with socat)
  ./configure_kvh_device.py

  # Or pipe through socat to device
  ./configure_kvh_device.py | socat - /dev/cu.usbserial-FT0R4P590,b115200,raw,echo=0

Based on OpenDLV implementation:
https://git.opendlv.org/testing/opendlv-device-imu-kvhp1775
"""

import sys
import time
import argparse

def configure_kvh_device(verbose=True):
    """
    Send configuration commands to KVH device to enable binary format B output.
    Based on OpenDLV implementation.
    
    Commands to send:
    - =CONFIG,1 - Enable configuration mode
    - =OUTPUTFMT,B - Set output format to B  
    - =OUTPUTRATE,200 - Set output rate to 200Hz
    - =OUTPUTBAUD,115200 - Set baud rate to 115200
    - =CONFIG,0 - Exit configuration mode and start data output
    """
    config_commands = [
        "=CONFIG,1",         # Enter configuration mode
        "=OUTPUTFMT,B",      # Set output format to binary format B
        "=OUTPUTRATE,200",   # Set output rate to 200Hz
        "=OUTPUTBAUD,115200", # Set baud rate to 115200
        "=CONFIG,0"          # Exit configuration mode, start data output
    ]
    
    if verbose:
        print("# Configuring KVH P1775 IMU device for binary format B output", file=sys.stderr)
        print("# Commands will be sent with 200ms delays between each", file=sys.stderr)
    
    for i, cmd in enumerate(config_commands):
        if verbose:
            print(f"# Sending command {i+1}/{len(config_commands)}: {cmd}", file=sys.stderr)
        
        # Send command with line ending
        sys.stdout.write(cmd + '\r\n')
        sys.stdout.flush()
        
        # Delay between commands (important for device to process)
        if i < len(config_commands) - 1:  # Don't delay after last command
            time.sleep(0.2)
    
    if verbose:
        print("# Configuration complete. Device should now output binary format B.", file=sys.stderr)
        print("# Expected output: 40-byte binary messages at 200Hz with header 0xFE81FF56", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Configure KVH P1775 IMU for binary format B output",
        epilog="Example: ./configure_kvh_device.py | socat - /dev/cu.usbserial-FT0R4P590,b115200,raw,echo=0"
    )
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help='Suppress verbose output to stderr')
    
    args = parser.parse_args()
    
    configure_kvh_device(verbose=not args.quiet)

if __name__ == "__main__":
    main()
