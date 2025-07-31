"""
Script para demonstrar o processamento OMR com a imagem G5-P.jpg específica
"""

import os
import sys
import cv2
import numpy as np

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
import django
django.setup()


def process_specific_omr(image_path, debug=True):
    """
    Processa especificamente a imagem G5-P.jpg para reconhecimento preciso
    
    Esta função é otimizada para o layout específico do exemplo fornecido
    """
    if not os.path.exists(image_path):
        print(f"Arquivo não encontrado: {image_path}")
        return []
    
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
    
    # Definir posições precisas para o gabarito G5-P.jpg
    # [y, [x_A, x_B, x_C, x_D, x_E]]
    # Estas posições são baseadas na imagem G5-P.jpg específica
    positions = [
        [482, [452, 503, 554, 605, 656]],  # Questão 1
        [540, [452, 503, 554, 605, 656]],  # Questão 2
        [598, [452, 503, 554, 605, 656]],  # Questão 3
        [656, [452, 503, 554, 605, 656]],  # Questão 4
        [714, [452, 503, 554, 605, 656]]   # Questão 5
    ]
    
    # Criar diretório para salvar imagens de debug
    debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_omr')
    os.makedirs(debug_dir, exist_ok=True)
    
    # Salvar imagem threshold para debug
    if debug:
        cv2.imwrite(os.path.join(debug_dir, "thresh_specific.jpg"), thresh)
        debug_image = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2BGR)
    
    # Detectar marcações
    results = []
    radius = 25  # Raio da área circular para verificar
    
    for q_idx, (y, x_positions) in enumerate(positions):
        max_filled = 0
        max_idx = -1
        
        for alt_idx, x in enumerate(x_positions):
            # Criar máscara circular
            mask = np.zeros(thresh.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), radius, 255, -1)
            
            # Aplicar máscara
            masked = cv2.bitwise_and(thresh, thresh, mask=mask)
            filled_pixels = cv2.countNonZero(masked)
            
            # Debug info
            if debug:
                print(f"Q{q_idx+1}, Alt {chr(65+alt_idx)}: {filled_pixels} pixels")
                
                # Desenhar círculo na imagem de debug
                color = (0, 0, 255) if filled_pixels > max_filled else (0, 255, 0)
                cv2.circle(debug_image, (x, y), radius, color, 2)
                cv2.putText(debug_image, f"{filled_pixels}", (x - 15, y - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Atualizar se for o maior preenchimento
            if filled_pixels > max_filled:
                max_filled = filled_pixels
                max_idx = alt_idx
        
        # Adicionar resultado
        if max_idx >= 0 and max_filled > 30:
            results.append(chr(65 + max_idx))
        else:
            results.append('')
    
    # Salvar imagem de debug
    if debug:
        cv2.imwrite(os.path.join(debug_dir, "debug_specific.jpg"), debug_image)
    
    return results


if __name__ == "__main__":
    print("=== Teste de Processamento OMR Específico ===")
    
    # Verificar se foi passado caminho da imagem como argumento
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Usar a imagem G5-P.jpg como padrão
        image_path = os.path.join(os.path.dirname(__file__), '..', 'gabaritos para teste', 'G5-P.jpg')
    
    print(f"Processando imagem: {image_path}")
    answers = process_specific_omr(image_path)
    print(f"Respostas detectadas: {answers}")
    print("=== Fim do teste ===")
