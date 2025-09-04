#!/usr/bin/env python3

"""
Test change detection functionality
"""

# Mock the global variables that would normally be set in main
last_gyro_data = None
last_accel_data = None
last_temp = None

def has_significant_change(decoded_data, threshold_gyro=0.01, threshold_accel=0.1, threshold_temp=1.0):
    """
    Check if there's a significant change in IMU data compared to the last reading.
    """
    global last_gyro_data, last_accel_data, last_temp
    
    # Always consider first packet as a change
    if last_gyro_data is None or last_accel_data is None or last_temp is None:
        last_gyro_data = (decoded_data['gyro_x'], decoded_data['gyro_y'], decoded_data['gyro_z'])
        last_accel_data = (decoded_data['accel_x_ms2'], decoded_data['accel_y_ms2'], decoded_data['accel_z_ms2'])
        last_temp = decoded_data['temperature_raw']
        return True
    
    # Check gyro changes
    gyro_change = any(abs(current - last) > threshold_gyro 
                     for current, last in zip([decoded_data['gyro_x'], decoded_data['gyro_y'], decoded_data['gyro_z']], 
                                             last_gyro_data))
    
    # Check acceleration changes
    accel_change = any(abs(current - last) > threshold_accel 
                      for current, last in zip([decoded_data['accel_x_ms2'], decoded_data['accel_y_ms2'], decoded_data['accel_z_ms2']], 
                                              last_accel_data))
    
    # Check temperature change
    temp_change = abs(decoded_data['temperature_raw'] - last_temp) > threshold_temp
    
    # Update stored values if there's a change
    if gyro_change or accel_change or temp_change:
        last_gyro_data = (decoded_data['gyro_x'], decoded_data['gyro_y'], decoded_data['gyro_z'])
        last_accel_data = (decoded_data['accel_x_ms2'], decoded_data['accel_y_ms2'], decoded_data['accel_z_ms2'])
        last_temp = decoded_data['temperature_raw']
        return True
    
    return False

def test_change_detection():
    # Test data - first reading
    data1 = {
        'gyro_x': 0.1, 'gyro_y': 0.2, 'gyro_z': 0.3,
        'accel_x_ms2': 9.8, 'accel_y_ms2': 0.1, 'accel_z_ms2': 0.2,
        'temperature_raw': 25
    }
    
    # Test data - small change (should not trigger)
    data2 = {
        'gyro_x': 0.105, 'gyro_y': 0.205, 'gyro_z': 0.305,  # 0.005 change < 0.01 threshold
        'accel_x_ms2': 9.85, 'accel_y_ms2': 0.15, 'accel_z_ms2': 0.25,  # 0.05 change < 0.1 threshold
        'temperature_raw': 25.5  # 0.5 change < 1.0 threshold
    }
    
    # Test data - significant change
    data3 = {
        'gyro_x': 0.15, 'gyro_y': 0.25, 'gyro_z': 0.35,  # 0.05 change > 0.01 threshold
        'accel_x_ms2': 10.0, 'accel_y_ms2': 0.3, 'accel_z_ms2': 0.4,  # 0.2 change > 0.1 threshold
        'temperature_raw': 27  # 2.0 change > 1.0 threshold
    }
    
    print("Testing change detection:")
    print(f"First reading: {has_significant_change(data1)} (should be True - first reading)")
    print(f"Small change: {has_significant_change(data2)} (should be False - below thresholds)")
    print(f"Significant change: {has_significant_change(data3)} (should be True - above thresholds)")

if __name__ == "__main__":
    test_change_detection()
