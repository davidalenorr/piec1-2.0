#!/usr/bin/env python
"""
Script para analisar as coordenadas e verificar o alinhamento do gabarito G10
"""

import os
import sys
import cv2
import numpy as np

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cadastro.omr_processor import OMRProcessor

def analyze_coordinates():
    """Analisa as coordenadas das bolhas no gabarito G10"""
    
    # Caminho da imagem de teste
    test_image = "gabaritos para teste/G10-P.jpg"
    
    if not os.path.exists(test_image):
        print(f"Imagem de teste não encontrada: {test_image}")
        return
    
    # Carregar a imagem
    image = cv2.imread(test_image)
    image = cv2.resize(image, (800, 1100))
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 3)
    
    # Coordenadas testadas
    positions = [
        [355, [290, 341, 392, 443, 494]],  # Questão 1
        [413, [290, 341, 392, 443, 494]],  # Questão 2
        [471, [290, 341, 392, 443, 494]],  # Questão 3
        [529, [290, 341, 392, 443, 494]],  # Questão 4
        [587, [290, 341, 392, 443, 494]],  # Questão 5
        [645, [290, 341, 392, 443, 494]],  # Questão 6
        [703, [290, 341, 392, 443, 494]],  # Questão 7
        [761, [290, 341, 392, 443, 494]],  # Questão 8
        [819, [290, 341, 392, 443, 494]],  # Questão 9
        [877, [290, 341, 392, 443, 494]]   # Questão 10
    ]
    
    # Respostas corretas esperadas
    expected = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'A', 'C', 'B']
    
    # Criar imagem de debug
    debug_image = image.copy()
    radius = 22
    
    print("Análise das coordenadas:")
    print("========================")
    
    for q_idx, (y, x_positions) in enumerate(positions):
        filled_counts = []
        expected_answer = expected[q_idx]
        expected_idx = ord(expected_answer) - 65  # A=0, B=1, etc.
        
        print(f"\nQuestão {q_idx+1} (Esperado: {expected_answer}):")
        
        for alt_idx, x in enumerate(x_positions):
            # Criar máscara circular
            mask = np.zeros(thresh.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), radius, 255, -1)
            
            # Aplicar máscara
            masked = cv2.bitwise_and(thresh, thresh, mask=mask)
            filled_pixels = cv2.countNonZero(masked)
            filled_counts.append(filled_pixels)
            
            # Desenhar círculo
            color = (0, 255, 0) if alt_idx == expected_idx else (255, 0, 0)
            cv2.circle(debug_image, (x, y), radius, color, 2)
            cv2.putText(debug_image, f"{chr(65+alt_idx)}{filled_pixels}", (x - 15, y - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            print(f"  {chr(65+alt_idx)}: {filled_pixels} pixels")
        
        # Verificar qual tem mais pixels
        max_idx = filled_counts.index(max(filled_counts))
        detected = chr(65 + max_idx)
        correct = "✓" if detected == expected_answer else "✗"
        
        print(f"  Detectado: {detected}, Esperado: {expected_answer} {correct}")
        print(f"  Valores: {filled_counts}")
        
        # Destacar a resposta esperada
        expected_x = x_positions[expected_idx]
        cv2.circle(debug_image, (expected_x, y), radius + 5, (0, 0, 255), 3)
    
    # Salvar imagem de debug
    cv2.imwrite("debug_omr/coordinate_analysis.jpg", debug_image)
    print(f"\nImagem de análise salva em: debug_omr/coordinate_analysis.jpg")

if __name__ == "__main__":
    analyze_coordinates()
