"""
Script para processar a imagem G5-P.jpg usando abordagem de grade fixa
Pode ser mais eficaz para folhas OMR com formato padronizado
"""

import os
import cv2
import numpy as np
import sys
import json

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def process_grid_approach(image_path):
    """
    Processa uma imagem OMR usando abordagem de grade fixa
    Esta abordagem funciona melhor quando o gabarito tem posições fixas
    """
    # Carregar e preprocessar a imagem
    image = cv2.imread(image_path)
    if image is None:
        print(f"Não foi possível carregar a imagem: {image_path}")
        return []
    
    # Redimensionar para tamanho padrão
    image = cv2.resize(image, (800, 1100))
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Melhorar contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Aplicar filtro Gaussiano para reduzir ruído
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # Aplicar threshold adaptativo
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 13, 3
    )
    
    # Definir regiões de interesse para cada questão (ajustar conforme a imagem)
    # Formato: [y_start, y_end, [x_positions para A, B, C, D, E]]
    # Estas coordenadas precisam ser ajustadas para corresponder ao layout do gabarito
    roi_regions = [
        # Questão 1
        [450, 500, [430, 480, 530, 580, 630]],
        # Questão 2
        [510, 560, [430, 480, 530, 580, 630]],
        # Questão 3
        [570, 620, [430, 480, 530, 580, 630]],
        # Questão 4
        [630, 680, [430, 480, 530, 580, 630]],
        # Questão 5
        [690, 740, [430, 480, 530, 580, 630]],
    ]
    
    # Criar diretório de debug
    debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_omr')
    os.makedirs(debug_dir, exist_ok=True)
    
    # Salvar imagem threshold
    cv2.imwrite(os.path.join(debug_dir, "threshold_grid.jpg"), thresh)
    
    # Verificar cada região e detectar marcação
    detected_answers = []
    circle_radius = 20  # Ajustar conforme o tamanho das bolhas
    
    # Criar uma cópia da imagem para visualização
    debug_image = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2BGR)
    
    for q_idx, (y_start, y_end, x_positions) in enumerate(roi_regions):
        max_filled = 0
        answer_idx = -1
        
        for alt_idx, x_center in enumerate(x_positions):
            # Criar uma máscara circular
            y_center = (y_start + y_end) // 2
            mask = np.zeros(thresh.shape, dtype=np.uint8)
            cv2.circle(mask, (x_center, y_center), circle_radius, 255, -1)
            
            # Aplicar máscara e contar pixels preenchidos
            masked = cv2.bitwise_and(thresh, thresh, mask=mask)
            filled_pixels = cv2.countNonZero(masked)
            
            # Desenhar círculo na imagem de debug
            color = (0, 0, 255) if filled_pixels > max_filled else (0, 255, 0)
            cv2.circle(debug_image, (x_center, y_center), circle_radius, color, 2)
            cv2.putText(debug_image, f"{filled_pixels}", (x_center - 10, y_center - 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            print(f"Q{q_idx+1}, Alt {chr(65+alt_idx)}: {filled_pixels} pixels")
            
            # Atualizar se for a alternativa mais preenchida
            if filled_pixels > max_filled:
                max_filled = filled_pixels
                answer_idx = alt_idx
        
        # Adicionar resposta detectada
        if answer_idx != -1 and max_filled > 30:  # Ajustar este limite conforme necessário
            detected_answers.append(chr(65 + answer_idx))
        else:
            detected_answers.append('')
    
    # Salvar imagem de debug
    cv2.imwrite(os.path.join(debug_dir, "debug_grid.jpg"), debug_image)
    
    return detected_answers


if __name__ == "__main__":
    print("=== Teste com Abordagem de Grade Fixa ===")
    
    # Verificar se foi passado caminho da imagem como argumento
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Usar um dos arquivos de teste disponíveis
        gabaritos_path = os.path.join(os.path.dirname(__file__), '..', 'gabaritos para teste')
        if os.path.exists(gabaritos_path):
            image_path = os.path.join(gabaritos_path, 'G5-P.jpg')  # Usar gabarito de 5 questões como padrão
        else:
            print("Caminho para imagem não fornecido e pasta de gabaritos não encontrada")
            sys.exit(1)
    
    print(f"Processando imagem: {image_path}")
    answers = process_grid_approach(image_path)
    print(f"Respostas detectadas: {answers}")
    print("=== Fim do teste ===")
