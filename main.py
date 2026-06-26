# -*- coding: utf-8 -*-
import pyIT
from pyIT import WavInstrumentBuilder, PatternBuilder

def main():
    # 1. Inicializa o arquivo .IT
    musica = pyIT.ITfile()
    musica.SongName = b"Batida Direta 180"
    musica.IT = 180  # Configura o BPM
    musica.IS = 6    # Velocidade estável padrão do Tracker

    # 2. Cria o Instrumento e o Sample a partir do WAV (Direto, sem rodeios)
    inst, smp = WavInstrumentBuilder.create_from_wav("samples/c5.wav", "Piano Principal")
    
    # Vincula o instrumento ao sample de índice 1 para todas as 120 notas
    for nota in range(120):
        inst.SampleTable[nota] = [nota, 1]
        
    musica.Instruments.append(inst)
    musica.Samples.append(smp)

    # 3. Cria a sequência de notas com pausas (None)
    # 16 elementos * 4 linhas por nota = 64 linhas exatas (1 padrão completo)
    sequencia = [
        'D-4', 'D-4', 'D-5', None, None, 'A-4', None, None,
        'G#4', None, None, 'G-4', None, 'F-4', 'D-4', 'F-4',
        'G-4', 'C-4', 'C-4', 'D-5', None, None, 'A-4', None,
        'G#4', None, None, 'G-4', None, None, None
    ]

    # 4. Constroi o Pattern e adiciona na ordem de reprodução
    builder_ptn = PatternBuilder(bpm=240, linhas_por_nota=2)
    meu_padrao = builder_ptn.build_pattern(sequencia, id_instrumento=1)
    
    musica.Patterns.append(meu_padrao)
    musica.Orders.extend([0, 255])  # Toca o padrão 0 e finaliza (255)

    # 5. Salva o arquivo final
    musica.write("batida_direta.it")
    print("Arquivo 'batida_direta.it' gerado com sucesso!")

if __name__ == '__main__':
    main()