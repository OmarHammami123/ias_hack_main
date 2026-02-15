import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import queue

# Configuration
SAMPLE_RATE = 44100  # Hz
BLOCK_SIZE = 2048    # samples
DEVICE_NAME = 'Teensy'  # Partial name match

# Queue for audio data
audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    """Callback function for audio stream"""
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata.copy())

def find_teensy_device():
    """Find Teensy audio device"""
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if DEVICE_NAME.lower() in device['name'].lower() and device['max_input_channels'] > 0:
            print(f"✓ Found: {device['name']} (ID: {i})")
            return i
    return None

def monitor_audio():
    """Monitor audio from INMP441 via Teensy"""
    
    # Find Teensy device
    device_id = find_teensy_device()
    
    if device_id is None:
        print("❌ Teensy audio device not found")
        print("\nAvailable input devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        return
    
    print("=" * 50)
    print("INMP441 Audio Monitor")
    print("=" * 50)
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Block Size: {BLOCK_SIZE} samples")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        with sd.InputStream(device=device_id, 
                           channels=1, 
                           samplerate=SAMPLE_RATE,
                           blocksize=BLOCK_SIZE,
                           callback=audio_callback):
            
            while True:
                # Get audio data
                audio_data = audio_queue.get()
                
                # Calculate audio level
                rms = np.sqrt(np.mean(audio_data**2))
                peak = np.max(np.abs(audio_data))
                
                # Visual level meter
                bars = int(peak * 50)
                meter = '█' * bars + '░' * (50 - bars)
                
                print(f"RMS: {rms:.4f} | Peak: {peak:.4f} | [{meter}]", end='\r')
                
    except KeyboardInterrupt:
        print("\n\n⚠ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    monitor_audio()