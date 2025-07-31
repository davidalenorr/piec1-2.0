"""
Script de teste para verificar o funcionamento do processador OMR
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
import django
django.setup()

from cadastro.omr_processor import OMRProcessor


def test_omr_with_sample_image():
    """Testa o processamento OMR com uma das imagens de exemplo"""
    
    # Caminho para as imagens de teste
    gabaritos_path = os.path.join(os.path.dirname(__file__), '..', 'gabaritos para teste')
    
    # Listar imagens disponíveis
    if os.path.exists(gabaritos_path):
        images = [f for f in os.listdir(gabaritos_path) if f.endswith('.jpg')]
        print(f"Imagens disponíveis: {images}")
        
        if images:
            # Testar com a primeira imagem
            test_image = os.path.join(gabaritos_path, images[0])
            print(f"Testando com: {test_image}")
            
            # Criar processador OMR
            processor = OMRProcessor()
            processor.set_debug(True)
            
            # Processar imagem
            try:
                results = processor.process_omr_image(test_image, num_questions=5)
                print(f"Resultados detectados: {results}")
                
                # Testar com diferentes números de questões
                for num_q in [10, 15, 20]:
                    results = processor.process_omr_image(test_image, num_questions=num_q)
                    print(f"Resultados para {num_q} questões: {results}")
                    
            except Exception as e:
                print(f"Erro no processamento: {str(e)}")
        else:
            print("Nenhuma imagem encontrada na pasta de gabaritos")
    else:
        print(f"Pasta de gabaritos não encontrada: {gabaritos_path}")


if __name__ == "__main__":
    print("=== Teste do Processador OMR ===")
    test_omr_with_sample_image()
    print("=== Fim do teste ===")
