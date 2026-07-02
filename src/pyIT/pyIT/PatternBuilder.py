# -*- coding: utf-8 -*-
# Importa a classe ITpattern de dentro do módulo ITpattern
from .ITpattern import ITpattern

class PatternBuilder:
    def __init__(self, bpm=180, linhas_por_nota=4):
        """
        :param bpm: Batidas por minuto (IT).
        :param linhas_por_nota: Quantas linhas do Tracker cada nota vai ocupar.
        """
        self.bpm = bpm
        self.linhas_por_nota = linhas_por_nota

        # Dicionário base de semitons para calcular qualquer oitava dinamicamente
        self._semitons = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }

    def string_para_numero(self, nome_nota):
        if not nome_nota:
            return None
            
        # Normaliza o formato (ex: transforma "mi" em "E-5", "c-5" em "C-5", "C#5" em "C#5")
        nota_limpa = nome_nota.upper().replace('-', '')
        
        # Atalhos comuns em português para facilitar sua escrita
        atalhos = {'DO': 'C5', 'RE': 'D5', 'MI': 'E5', 'FA': 'F5', 'SOL': 'G5', 'LA': 'A5', 'SI': 'B5'}
        if nota_limpa in atalhos:
            nota_limpa = atalhos[nota_limpa]

        try:
            # Separa o tom (letras) da oitava (número no final)
            if '#' in nota_limpa:
                tom = nota_limpa[:2]
                oitava = int(nota_limpa[2:])
            else:
                tom = nota_limpa[0]
                oitava = int(nota_limpa[1:])
                
            # O cálculo matemático padrão do formato Impulse Tracker:
            # Oitava * 12 + o semitom correspondente
            return (oitava * 12) + self._semitons[tom]
        except (KeyError, ValueError):
            # Se a nota for completamente inválida, retorna o C-5 (60)
            return 60

    def build_pattern(self, sequencia_notas, id_instrumento=1):
        """
        Gera um ITpattern a partir de uma lista contendo notas em string e Nones.
        """
        # Correção crucial: Agora instancia a CLASSE importada corretamente
        padrao = ITpattern()
        linha_atual = 0

        for item in sequencia_notas:
            if linha_atual >= 64:
                print(f"[Aviso] A sequência de notas ultrapassou o limite de 64 linhas do Pattern e foi cortada.")
                break

            if item is not None:
                num_nota = self.string_para_numero(item)
                
                # Acessa a célula do Canal 0 na linha atual
                nota_it = padrao.Rows[linha_atual][0]
                nota_it.Note = num_nota
                nota_it.Instrument = id_instrumento
                nota_it.Volume = 64  # Volume cheio

            # Avança o ponteiro de linhas para a próxima nota
            linha_atual += self.linhas_por_nota

        return padrao