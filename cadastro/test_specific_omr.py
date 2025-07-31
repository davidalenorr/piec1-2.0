"""
Script de teste para verificar o funcionamento do processador OMR com uma imagem específica
"""

import sys
import os
import cv2

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
import django
django.setup()

from cadastro.omr_processor import OMRProcessor


def test_omr_with_specific_image(image_path):
    """Testa o processamento OMR com uma imagem específica"""
    
    if not os.path.exists(image_path):
        print(f"Arquivo não encontrado: {image_path}")
        return
    
    print(f"Testando com: {image_path}")
    
    # Criar processador OMR
    processor = OMRProcessor()
    processor.set_debug(True)
    
    # Processar imagem
    try:
        # Testar com diferentes números de questões
        for num_q in [5, 10, 15, 20]:
            results = processor.process_omr_image(image_path, num_questions=num_q)
            print(f"Resultados para {num_q} questões: {results}")
            
        # Exibir a imagem para debug visual
        try:
            image = cv2.imread(image_path)
            image = cv2.resize(image, (600, int(600 * image.shape[0] / image.shape[1])))
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar threshold adaptativo para visualização
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Salvar as imagens processadas para análise
            debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_omr')
            os.makedirs(debug_dir, exist_ok=True)
            
            # Salvar imagens de debug
            image_name = os.path.basename(image_path)
            cv2.imwrite(os.path.join(debug_dir, f"original_{image_name}"), image)
            cv2.imwrite(os.path.join(debug_dir, f"threshold_{image_name}"), thresh)
            
            print(f"Imagens de debug salvas em: {debug_dir}")
            
        except Exception as e:
            print(f"Erro ao exibir imagem: {str(e)}")
            
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")


if __name__ == "__main__":
    print("=== Teste do Processador OMR com Imagem Específica ===")
    
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
    
    test_omr_with_specific_image(image_path)
    print("=== Fim do teste ===")
