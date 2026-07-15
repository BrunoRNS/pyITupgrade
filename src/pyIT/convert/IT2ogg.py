import logging
import subprocess
import tempfile
import wave
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydub import AudioSegment # type: ignore

class ModuleRenderer(ABC):
    """Abstract renderer: converts a tracker module file to raw PCM audio."""

    @abstractmethod
    def render(
        self, input_path: Path, sample_rate: int, channels: int
    ) -> bytes:
        """
        Render the entire module to interleaved PCM bytes.

        Args:
            input_path: Path to the tracker module file (.it).
            sample_rate: Desired output sample rate in Hz.
            channels: Number of output channels (1 = mono, 2 = stereo).

        Returns:
            Raw PCM audio data as 16-bit signed little-endian interleaved bytes.
        """
        ...


class AudioEncoder(ABC):
    """Abstract encoder: writes raw PCM data into an OGG Vorbis file."""

    @abstractmethod
    def encode(
        self,
        pcm_data: bytes,
        sample_rate: int,
        channels: int,
        output_path: Union[str, Path],
        quality: Union[str, float] = "128k",
    ) -> None:
        """
        Encode PCM audio and save it as an OGG Vorbis file.

        Args:
            pcm_data: Interleaved 16-bit LE PCM bytes.
            sample_rate: Sample rate in Hz.
            channels: Number of channels.
            output_path: Destination file path.
            quality: Bitrate string (e.g. "128k") or quality float (0.0-1.0).
        """
        ...

class SchismRenderer(ModuleRenderer):
    """
    Renders a tracker module using the Schism Tracker CLI (schism).
    The schism executable must be in the system PATH.
    """

    def __init__(self, schism_executable: str = "schism"):
        """
        Args:
            schism_executable: Name or path of the Schism Tracker executable.
        """
        self.schism_exe: str = schism_executable

    def render(
        self, input_path: Path, sample_rate: int, channels: int
    ) -> bytes:
        """
        Render using Schism Tracker:

        1. Create a temporary WAV file.
        2. Call ``schism -r <sample_rate> -o <temp.wav> <input_path>``.
        3. Read the WAV, extract PCM data.
        4. Downmix to mono if requested, then return raw PCM bytes.
        """
        
        DeprecationWarning(
            "Sample rate usage in Schism rendering is currently ignored.",
            "It will be removed in a future release.",
        )
        
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp_file:
            temp_wav = tmp_file.name

        try:
            if (sys.platform == "darwin") and not (Path(self.schism_exe).is_dir()):
                raise RuntimeError(
                    "Schism Tracker executable must be an .app directory on macOS."
                )
            executable: List[str] = ["open", "-a", self.schism_exe] if sys.platform == "darwin" \
                else [self.schism_exe]
            
            cmd = [
                *executable,
                "--diskwrite",
                temp_wav,
                str(input_path),
            ]
            logging.info("Running: %s", " ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"Schism Tracker failed (exit {result.returncode}):\n"
                    f"stdout: {result.stdout}\nstderr: {result.stderr}"
                )

            with wave.open(temp_wav, "rb") as wf:
                rendered_rate = wf.getframerate()
                rendered_channels = wf.getnchannels()
                rendered_width = wf.getsampwidth()
                frames = wf.readframes(wf.getnframes())

            if rendered_rate != sample_rate:
                logging.warning(
                    "Rendered sample rate %d differs from requested %d",
                    rendered_rate,
                    sample_rate,
                )
            if rendered_width != 2:
                raise RuntimeError(
                    f"Unexpected sample width {rendered_width} (expected 2 bytes)."
                )
            if rendered_channels != 2:
                logging.warning("Rendered WAV is not stereo; channels=%d", rendered_channels)

            pcm_data = frames

            if channels == 1:
                pcm_data = self._downmix_stereo_to_mono(pcm_data)

            return pcm_data

        finally:
            try:
                Path(temp_wav).unlink()
            except OSError:
                pass

    @staticmethod
    def _downmix_stereo_to_mono(pcm_stereo: bytes) -> bytes:
        """
        Downmix interleaved 16-bit LE stereo PCM to mono by averaging channels.
        """
        import array

        stereo = memoryview(pcm_stereo).cast("h")
        half = len(stereo) // 2
        mono = array.array("h", [0] * half)
        for i in range(half):
            mono[i] = (stereo[2 * i] + stereo[2 * i + 1]) // 2
        return mono.tobytes()


