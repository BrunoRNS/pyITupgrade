# -*- coding: utf-8 -*-
import wave
import os

def verificar_wav(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    with wave.open(caminho_arquivo, "rb") as wav:
        canais = wav.getnchannels()        # 1 = Mono, 2 = Estéreo
        largura_byte = wav.getsampwidth() # 1 = 8 bits, 2 = 16 bits, 4 = 32 bits
        frequencia = wav.getframerate()   # Frequência em Hz (ex: 44100)
        frames = wav.getnframes()          # Total de amostras de áudio
        duracao = frames / float(frequencia)

        bits = largura_byte * 8

        print("=" * 40)
        print(f" Análise do arquivo: {os.path.basename(caminho_arquivo)}")
        print("=" * 40)
        
        # 1. Verifica Canais (Ideal: Mono)
        if canais == 1:
            print(f" Canais: {canais} (Mono) -> [ OK ]")
        else:
            print(f" Canais: {canais} (Estéreo) -> [ INCORRETO: Altere para Mono ]")

        # 2. Verifica Frequência (Ideal: 44100 Hz)
        if frequencia == 44100:
            print(f" Frequência: {frequencia} Hz -> [ OK ]")
        else:
            print(f" Frequência: {frequencia} Hz -> [ RECOMENDADO: Converter para 44100 Hz ]")

        # 3. Verifica Resolução de Bits (Ideal: 16 bits)
        if bits == 16:
            print(f" Resolução: {bits} bits -> [ OK ]")
        else:
            print(f" Resolução: {bits} bits -> [ RECOMENDADO: Converter para 16-bit PCM ]")

        print(f" Duração: {duracao:.2f} segundos")
        print("=" * 40)

        # Diagnóstico Final
        if canais == 1 and frequencia == 44100 and bits == 16:
            print("Resultado: O arquivo está PERFEITO para o Impulse Tracker! 🎉")
        else:
            print("Resultado: O arquivo vai funcionar, mas pode distorcer ou transpor o pitch.")

# Substitua pelo nome exato do seu arquivo .wav
verificar_wav("samples/c5.wav")