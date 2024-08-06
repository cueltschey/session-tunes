import os
from pydub import AudioSegment

# Define paths
midi_file = 'output.mid'
wav_file = 'output.wav'

# Use FluidSynth to convert MIDI to WAV
os.system(f'fluidsynth -ni ./Tabla.sf2 ./output.mid -F ./output.wav -n')

# Load the WAV file to ensure it's created
audio = AudioSegment.from_wav(wav_file)

# Optionally, export as a different format
# audio.export("output.mp3", format="mp3")