class OggVorbisEncoder(AudioEncoder):
    """Encodes PCM data to OGG Vorbis using pydub (which relies on ffmpeg)."""

    def encode(
        self,
        pcm_data: bytes,
        sample_rate: int,
        channels: int,
        output_path: Union[str, Path],
        quality: Union[str, float] = "128k",
    ) -> None:
        sample_width = 2
        audio: Optional[AudioSegment] = None
        audio = AudioSegment( # type: ignore
            data=pcm_data,
            sample_width=sample_width,
            frame_rate=sample_rate,
            channels=channels,
        )
        export_kwargs: Dict[str, str|List[str]] = {
            "format": "ogg",
            "codec": "libvorbis",
        }
        if isinstance(quality, str):
            export_kwargs["bitrate"] = quality
        else:
            export_kwargs["parameters"] = ["-q:a", str(quality)]

        audio.export(output_path, **export_kwargs) # type: ignore
        logging.info("OGG file written to %s", output_path)


class IT2ogg:
    """
    Converts an Impulse Tracker (.it) module file to an OGG Vorbis audio file.

    This class follows the Single Responsibility Principle by delegating
    rendering and encoding to swappable, independent components. Dependency
    Inversion is achieved by depending on the abstract ``ModuleRenderer`` and
    ``AudioEncoder`` interfaces.

    Typical usage::

        converter = IT2ogg("song.it", "song.ogg", sample_rate=44100)
        converter.convert()
    """

    def __init__(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        sample_rate: int = 44100,
        channels: int = 2,
        quality: Union[str, float] = "128k",
        renderer: Optional[ModuleRenderer] = None,
        encoder: Optional[AudioEncoder] = None,
    ):
        """
        Initialize the converter.

        Args:
            input_path: Path to the .it module file.
            output_path: Desired path for the .ogg output file.
            sample_rate: Output sample rate in Hz (default 44100).
            channels: Number of output channels (1 = mono, 2 = stereo).
            quality: Encoding quality – bitrate string like "128k" or
                     Vorbis quality float (0.0-1.0).
            renderer: Optional custom renderer (defaults to SchismRenderer).
            encoder: Optional custom encoder (defaults to OggVorbisEncoder).
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.sample_rate = sample_rate
        self.channels = channels
        self.quality = quality

        self.renderer = renderer if renderer is not None else SchismRenderer()
        self.encoder = encoder if encoder is not None else OggVorbisEncoder()

        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    def convert(self) -> None:
        """
        Execute the full conversion pipeline:
        1. Render the .it module to raw PCM using the configured renderer.
        2. Encode the PCM to OGG Vorbis using the configured encoder.
        """
        if not self.input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        logging.info("Rendering module '%s'...", self.input_path.name)
        pcm_data = self.renderer.render(
            input_path=self.input_path,
            sample_rate=self.sample_rate,
            channels=self.channels,
        )
        logging.info("Rendering complete (%d bytes).", len(pcm_data))

        logging.info("Encoding to OGG Vorbis...")
        self.encoder.encode(
            pcm_data=pcm_data,
            sample_rate=self.sample_rate,
            channels=self.channels,
            output_path=self.output_path,
            quality=self.quality,
        )
        logging.info("Conversion successful: %s", self.output_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python it2ogg.py <input.it> <output.ogg> [sample_rate] [channels]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2]
    sr = int(sys.argv[3]) if len(sys.argv) > 3 else 44100
    ch = int(sys.argv[4]) if len(sys.argv) > 4 else 2

    converter = IT2ogg(in_file, out_file, sample_rate=sr, channels=ch)
    converter.convert()
