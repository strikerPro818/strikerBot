import pyaudio
import numpy as np

# Set up the microphone array
pa = pyaudio.PyAudio()
mic_array = pyaudio.PyAudio().open(
    format=pyaudio.paInt16,
    channels=6,
    rate=16000,
    input=True,
    input_device_index=0,
    frames_per_buffer=512)

# Compute the steering vector
mic_pos = np.array(
    [
        [0.0, 0.0, 0.0],
        [0.0, 0.0143, 0.0],
        [0.0124, 0.0124, 0.0],
        [0.0143, 0.0, 0.0],
        [0.0124, -0.0124, 0.0],
        [0.0, -0.0143, 0.0],
        [-0.0124, -0.0124, 0.0],
        [-0.0143, 0.0, 0.0],
        [-0.0124, 0.0124, 0.0]
    ]
)
prop_speed = 340.0
fs = 16000
freq = 4000.0
omega = 2 * np.pi * freq
k = omega / prop_speed
A = np.exp(1j * k * np.dot(mic_pos, np.array([np.sin(70 * np.pi / 180), 0, np.cos(70 * np.pi / 180)])))

# Record audio and locate the direction of the voice
while True:
    # Read a chunk of audio from the microphone array
    indata = np.fromstring(mic_array.read(512), dtype=np.int16)

    # Compute the direction of the voice
    direction = np.argmax(np.abs(np.dot(indata.T, A)))

    # Convert the direction to an angle
    angle = (direction / 8.0) * 360.0 - 90.0

    # Print the angle
    print("Voice direction: {:.2f} degrees".format(angle))
