#!/usr/bin/env python
"""
Script para testar e corrigir o problema na questão 10 do gabarito G10-P
"""

import os
import sys
import cv2
import numpy as np

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cadastro.omr_processor import OMRProcessor

def test_g10_specific():
    """Testa o processamento específico do gabarito G10"""
    
    # Caminho da imagem de teste
    test_image = "gabaritos para teste/WhatsApp Image 2025-07-30 at 23.28.36_1d3a08f2.jpg"
    
    if not os.path.exists(test_image):
        print(f"Imagem de teste não encontrada: {test_image}")
        return
    
    # Copiar a imagem com o nome padrão G10 para teste
    import shutil
    g10_test_image = "gabaritos para teste/G10-P.jpg"
    shutil.copy2(test_image, g10_test_image)
    
    # Criar processor com debug ativado
    processor = OMRProcessor()
    processor.set_debug(True)
    
    print("Processando gabarito G10...")
    results = processor.process_omr_image(g10_test_image, num_questions=10)
    
    print("\nResultados detectados:")
    for i, answer in enumerate(results, 1):
        print(f"Questão {i}: {answer if answer else 'Não detectado'}")
    
    # Respostas esperadas baseadas na imagem
    expected = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'A', 'C', 'B']
    
    print("\nComparação com respostas esperadas:")
    for i, (detected, expected_ans) in enumerate(zip(results, expected), 1):
        status = "✓" if detected == expected_ans else "✗"
        print(f"Questão {i}: Detectado={detected}, Esperado={expected_ans} {status}")
    
    # Verificar problema específico da questão 10
    if len(results) >= 10:
        q10_result = results[9]  # índice 9 = questão 10
        q10_expected = expected[9]  # B
        
        print(f"\nProblema específico da questão 10:")
        print(f"Detectado: {q10_result}")
        print(f"Esperado: {q10_expected}")
        
        if q10_result != q10_expected:
            print("❌ PROBLEMA CONFIRMADO: Questão 10 está sendo detectada incorretamente!")
            return False
        else:
            print("✅ Questão 10 está sendo detectada corretamente!")
            return True
    
    # Limpar arquivo de teste
    if os.path.exists(g10_test_image):
        os.remove(g10_test_image)
    
    return False

if __name__ == "__main__":
    test_g10_specific()
