from pathlib import Path

import numpy as np
from scipy.io import wavfile

class MathSynthesizer:
    """Generate simple waveform audio files for musical notes.

    The synthesizer creates WAV files for different oscillator shapes using
    a fixed 8 kHz sample rate and 8-bit unsigned PCM output. It is intended
    for lightweight audio generation and simple testing scenarios.
    """

    def __init__(self, sample_rate: int = 8000):
        """Initialize the synthesizer with a target sample rate.

        Args:
            sample_rate: Number of samples per second used to generate the audio.
                Defaults to 8000 Hz.
        """
        
        self.sample_rate = sample_rate
        self.base_frequencies = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }

    def _calculate_frequency(self, note_name: str, octave: int) -> float:
        """Calculate the frequency of a note for a given octave.

        Args:
            note_name: Musical note name such as "C", "C#", or "B".
            octave: Octave number where middle C is typically in octave 4.

        Returns:
            The corresponding frequency in hertz.
        """
        
        octave_distance = octave - 4
        return self.base_frequencies[note_name.upper()] * (2 ** octave_distance)

    def _save_wav(self, signal: np.ndarray, duration: float, output_file: str):
        """Apply an envelope and write a normalized 8-bit WAV file.

        Args:
            signal: Raw waveform samples before envelope shaping.
            duration: Duration of the generated sound in seconds.
            output_file: Path to the output WAV file.
        """
        
        t = np.linspace(0, duration, len(signal), endpoint=False)
        
        attack = 1.0 - np.exp(-100 * t)
        decay = np.exp(-2.5 * t)
        envelope = attack * decay
        
        final_signal: np.ndarray = signal * envelope
        
        peak = np.max(np.abs(final_signal))
        if peak == 0:
            final_signal = np.zeros_like(final_signal)
        else:
            final_signal = final_signal / peak

        audio_8bit = np.clip(np.round((final_signal * 127.5) + 127.5), 0, 255).astype(np.uint8)
        
        wavfile.write(output_file, self.sample_rate, audio_8bit)
        print(f"File '{output_file}' generated successfully.")

    def sine_wave(self, note: str, octave: int, duration: float, output_file: str):
        """Generate a sine-wave tone and save it as a WAV file.

        Args:
            note: Note name to play, such as "C" or "F#".
            octave: Octave in which the note should be generated.
            duration: Length of the tone in seconds.
            output_file: Destination path for the generated WAV file.
        """
        
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = np.sin(2 * np.pi * freq * t)
        self._save_wav(signal, duration, output_file)

    def square_wave(self, note: str, octave: int, duration: float, output_file: str):
        """Generate a square-wave tone with a sharp, buzzy timbre.

        Args:
            note: Note name to play.
            octave: Octave in which the note should be generated.
            duration: Length of the tone in seconds.
            output_file: Destination path for the generated WAV file.
        """
        
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = np.sign(np.sin(2 * np.pi * freq * t))
        self._save_wav(signal, duration, output_file)

    def sawtooth_wave(self, note: str, octave: int, duration: float, output_file: str):
        """Generate a sawtooth-wave tone with a bright, edgy timbre.

        Args:
            note: Note name to play.
            octave: Octave in which the note should be generated.
            duration: Length of the tone in seconds.
            output_file: Destination path for the generated WAV file.
        """
        
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = 2 * (t * freq - np.floor(0.5 + t * freq))
        self._save_wav(signal, duration, output_file)

    def triangle_wave(self, note: str, octave: int, duration: float, output_file: str):
        """Generate a triangle-wave tone with a softer timbre.

        Args:
            note: Note name to play.
            octave: Octave in which the note should be generated.
            duration: Length of the tone in seconds.
            output_file: Destination path for the generated WAV file.
        """
        
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        signal = 2 * np.abs(2 * (t * freq - np.floor(0.5 + t * freq))) - 1
        self._save_wav(signal, duration, output_file)

    def pwm_pulse_wave(self, note: str, octave: int, duration: float, output_file: str):
        """Generate a pulse-width-modulated wave with a moving duty cycle.

        The duty cycle varies over time, creating a more organic and analog-like
        character compared to a static square wave.

        Args:
            note: Note name to play.
            octave: Octave in which the note should be generated.
            duration: Length of the tone in seconds.
            output_file: Destination path for the generated WAV file.
        """
        
        freq = self._calculate_frequency(note, octave)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        lfo = 0.5 + 0.4 * np.sin(2 * np.pi * 3.0 * t)
        
        wave_phase = (t * freq) % 1.0
        signal = np.where(wave_phase < lfo, 1.0, -1.0)
        
        self._save_wav(signal, duration, output_file)

def main(output_dir: Path|None = None):
    
    if output_dir is None:
        output_dir = Path(__file__).parent.resolve()
    
    synthesizer = MathSynthesizer()

    synthesizer.sine_wave(
        note="C",
        octave=5,
        duration=2.0,
        output_file=str(output_dir / "1_sine.wav")
    )
    synthesizer.square_wave(
        note="C",
        octave=5,
        duration=2.0,
        output_file=str(output_dir / "2_square.wav")
    )
    synthesizer.sawtooth_wave(
        note="C",
        octave=5,
        duration=2.0,
        output_file=str(output_dir / "3_sawtooth.wav")
    )
    synthesizer.triangle_wave(
        note="C",
        octave=5,
        duration=2.0,
        output_file=str(output_dir / "4_triangle.wav")
    )
    synthesizer.pwm_pulse_wave(
        note="C",
        octave=5,
        duration=2.0,
        output_file=str(output_dir / "5_pwm_pulse.wav")
    )

if __name__ == "__main__":
    
    assets: Path = Path(__file__).parent.parent / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    assets = assets.resolve()
    
    main(output_dir=assets)

