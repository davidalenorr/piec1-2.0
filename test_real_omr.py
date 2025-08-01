#!/usr/bin/env python3
"""
Script para simular o processamento da imagem OMR real enviada pelo usuário
"""

import os
import sys
import django
from PIL import Image
import numpy as np
import cv2

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cadastro.settings')
django.setup()

from cadastro.omr_processor import process_uploaded_image


class MockUploadedFile:
    """Simula um arquivo enviado pelo Django"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'rb')
        self.name = os.path.basename(file_path)
    
    def read(self):
        return self.file.read()
    
    def seek(self, pos):
        return self.file.seek(pos)
    
    def close(self):
        self.file.close()


def test_real_image_processing():
    """Testa o processamento com imagem real de 20 questões"""
    
    print("=== Teste com Imagem Real de 20 Questões ===")
    
    # Usar a imagem de 20 questões como exemplo
    test_image = "gabaritos para teste/gabarito de 20.jpg"
    
    if not os.path.exists(test_image):
        print(f"Arquivo não encontrado: {test_image}")
        return
    
    # Respostas esperadas conforme a imagem real mostrada pelo usuário
    # (baseado na análise visual da imagem do gabarito)
    expected_answers = [
        'C', 'C', 'A', 'E', 'D', 'A', 'A', 'B', 'D', 'E',  # Questões 1-10
        'D', 'C', 'E', 'B', 'A', 'C', 'D', 'C', 'A', 'E'   # Questões 11-20
    ]
    
    try:
        # Simular arquivo enviado
        mock_file = MockUploadedFile(test_image)
        
        # Processar com 20 questões
        num_questions = 20
        detected_answers = process_uploaded_image(mock_file, num_questions)
        
        mock_file.close()
        
        print(f"Respostas detectadas: {detected_answers}")
        print(f"Respostas esperadas: {expected_answers}")
        
        # Comparar resultados
        correct_count = 0
        for i, (detected, expected) in enumerate(zip(detected_answers, expected_answers)):
            if detected == expected:
                correct_count += 1
                status = "✓"
            else:
                status = "✗"
            print(f"Q{i+1}: Detectado={detected or 'N/A'}, Esperado={expected} {status}")
        
        accuracy = (correct_count / len(expected_answers)) * 100 if expected_answers else 0
        print(f"\nPrecisão: {correct_count}/{len(expected_answers)} ({accuracy:.1f}%)")
        
        # Calcular nota como no sistema
        total_questions = len(expected_answers)
        final_grade = round((correct_count / total_questions) * 10, 1) if total_questions > 0 else 0
        print(f"Nota calculada: {final_grade}/10")
        
        # Mostrar melhorias
        empty_count = detected_answers.count('')
        print(f"Questões não detectadas: {empty_count}/{total_questions}")
        
        if empty_count == 0:
            print("✅ SUCESSO: Todas as questões foram detectadas!")
        elif empty_count <= 2:
            print("⚠️  QUASE PERFEITO: Apenas algumas questões não foram detectadas")
        else:
            print("❌ PRECISA MELHORIA: Muitas questões não foram detectadas")
        
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")


if __name__ == "__main__":
    test_real_image_processing()
