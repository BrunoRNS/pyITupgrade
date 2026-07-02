import numpy as np
from scipy.io import wavfile

class MathSynthesizer:
    def __init__(self, sample_rate=44100):
        """Initializes the synthesizer with the sample rate (default 44.1kHz)."""
        self.sample_rate = sample_rate
        # Base frequencies for notes in octave 4
        self.base_frequencies = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }

    def _calculate_frequency(self, note_name, octave):
        """Calculates the exact frequency in Hz based on the note and octave."""
        octave_distance = octave - 4
        return self.base_frequencies[note_name.upper()] * (2 ** octave_distance)

    def _save_wav(self, signal, duration, output_file):
        """Applies a decay envelope, normalizes, and saves the file."""
        t = np.linspace(0, duration, len(signal), endpoint=False)
        
        # Envelope for fast attack and smooth decay
        attack = 1.0 - np.exp(-100 * t)
        decay = np.exp(-2.5 * t)
        envelope = attack * decay
        
        final_signal = signal * envelope
        
        # Normalization and 16-bit conversion
        final_signal = final_signal / np.max(np.abs(final_signal))
        audio_16bit = (final_signal * 32767).astype(np.int16)
        
        wavfile.write(output_file, self.sample_rate, audio_16bit)
        print(f"File '{output_file}' generated successfully.")

    def sine_wave(self, note, octave, duration, output_file):
        """1. SINE WAVE: Pure and clean sound (flute or tuning fork style)."""
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = np.sin(2 * np.pi * freq * t)
        self._save_wav(signal, duration, output_file)

    def square_wave(self, note, octave, duration, output_file):
        """2. SQUARE WAVE: Hollow and symmetrical sound (classic Chiptune/8-bit style)."""
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = np.sign(np.sin(2 * np.pi * freq * t))
        self._save_wav(signal, duration, output_file)

    def sawtooth_wave(self, note, octave, duration, output_file):
        """3. SAWTOOTH WAVE: Bright, harsh, and rich sound (Synthwave synthesizer style)."""
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = 2 * (t * freq - np.floor(0.5 + t * freq))
        self._save_wav(signal, duration, output_file)

    def triangle_wave(self, note, octave, duration, output_file):
        """4. TRIANGLE WAVE: Soft sound with a slight brightness (woodwind or recorder style)."""
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = 2 * np.abs(2 * (t * freq - np.floor(0.5 + t * freq))) - 1
        self._save_wav(signal, duration, output_file)

    def pwm_pulse_wave(self, note, octave, duration, output_file):
        """5. PULSE WAVE (PWM): An asymmetrical variation of the square wave. 
        The duty cycle varies over time, giving an organic 'chorus' or analog string effect."""
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # A low-frequency oscillator (LFO) modulates the wave width between 10% and 90%
        lfo = 0.5 + 0.4 * np.sin(2 * np.pi * 3.0 * t) # 3Hz LFO
        
        # Generates the dynamic pulse based on the fluctuating LFO value
        wave_phase = (t * freq) % 1.0
        signal = np.where(wave_phase < lfo, 1.0, -1.0)
        
        self._save_wav(signal, duration, output_file)

# --- Execution ---
if __name__ == "__main__":
    synthesizer = MathSynthesizer()

    # Generates the 5 melodic waves on note C5
    synthesizer.sine_wave(note="C", octave=5, duration=2.0, output_file="1_sine.wav")
    synthesizer.square_wave(note="C", octave=5, duration=2.0, output_file="2_square.wav")
    synthesizer.sawtooth_wave(note="C", octave=5, duration=2.0, output_file="3_sawtooth.wav")
    synthesizer.triangle_wave(note="C", octave=5, duration=2.0, output_file="4_triangle.wav")
    synthesizer.pwm_pulse_wave(note="C", octave=5, duration=2.0, output_file="5_pwm_pulse.wav")
