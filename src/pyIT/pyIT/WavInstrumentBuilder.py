import os
import struct
import wave
from typing import Tuple

from . import ITinstrument, ITsample


class WavInstrumentBuilder:
    """Create IT-compatible instrument/sample pairs from WAV audio files."""

    @staticmethod
    def _read_wave_format(wav_path: str) -> Tuple[int, int, int, int]:
        """Read the WAV format header and return format metadata."""
        with open(wav_path, "rb") as wav_file:
            riff_header = wav_file.read(12)
            if len(riff_header) < 12 or riff_header[:4] != b"RIFF" or riff_header[8:12] != b"WAVE":
                raise ValueError(f"The file '{wav_path}' is not a valid WAV file.")

            while True:
                chunk_header = wav_file.read(8)
                if not chunk_header:
                    break

                chunk_id, chunk_size = struct.unpack("<4sI", chunk_header)
                if chunk_id == b"fmt ":
                    fmt_bytes = wav_file.read(chunk_size)
                    if len(fmt_bytes) < 16:
                        raise ValueError(f"The file '{wav_path}' has an invalid fmt chunk.")

                    audio_format, channels, sample_rate, _, _, bits_per_sample = struct.unpack(
                        "<HHIIHH", fmt_bytes[:16]
                    )
                    return audio_format, channels, sample_rate, bits_per_sample

                wav_file.seek(chunk_size + (chunk_size % 2), os.SEEK_CUR)

        raise ValueError(f"The file '{wav_path}' does not contain a fmt chunk.")

    @staticmethod
    def _normalize_pcm_data(pcm_data: bytes, audio_format: int, bits_per_sample: int, channels: int) -> Tuple[bytes, bool]:
        """Normalize common WAV encodings into a format suitable for IT samples."""
        if audio_format == 1:  # PCM
            if bits_per_sample == 8:
                return pcm_data, False
            if bits_per_sample == 16:
                return pcm_data, True

            if bits_per_sample in (24, 32):
                return WavInstrumentBuilder._convert_to_16bit_pcm(pcm_data, bits_per_sample, channels), True

        if audio_format == 3:  # IEEE float
            return WavInstrumentBuilder._convert_float_to_16bit_pcm(pcm_data, bits_per_sample), True

        raise ValueError(
            f"Unsupported WAV format: audio_format={audio_format}, bits_per_sample={bits_per_sample}"
        )

    @staticmethod
    def _convert_to_16bit_pcm(pcm_data: bytes, bits_per_sample: int, channels: int) -> bytes:
        """Convert 24-bit or 32-bit PCM data to 16-bit signed PCM."""
        bytes_per_sample = bits_per_sample // 8
        frame_size = bytes_per_sample * channels
        if len(pcm_data) % frame_size != 0:
            pcm_data = pcm_data[: len(pcm_data) - (len(pcm_data) % frame_size)]

        output = bytearray()
        for offset in range(0, len(pcm_data), frame_size):
            frame = pcm_data[offset : offset + frame_size]
            for channel_index in range(channels):
                sample_offset = channel_index * bytes_per_sample
                sample_bytes = frame[sample_offset : sample_offset + bytes_per_sample]

                if bits_per_sample == 24:
                    sample_value = int.from_bytes(sample_bytes, byteorder="little", signed=True)
                else:
                    sample_value = int.from_bytes(sample_bytes, byteorder="little", signed=True)

                sample_value = max(-32768, min(32767, sample_value >> 8))
                output.extend(struct.pack("<h", sample_value))

        return bytes(output)

    @staticmethod
    def _convert_float_to_16bit_pcm(pcm_data: bytes, bits_per_sample: int) -> bytes:
        """Convert IEEE float PCM data to 16-bit signed PCM."""
        output = bytearray()
        if bits_per_sample == 32:
            sample_count = len(pcm_data) // 4
            for offset in range(0, sample_count * 4, 4):
                sample_value = struct.unpack_from("<f", pcm_data, offset)[0]
                sample_value = max(-1.0, min(1.0, sample_value))
                output.extend(struct.pack("<h", int(round(sample_value * 32767))))
        elif bits_per_sample == 64:
            sample_count = len(pcm_data) // 8
            for offset in range(0, sample_count * 8, 8):
                sample_value = struct.unpack_from("<d", pcm_data, offset)[0]
                sample_value = max(-1.0, min(1.0, sample_value))
                output.extend(struct.pack("<h", int(round(sample_value * 32767))))
        else:
            raise ValueError(f"Unsupported float sample width: {bits_per_sample} bits")

        return bytes(output)

    @staticmethod
    def create_from_wav(wav_path: str, instrument_name: str = "SampleWav") -> Tuple[ITinstrument, ITsample]:
        """Load a WAV file and return matching IT instrument and sample objects.

        Args:
            wav_path: Path to the input WAV file.
            instrument_name: Base name used for the created IT sample and instrument.

        Returns:
            A tuple containing the generated IT instrument and IT sample objects.

        Raises:
            FileNotFoundError: If the WAV file does not exist.
            ValueError: If the WAV file is not supported.
        """
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"The file {wav_path} does not exist.")

        audio_format, channels, sample_rate, bits_per_sample = WavInstrumentBuilder._read_wave_format(wav_path)

        with wave.open(wav_path, "rb") as wav_file:
            frame_count = wav_file.getnframes()
            pcm_data = wav_file.readframes(frame_count)

        if channels > 1:
            print(f"[Warning] The file '{wav_path}' is stereo. Mono is preferred for tracker usage.")

        normalized_data, is_16bit = WavInstrumentBuilder._normalize_pcm_data(
            pcm_data, audio_format, bits_per_sample, channels
        )

        if audio_format != 1 or bits_per_sample not in (8, 16):
            print(
                f"[Info] The file '{wav_path}' was normalized to a compatible IT sample format."
            )

        sample = ITsample()
        sample.SampleName = instrument_name[:25].encode("ascii", errors="ignore")
        sample.IsSample = True
        sample.Is16bit = is_16bit
        sample.IsStereo = channels == 2
        sample.C5Speed = sample_rate
        sample.SampleData = normalized_data
        sample.Vol = 64

        instrument = ITinstrument()
        instrument.InstName = f"Inst {instrument_name[:20]}".encode("ascii", errors="ignore")

        return instrument, sample
    
