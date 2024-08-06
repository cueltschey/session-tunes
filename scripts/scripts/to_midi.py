from music21 import converter, stream
import sqlite3


conn = sqlite3.connect("/home/charles/session-tunes/mueller.db")
c = conn.cursor()
c.execute('SELECT abc, tune_mode, tune_meter FROM Tune WHERE tune_id = 1')
tune = c.fetchone()
conn.close()

print(tune[0])


# Your ABC notation as a string

# Convert ABC to music21 stream
abc_stream = converter.parse(tune[0], format='abc')

# Save the stream to a MIDI file
midi_file = 'output.mid'
abc_stream.write('midi', fp=midi_file)
