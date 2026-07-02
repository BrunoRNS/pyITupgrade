# -*- coding: utf-8 -*-
import wave
import os

from . import ITsample, ITinstrument

class WavInstrumentBuilder:
    @staticmethod
    def create_from_wav(caminho_wav, nome_instrumento="SampleWav"):
        """
        Lê um arquivo .wav e retorna uma tupla (ITinstrument, ITsample)
        pronta para ser adicionada ao seu ITfile.
        """
        if not os.path.exists(caminho_wav):
            raise FileNotFoundError(f"O arquivo {caminho_wav} não existe.")

        # 1. Abre e lê metadados do WAV
        with wave.open(caminho_wav, "rb") as wav:
            canais = wav.getnchannels()
            largura_byte = wav.getsampwidth()
            frequencia = wav.getframerate()
            frames = wav.getnframes()
            dados_pcm = wav.readframes(frames)

        # Avisos preventivos no console
        if canais > 1:
            print(f"[Aviso] O arquivo '{caminho_wav}' é Estéreo. O ideal para Tracker é Mono.")
        if largura_byte != 2:
            print(f"[Aviso] O arquivo '{caminho_wav}' não é 16-bit. Resolução detectada: {largura_byte * 8} bits.")

        # 2. Cria e configura o Sample do IT
        smp = ITsample()
        smp.SampleName = nome_instrumento[:25].encode('ascii', errors='ignore')
        smp.IsSample = True
        smp.Is16bit = (largura_byte == 2)
        smp.IsStereo = (canais == 2)
        smp.C5Speed = frequencia  # Garante que o pitch (Hz) fique perfeito na nota C-5
        smp.SampleData = dados_pcm
        smp.Vol = 64  # Volume máximo padrão

        # 3. Cria e configura o Instrumento do IT
        inst = ITinstrument()
        inst.InstName = f"Inst {nome_instrumento[:20]}".encode('ascii', errors='ignore')
        
        return inst, smp