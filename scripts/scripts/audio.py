from music21 import converter, stream
import os
from pydub import AudioSegment

class AudioManager():
    def create_audio_converter(self, ref_num, title, meter, key, abc, default_length=None):

        abc_notation = f"""
        X: {ref_num}
        T: {title}
        M: {meter}
        K: {key}
        """

        if default_length:
            abc_notation += f"L: {default_length}\n"

        abc_notation += abc

        self.audio_stream = converter.parse(abc_notation, format='abc')

    def write_wav(self, output_filepath, font_file):
        midi_file = output_filepath.split('.')[0] + ".mid"
        self.audio_stream.write('midi', midi_file)
        os.system(f'fluidsynth -ni {font_file} {midi_file} -F {output_filepath} -n')
        try:
            audio = AudioSegment.from_wav(output_filepath)
        except err:
            print("Failed to create wav file: ", err)

