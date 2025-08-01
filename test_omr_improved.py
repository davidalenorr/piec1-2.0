#!/usr/bin/env python3
"""
Script para testar as melhorias no processamento OMR
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
django.setup()

from cadastro.omr_processor import OMRProcessor


def test_omr_processor():
    """Testa o processador OMR com debug ativado"""
    
    # Inicializar processador com debug
    processor = OMRProcessor()
    processor.set_debug(True)
    
    print("=== Teste do Processador OMR Melhorado ===")
    
    # Testar com gabarito de exemplo (se existir)
    test_images = [
        "gabaritos para teste/gabarito de 20.jpg",
        "gabaritos para teste/gabarito de 15.jpg",
        "gabaritos para teste/gabarito de 10.jpg",
        "gabaritos para teste/gabarito de 5.jpg",
    ]
    
    num_questions_map = {
        "gabarito de 20.jpg": 20,
        "gabarito de 15.jpg": 15, 
        "gabarito de 10.jpg": 10,
        "gabarito de 5.jpg": 5,
    }
    
    for image_path in test_images:
        if os.path.exists(image_path):
            filename = os.path.basename(image_path)
            num_questions = num_questions_map.get(filename, 5)
            
            print(f"\n--- Testando: {filename} ({num_questions} questões) ---")
            
            try:
                results = processor.process_omr_image(image_path, num_questions)
                
                print(f"Resultados detectados: {results}")
                print(f"Questões preenchidas: {len([r for r in results if r])}")
                print(f"Questões vazias: {len([r for r in results if not r])}")
                
                # Mostrar resultado formatado
                formatted_results = []
                for i, answer in enumerate(results):
                    if answer:
                        formatted_results.append(f"{i+1}: {answer}")
                    else:
                        formatted_results.append(f"{i+1}: N/A")
                
                print("Respostas formatadas:")
                print(", ".join(formatted_results))
                
            except Exception as e:
                print(f"Erro ao processar {filename}: {str(e)}")
        else:
            print(f"Arquivo não encontrado: {image_path}")
    
    print("\n=== Teste Concluído ===")
    print("Verifique a pasta 'debug_omr' para imagens de debug.")


if __name__ == "__main__":
    test_omr_processor()
