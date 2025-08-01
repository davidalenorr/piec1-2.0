#!/usr/bin/env python3
"""
Script de teste final com análise visual da imagem real
"""

import os
import sys
import django
import cv2
import numpy as np

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
django.setup()


def analyze_real_image():
    """Analisa a imagem real para verificar as marcações"""
    
    image_path = "gabaritos para teste/gabarito de 20.jpg"
    
    if not os.path.exists(image_path):
        print("Imagem não encontrada")
        return
    
    # Carregar imagem
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Redimensionar para análise
    height, width = gray.shape
    scale = 1000 / width
    new_width = 1000
    new_height = int(height * scale)
    
    resized = cv2.resize(gray, (new_width, new_height))
    
    # Aplicar threshold
    _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar círculos
    circles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 200 < area < 2000:  # Tamanho de círculo de resposta
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity > 0.4:  # Razoavelmente circular
                    x, y, w, h = cv2.boundingRect(contour)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    circles.append((center_x, center_y, area))
    
    print(f"Círculos encontrados: {len(circles)}")
    
    # Separar em duas colunas
    circles.sort(key=lambda c: c[0])  # Ordenar por X
    mid_x = new_width // 2
    
    left_circles = [c for c in circles if c[0] < mid_x]
    right_circles = [c for c in circles if c[0] >= mid_x]
    
    print(f"Coluna esquerda: {len(left_circles)} círculos")
    print(f"Coluna direita: {len(right_circles)} círculos")
    
    # Organizar por linhas
    def organize_by_rows(column_circles):
        # Agrupar por Y (linhas)
        rows = {}
        for x, y, area in column_circles:
            row_key = y // 40 * 40  # Agrupar em intervalos de 40 pixels
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append((x, y, area))
        
        # Ordenar cada linha por X e manter apenas linhas com 5 círculos
        organized_rows = []
        for row_y in sorted(rows.keys()):
            row_circles = sorted(rows[row_y], key=lambda c: c[0])
            if len(row_circles) >= 5:
                organized_rows.append(row_circles[:5])  # Pegar apenas os 5 primeiros
        
        return organized_rows[:10]  # No máximo 10 questões por coluna
    
    left_rows = organize_by_rows(left_circles)
    right_rows = organize_by_rows(right_circles)
    
    print(f"Linhas organizadas - Esquerda: {len(left_rows)}, Direita: {len(right_rows)}")
    
    # Analisar marcações
    def analyze_column(rows, column_name, start_question=1):
        results = []
        
        for row_idx, row_circles in enumerate(rows):
            question_num = start_question + row_idx
            max_filled = 0
            max_idx = -1
            
            print(f"\n{column_name} - Questão {question_num}:")
            
            for alt_idx, (x, y, area) in enumerate(row_circles):
                # Criar máscara circular
                mask = np.zeros(thresh.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), 20, 255, -1)
                
                # Contar pixels preenchidos
                masked = cv2.bitwise_and(thresh, thresh, mask=mask)
                filled_pixels = cv2.countNonZero(masked)
                
                print(f"  {chr(65+alt_idx)}: {filled_pixels} pixels")
                
                if filled_pixels > max_filled:
                    max_filled = filled_pixels
                    max_idx = alt_idx
            
            if max_idx >= 0 and max_filled > 100:
                answer = chr(65 + max_idx)
                results.append(answer)
                print(f"  Resposta: {answer} (preenchimento: {max_filled})")
            else:
                results.append('')
                print(f"  Resposta: N/A (preenchimento: {max_filled})")
        
        return results
    
    # Analisar ambas as colunas
    left_results = analyze_column(left_rows, "Coluna Esquerda", 1)
    right_results = analyze_column(right_rows, "Coluna Direita", 11)
    
    # Combinar resultados
    all_results = left_results + right_results
    
    # Garantir 20 respostas
    while len(all_results) < 20:
        all_results.append('')
    
    all_results = all_results[:20]
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Respostas detectadas: {all_results}")
    
    # Comparar com respostas esperadas
    expected = ['C', 'C', 'A', 'E', 'D', 'A', 'A', 'B', 'D', 'E', 'D', 'C', 'E', 'B', 'A', 'C', 'D', 'C', 'A', 'E']
    
    correct = 0
    for i, (detected, expected_ans) in enumerate(zip(all_results, expected)):
        status = "✓" if detected == expected_ans else "✗"
        if detected == expected_ans:
            correct += 1
        print(f"Q{i+1}: {detected or 'N/A'} vs {expected_ans} {status}")
    
    accuracy = (correct / 20) * 100
    print(f"\nPrecisão: {correct}/20 ({accuracy:.1f}%)")
    
    # Salvar imagem com marcações
    debug_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    # Marcar círculos detectados
    for x, y, area in circles:
        cv2.circle(debug_image, (x, y), 20, (0, 255, 0), 2)
    
    cv2.imwrite("debug_omr/analysis_circles.jpg", debug_image)
    print("\nImagem de debug salva em: debug_omr/analysis_circles.jpg")


if __name__ == "__main__":
    analyze_real_image()
