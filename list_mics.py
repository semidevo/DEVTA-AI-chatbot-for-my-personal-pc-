import pyaudio
pa = pyaudio.PyAudio()
print("Available audio INPUT devices:")
print("-" * 50)
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"  [{i}] {info['name']}  (ch={info['maxInputChannels']})")
print()
try:
    default = pa.get_default_input_device_info()
    print(f"Default input device: [{default['index']}] {default['name']}")
except Exception as e:
    print(f"No default input device found: {e}")
pa.terminate()
