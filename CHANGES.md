# KVH IMU Connector Updates - Updated to Format C (OpenDLV C++ Implementation)

## Summary of Changes

This document summarizes the changes made to update the Python KVH IMU connector from Format B to Format C, following the OpenDLV C++ reference implementation at:
https://git.opendlv.org/testing/opendlv-device-imu-kvhp1775

## Major Changes Made

### 1. Format C Implementation (38 bytes vs 40 bytes)
- **Changed from Format B to Format C** - Default in C++ implementation
- **Message size**: 38 bytes instead of 40 bytes
- **Header**: Now uses `0xFE81FF57` (Format C) instead of `0xFE81FF56` (Format B)
- **Structure**: Removed timestamp field, added interleaved temp/magnetic data

### 2. Configuration Commands Updated for Format C
- **Baud Rate**: Changed to 921600 (default for 1000Hz in Format C)
- **Format**: `=OUTPUTFMT,C` instead of `=OUTPUTFMT,B`
- All other configuration commands remain the same (following C++ implementation)

### 3. Interleaved Temperature/Magnetic Data
- **Key Innovation**: Format C interleaves temperature and magnetic field data
- **Based on sequence % 4**:
  - `sequence % 4 == 0`: Temperature (°C)
  - `sequence % 4 == 1`: Magnetic field X (Gauss)
  - `sequence % 4 == 2`: Magnetic field Y (Gauss)
  - `sequence % 4 == 3`: Magnetic field Z (Gauss)

### 4. Enhanced Change Detection
- **Only prints data on significant changes** as requested
- **Detects changes in**:
  - Gyroscope values (threshold: 0.01 rad/s)
  - Acceleration values (threshold: 0.1 m/s²)  
  - Temperature/magnetic data (threshold: 0.1)
  - Sequence mod 4 changes (different data types)
- **Detailed logging** shows what type of data is in each message

### 5. CRC Handling Updated for Format C
- **Split CRC**: Format C uses 2x uint16 instead of 1x uint32
- **CRC calculation**: Adjusted for 38-byte format (excludes header, includes data)
- **Following C++ implementation**: Same CRC-32/MPEG-2 algorithm

### 6. Improved Data Structure
The decoded Format C data structure now includes:
```python
{
    'header': 0xFE81FF57,
    'gyro_x/y/z': float,             # rad/s
    'accel_x/y/z': float,            # g's (raw)
    'accel_x/y/z_ms2': float,        # m/s² (converted)
    'temp_magnetic_data': float,     # Interleaved data
    'sequence_mod4': int,            # 0-3, determines data type
    'temp_data': float,              # When seq%4==0
    'mag_x/y/z_data': float,         # When seq%4==1/2/3
    'temperature_valid': bool,
    'magnetic_valid': bool,
    'crc_valid': bool,
    # ... other fields
}
```

### 7. Enhanced Logging Output
Example of new logging output:
```
IMU Format C CHANGE: gyro=(0.001, -0.002, 0.000)rad/s, accel=(0.050g, 0.980g, 0.010g) -> (0.490, 9.609, 0.098)m/s², seq=124, temp=23.5°C, CRC=OK
IMU Format C CHANGE: gyro=(0.001, -0.002, 0.000)rad/s, accel=(0.050g, 0.980g, 0.010g) -> (0.490, 9.609, 0.098)m/s², seq=125, magX=-0.125G, CRC=OK
```

## Technical Details

### Format C Structure (38 bytes)
```
Bytes 1-4:   Header (0xFE81FF57)
Bytes 5-16:  Gyro X,Y,Z (3x float, rad/s) 
Bytes 17-28: Accel X,Y,Z (3x float, g's)
Bytes 29-32: Temp/Mag data (1x float, interleaved)
Byte 33:     Status (validity flags)
Byte 34:     Sequence (0-127)
Bytes 35-38: CRC (2x uint16: high,low)
```

### Interleaved Data Pattern
Following the C++ implementation exactly:
- Every 4th packet (seq%4==0): Temperature in °C
- Next packet (seq%4==1): Magnetic field X in Gauss
- Next packet (seq%4==2): Magnetic field Y in Gauss  
- Next packet (seq%4==3): Magnetic field Z in Gauss
- Then repeat cycle

### Change Detection Logic
- **Only logs when values change significantly**
- **Tracks**: gyro, accel, temp/mag data, and sequence mod 4
- **Benefits**: Reduces log noise, highlights actual sensor changes
- **Preserves all data**: Still publishes all valid data to Zenoh

## Updated Usage
```bash
# Format C uses 921600 baud rate for 1000Hz (as per C++ implementation)
socat /dev/ttyUSB4,b921600,raw,echo=0 - | bin/main --log-level 10 -r rise -e storakrabban --publish raw --publish imu

# Frame ID support
socat /dev/ttyUSB4,b921600,raw,echo=0 - | bin/main --log-level 10 -r rise -e kvh_imu --publish imu --frame-id "imu_link"
```

## Validation Ranges (unchanged from C++ implementation)
- **Temperature**: -40°C to +75°C
- **Magnetic Field**: -10.0 to +10.0 Gauss  
- **Sequence Number**: 0 to 127 (wrapping)

## Compatibility
- **Maintains Keelson message format compatibility**
- **Enhanced error detection and reporting**  
- **Improved data reliability through CRC validation**
- **Follows OpenDLV Format C reference implementation patterns**
- **Change-based logging reduces output noise**

The updated implementation now correctly follows the OpenDLV C++ reference for Format C, provides interleaved temperature and magnetic field data, includes change-based logging as requested, and maintains full compatibility with the Keelson ecosystem.
