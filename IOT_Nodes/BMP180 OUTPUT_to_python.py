import serial
import time
import re

# Configuration
SERIAL_PORT = 'COM3'  # Windows: 'COM3', 'COM4', etc.
                      # Mac: '/dev/cu.usbmodem*'
                      # Linux: '/dev/ttyACM0', '/dev/ttyUSB0'
BAUD_RATE = 9600

def read_bme280():
    """Read BME280 sensor data from Teensy via serial"""
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"✓ Connected to {SERIAL_PORT}")
        print("=" * 50)
        print("Reading BME280 Sensor Data...")
        print("=" * 50)
        
        # Wait for Arduino to reset
        time.sleep(2)
        
        # Clear buffer
        ser.reset_input_buffer()
        
        while True:
            try:
                # Read line from serial
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        print(line)
                        
            except KeyboardInterrupt:
                print("\n\n⚠ Stopped by user")
                break
            except Exception as e:
                print(f"Error reading line: {e}")
                
    except serial.SerialException as e:
        print(f"❌ Serial Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if Teensy is connected")
        print("  2. Verify correct port (change SERIAL_PORT variable)")
        print("  3. Close Arduino Serial Monitor if open")
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")

if __name__ == "__main__":
    read_bme280()