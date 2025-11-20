#!/usr/bin/env python3
"""
MIDI Converter for Alternative Rock Track Structure
Converts the musical notation into a playable MIDI file
"""

import mido
from mido import MidiFile, MidiTrack, Message
import math

class MidiConverter:
    def __init__(self):
        self.mid = MidiFile()
        self.tempo = 85  # BPM
        self.ticks_per_beat = 480
        self.key = 'Dm'  # D minor
        
        # Note mapping (MIDI note numbers)
        self.notes = {
            'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
            'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
            'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
        }
        
        # Chord definitions in D minor key
        self.chords = {
            'Dm': [62, 65, 69],      # D, F, A
            'Bb': [70, 62, 65],      # Bb, D, F  
            'F': [65, 69, 60],       # F, A, C
            'C': [60, 64, 67],       # C, E, G
            'Gm': [67, 70, 62],      # G, Bb, D
            'A7': [69, 61, 64, 67]   # A, C#, E, G
        }
        
        # Section structures
        self.structure = [
            ('intro', 8),
            ('verse1', 16),
            ('pre_chorus1', 8),
            ('chorus1', 16),
            ('verse2', 16),
            ('pre_chorus2', 8),
            ('chorus2', 16),
            ('bridge', 12),
            ('final_chorus', 24),
            ('outro', 8)
        ]
        
    def beats_to_ticks(self, beats):
        """Convert beats to MIDI ticks"""
        return int(beats * self.ticks_per_beat)
        
    def add_tempo_change(self, track):
        """Add tempo setting to track"""
        tempo_msg = mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo))
        track.append(tempo_msg)
        
    def note_name_to_midi(self, note_name):
        """Convert note name (e.g., 'D5') to MIDI number"""
        if not note_name or note_name == 'rest':
            return 60  # Default to middle C
            
        if len(note_name) < 2:
            return self.notes.get(note_name, 60)
        
        try:
            # Extract note and octave
            if note_name[-1].isdigit():
                note = note_name[:-1]
                octave = int(note_name[-1])
            else:
                # No octave specified, default to 4
                note = note_name
                octave = 4
                
            base_note = self.notes.get(note, 60)
            
            # Adjust for octave (octave 4 = middle C area)
            midi_note = base_note + (octave - 4) * 12
            
            # Clamp to valid MIDI range
            midi_note = max(0, min(127, midi_note))
            
            return midi_note
            
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse note '{note_name}', using default. Error: {e}")
            return 60
        
    def add_chord_progression(self, track, chords, bars, velocity=80, time_offset=0):
        """Add chord progression to track"""
        beats_per_chord = 4  # Whole note chords
        
        current_time = time_offset
        
        # Create the chord sequence for the specified number of bars
        chord_sequence = (chords * (bars // len(chords) + 1))[:bars]
        
        for i, chord in enumerate(chord_sequence):
            if chord in self.chords:
                chord_notes = self.chords[chord]
                
                # Add chord notes
                for note in chord_notes:
                    track.append(Message('note_on', channel=0, note=note, 
                                       velocity=velocity, time=current_time))
                    current_time = 0  # Only first note gets the time offset
                
                # Hold for the duration
                hold_time = self.beats_to_ticks(beats_per_chord)
                
                # Turn off chord notes
                for note in chord_notes:
                    track.append(Message('note_off', channel=0, note=note, 
                                       velocity=0, time=hold_time))
                    hold_time = 0  # Only first note gets the time offset
                    
                current_time = 0
                
    def add_melody(self, track, melody_notes, rhythm_pattern, velocity=90, time_offset=0):
        """Add melody line to track"""
        current_time = time_offset
        
        for i, note_name in enumerate(melody_notes):
            if note_name == 'rest':
                current_time += self.beats_to_ticks(rhythm_pattern[i % len(rhythm_pattern)])
                continue
                
            midi_note = self.note_name_to_midi(note_name)
            duration = self.beats_to_ticks(rhythm_pattern[i % len(rhythm_pattern)])
            
            # Note on
            track.append(Message('note_on', channel=1, note=midi_note, 
                               velocity=velocity, time=current_time))
            
            # Note off
            track.append(Message('note_off', channel=1, note=midi_note, 
                               velocity=0, time=duration))
            
            current_time = 0
            
    def add_bass_line(self, track, bass_notes, velocity=85, time_offset=0):
        """Add bass line to track"""
        current_time = time_offset
        beats_per_note = 4  # Whole notes
        
        for note_name in bass_notes:
            midi_note = self.note_name_to_midi(note_name)
            duration = self.beats_to_ticks(beats_per_note)
            
            # Note on
            track.append(Message('note_on', channel=2, note=midi_note, 
                               velocity=velocity, time=current_time))
            
            # Note off  
            track.append(Message('note_off', channel=2, note=midi_note, 
                               velocity=0, time=duration))
            
            current_time = 0
            
    def create_section(self, section_name, bars, start_time=0):
        """Create a specific section of the song"""
        section_data = {
            'intro': {
                'chords': ['Dm', 'Bb', 'F', 'C'] * 2,
                'melody': ['D4', 'F4', 'G4', 'F4', 'D4', 'C4', 'D4', 'D4'] * 2,
                'bass': ['D2', 'Bb1', 'F1', 'C2'] * 2,
                'velocity': 60,
                'rhythm': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
            },
            'verse1': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'A7'] * 2,
                'melody': ['D4', 'F4', 'G4', 'F4', 'D4', 'C4', 'D4', 'D4',
                          'F4', 'G4', 'A4', 'G4', 'F4', 'D4', 'F4', 'F4'] * 1,
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'D2', 'Bb1', 'F1', 'A1'] * 2,
                'velocity': 65,
                'rhythm': [1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 2.0]
            },
            'pre_chorus1': {
                'chords': ['Bb', 'C', 'Dm', 'Dm', 'Bb', 'C', 'F', 'A7'],
                'melody': ['Bb4', 'A4', 'G4', 'F4', 'G4', 'A4', 'Bb4', 'C5',
                          'D5', 'C5', 'Bb4', 'A4', 'G4', 'F4', 'G4', 'A4'],
                'bass': ['Bb1', 'C2', 'D2', 'D2', 'Bb1', 'C2', 'F1', 'A1'],
                'velocity': 75,
                'rhythm': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
            },
            'chorus1': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Gm', 'Bb', 'F', 'A7'] * 2,
                'melody': ['D5', 'F5', 'G5', 'F5', 'D5', 'C5', 'D5', 'D5',
                          'Bb4', 'C5', 'D5', 'F5', 'G5', 'A5', 'F5', 'D5'] * 1,
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'G1', 'Bb1', 'F1', 'A1'] * 2,
                'velocity': 100,
                'rhythm': [1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0]
            },
            'verse2': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'A7'] * 2,
                'melody': ['D4', 'F4', 'G4', 'F4', 'D4', 'C4', 'D4', 'D4',
                          'F4', 'G4', 'A4', 'G4', 'F4', 'D4', 'F4', 'F4'] * 1,
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'D2', 'Bb1', 'F1', 'A1'] * 2,
                'velocity': 70,
                'rhythm': [1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 2.0]
            },
            'pre_chorus2': {
                'chords': ['Bb', 'C', 'Dm', 'Dm', 'Bb', 'C', 'F', 'A7'],
                'melody': ['Bb4', 'A4', 'G4', 'F4', 'G4', 'A4', 'Bb4', 'C5',
                          'D5', 'C5', 'Bb4', 'A4', 'G4', 'F4', 'G4', 'A4'],
                'bass': ['Bb1', 'C2', 'D2', 'D2', 'Bb1', 'C2', 'F1', 'A1'],
                'velocity': 85,
                'rhythm': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
            },
            'chorus2': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Gm', 'Bb', 'F', 'A7'] * 2,
                'melody': ['D5', 'F5', 'G5', 'F5', 'D5', 'C5', 'D5', 'D5',
                          'Bb4', 'C5', 'D5', 'F5', 'G5', 'A5', 'F5', 'D5'] * 1,
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'G1', 'Bb1', 'F1', 'A1'] * 2,
                'velocity': 110,
                'rhythm': [1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0]
            },
            'bridge': {
                'chords': ['Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'A7', 'A7', 'Gm', 'Bb', 'C', 'Dm'],
                'melody': ['F5', 'G5', 'A5', 'Bb5', 'A5', 'G5', 'F5', 'F5',
                          'A5', 'G5', 'F5', 'D5', 'F5', 'G5', 'A5', 'Bb5'],
                'bass': ['Bb1', 'F1', 'C2', 'D2', 'Bb1', 'F1', 'A1', 'A1', 'G1', 'Bb1', 'C2', 'D2'],
                'velocity': 95,
                'rhythm': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
            },
            'final_chorus': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Gm', 'Bb', 'F', 'A7'] * 3,
                'melody': ['D5', 'F5', 'G5', 'F5', 'D5', 'C5', 'D5', 'D5',
                          'Bb4', 'C5', 'D5', 'F5', 'G5', 'A5', 'F5', 'D5'] * 3,
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'G1', 'Bb1', 'F1', 'A1'] * 3,
                'velocity': 127,
                'rhythm': [1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0]
            },
            'outro': {
                'chords': ['Dm', 'Bb', 'F', 'C', 'Dm', 'Dm'],
                'melody': ['D5', 'F5', 'G5', 'F5', 'D5', 'D5'],
                'bass': ['D2', 'Bb1', 'F1', 'C2', 'D2', 'D2'],
                'velocity': 60,
                'rhythm': [2.0, 2.0, 2.0, 2.0, 4.0, 4.0]
            }
        }
        
        return section_data.get(section_name, section_data['intro'])
        
    def generate_midi(self, filename='alternative_rock_track.mid'):
        """Generate the complete MIDI file"""
        
        # Create tracks
        chord_track = MidiTrack()
        melody_track = MidiTrack()
        bass_track = MidiTrack()
        lead_track = MidiTrack()
        
        # Add tempo to first track
        self.add_tempo_change(chord_track)
        
        # Set instruments
        chord_track.append(Message('program_change', channel=0, program=25, time=0))  # Steel Guitar
        melody_track.append(Message('program_change', channel=1, program=53, time=0))  # Voice
        bass_track.append(Message('program_change', channel=2, program=33, time=0))   # Electric Bass
        lead_track.append(Message('program_change', channel=3, program=29, time=0))   # Electric Guitar
        
        current_time = 0
        
        # Generate each section
        for section_name, bars in self.structure:
            section_data = self.create_section(section_name, bars)
            
            # Add section to tracks
            self.add_chord_progression(
                chord_track, 
                section_data['chords'], 
                bars, 
                section_data['velocity'],
                current_time if section_name == 'intro' else 0
            )
            
            self.add_melody(
                melody_track,
                section_data['melody'],
                section_data['rhythm'],
                min(section_data['velocity'] + 10, 127),
                current_time if section_name == 'intro' else 0
            )
            
            self.add_bass_line(
                bass_track,
                section_data['bass'],
                max(50, section_data['velocity'] - 15),
                current_time if section_name == 'intro' else 0
            )
            
            current_time = 0  # Reset for subsequent sections
            
        # Add lead guitar hook for choruses
        lead_hook = ['A5', 'F5', 'D5', 'F5', 'G5', 'A5', 'Bb5', 'A5',
                    'F5', 'D5', 'C5', 'D5', 'F5', 'G5', 'F5', 'D5']
        lead_rhythm = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
        
        # Add lead to chorus sections (approximate timing)
        chorus_start_time = self.beats_to_ticks(32)  # After intro + verse + pre-chorus
        self.add_melody(lead_track, lead_hook, lead_rhythm, 100, chorus_start_time)
        
        # Add tracks to MIDI file
        self.mid.tracks.append(chord_track)
        self.mid.tracks.append(melody_track) 
        self.mid.tracks.append(bass_track)
        self.mid.tracks.append(lead_track)
        
        # Save file
        self.mid.save(filename)
        print(f"MIDI file saved as: {filename}")
        
        return filename

def main():
    """Main function to run the MIDI converter"""
    print("Generating Alternative Rock MIDI track...")
    print("Style: Theory of a Deadman meets Blue October 'Hate Me'")
    print("With Imagine Dragons and My Chemical Romance influences")
    print()
    
    converter = MidiConverter()
    midi_file = converter.generate_midi()
    
    print(f"\nMIDI generation complete!")
    print(f"Tempo: {converter.tempo} BPM")
    print(f"Key: D minor")
    print(f"Total sections: {len(converter.structure)}")
    print("\nTrack assignments:")
    print("- Channel 0: Rhythm Guitar/Chords (Steel Guitar)")
    print("- Channel 1: Lead Vocals (Voice)")  
    print("- Channel 2: Bass Guitar (Electric Bass)")
    print("- Channel 3: Lead Guitar (Electric Guitar)")
    print(f"\nFile saved as: {midi_file}")
    print("\nReady to use as audio seed for Suno!")

if __name__ == "__main__":
    main()
