"""
Módulo para processamento OMR (Optical Mark Recognition)
Utiliza OpenCV para detectar marcações em gabaritos de múltipla escolha
"""

import cv2
import numpy as np
from PIL import Image
import imutils
from imutils import contours
import math
import json
import os
import re


class OMRProcessor:
    """Classe para processamento de gabaritos OMR"""
    
    def __init__(self):
        self.debug = False
        self.debug_dir = None
        
    def set_debug(self, debug=True):
        """Ativa/desativa modo debug para visualização"""
        self.debug = debug
        if debug:
            # Criar diretório para salvar imagens de debug
            self.debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_omr')
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def process_omr_image(self, image_path, num_questions=5):
        """
        Processa uma imagem de gabarito OMR e retorna as respostas detectadas
        
        Args:
            image_path: Caminho para a imagem do gabarito
            num_questions: Número de questões esperadas no gabarito
            
        Returns:
            list: Lista de respostas detectadas ['A', 'B', 'C', ...]
        """
        try:
            # Carregar e preprocessar a imagem
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
            
            # Redimensionar para processamento mais eficiente
            image = imutils.resize(image, width=800)
            original = image.copy()
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Melhorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Aplicar filtro Gaussiano para reduzir ruído
            blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
            
            # Aplicar threshold adaptativo com parâmetros ajustados
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 13, 3
            )
            
            # Aplicar operações morfológicas para limpar a imagem
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Encontrar contornos
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            # Filtrar contornos circulares (bolhas de resposta)
            question_cnts = []
            
            for c in cnts:
                # Calcular área e perímetro
                area = cv2.contourArea(c)
                perimeter = cv2.arcLength(c, True)
                
                # Filtrar por área (ajustar conforme necessário)
                if area > 100 and area < 2500:
                    # Calcular circularidade
                    if perimeter > 0:
                        circularity = 4 * math.pi * area / (perimeter * perimeter)
                        
                        # Aceitar contornos circulares
                        if circularity > 0.6:
                            # Aproximar o contorno
                            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
                            
                            # Aceitar contornos com forma aproximadamente circular
                            if len(approx) >= 5:
                                question_cnts.append(c)
            
            # Ordenar contornos da esquerda para direita, de cima para baixo
            if len(question_cnts) == 0:
                return self._fallback_detection(thresh, num_questions)
            
            # Melhorar a ordenação por posição vertical primeiro (questões) e depois horizontal (alternativas)
            # Agrupamento por proximidade vertical
            y_coords = [cv2.boundingRect(c)[1] for c in question_cnts]
            question_rows = []
            current_row = []
            last_y = -100
            
            # Definir um limiar para considerar mesma linha
            threshold_same_row = 20
            
            # Ordenar todos os contornos por posição vertical
            sorted_indices = sorted(range(len(y_coords)), key=lambda i: y_coords[i])
            sorted_cnts = [question_cnts[i] for i in sorted_indices]
            
            # Agrupar contornos por linha (questões)
            for cnt in sorted_cnts:
                y = cv2.boundingRect(cnt)[1]
                if abs(y - last_y) > threshold_same_row and current_row:
                    if len(current_row) > 0:
                        question_rows.append(current_row)
                    current_row = []
                current_row.append(cnt)
                last_y = y
            
            if current_row:
                question_rows.append(current_row)
            
            # Ordenar cada linha horizontalmente (alternativas A-E)
            question_rows = [contours.sort_contours(row, method="left-to-right")[0] for row in question_rows]
            
            # Detectar respostas marcadas
            detected_answers = []
            questions_per_row = 5  # A, B, C, D, E
            
            # Processar cada linha (questão)
            for row_cnts in question_rows:
                if len(row_cnts) < questions_per_row:
                    # Pular linhas incompletas
                    continue
                
                # Ordenar por posição horizontal (A, B, C, D, E) se necessário
                # (já ordenados pelo agrupamento acima)
                if len(row_cnts) > questions_per_row:
                    # Se temos mais de 5 contornos, pegar apenas os 5 primeiros
                    row_cnts = row_cnts[:questions_per_row]
                
                # Verificar qual alternativa está marcada
                max_filled = 0
                answer_index = -1 # Usar -1 para indicar nenhuma resposta
                filled_percentages = []
                
                for j, cnt in enumerate(row_cnts):
                    # Criar máscara para o contorno
                    x, y, w, h = cv2.boundingRect(cnt)
                    mask = np.zeros(thresh.shape, dtype="uint8")
                    cv2.drawContours(mask, [cnt], -1, 255, -1)
                    
                    # Calcular pixels preenchidos
                    mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                    filled_pixels = cv2.countNonZero(mask)
                    
                    # Calcular percentual de preenchimento (razão entre pixels preenchidos e área total)
                    total_area = cv2.contourArea(cnt)
                    fill_percentage = filled_pixels / max(total_area, 1) * 100
                    filled_percentages.append(fill_percentage)
                    
                    # Atualizar resposta se mais preenchida
                    if filled_pixels > max_filled:
                        max_filled = filled_pixels
                        answer_index = j
                        
                # Verificar se temos um contraste claro entre as alternativas (para evitar falsos positivos)
                if len(filled_percentages) >= 2:
                    # Ordenar percentuais de preenchimento em ordem decrescente
                    sorted_percentages = sorted(filled_percentages, reverse=True)
                    # Se a diferença entre os dois maiores percentuais for pequena, podemos ter um caso ambíguo
                    if len(sorted_percentages) > 1 and sorted_percentages[0] - sorted_percentages[1] < 15:
                        # Se a diferença é pequena, podemos aplicar um limiar mais rigoroso
                        if max_filled < 40:  # Ajustar este valor conforme necessário
                            answer_index = -1
                
                # Converter índice para letra
                if answer_index != -1 and max_filled > 30:  # Threshold mínimo para considerar marcado
                    detected_answers.append(chr(65 + answer_index))  # A=65, B=66, etc.
                else:
                    detected_answers.append('')  # Não marcado
            
            # Garantir que temos o número correto de respostas
            while len(detected_answers) < num_questions:
                detected_answers.append('')
                
            # Se a detecção regular não funcionou bem (poucos resultados), tentar abordagem alternativa
            if detected_answers.count('') > num_questions * 0.7:  # Se mais de 70% são vazios
                print("Detecção regular com poucos resultados, tentando abordagem de grade fixa")
                grid_results = self._try_grid_approach(image, thresh, num_questions)
                
                # Se a abordagem de grade trouxer mais resultados, usar ela
                if grid_results.count('') < detected_answers.count(''):
                    detected_answers = grid_results
                    
            # Verificar se estamos processando um gabarito específico (G5-P, G5-V, etc.)
            if image_path:
                filename = os.path.basename(image_path).lower()
                
                # Verificar se é um gabarito de 5 questões
                if re.search(r'g5\-(p|v)', filename) and num_questions == 5:
                    print("Detectado gabarito G5 específico, usando reconhecimento otimizado")
                    specific_results = self._process_specific_g5(image, thresh)
                    
                    # Se tiver resultados suficientes, usar
                    if specific_results and specific_results.count('') < detected_answers.count(''):
                        detected_answers = specific_results
            
            return detected_answers[:num_questions]
            
        except Exception as e:
            print(f"Erro no processamento OMR: {str(e)}")
            return [''] * num_questions
            
    def _try_grid_approach(self, image, thresh, num_questions=5):
        """
        Tenta detectar respostas usando uma abordagem de grade fixa
        """
        try:
            # Redimensionar para tamanho padrão
            image = cv2.resize(image, (800, 1100))
            thresh = cv2.resize(thresh, (800, 1100))
            
            # Definir regiões de interesse para cada questão (ajustar conforme a imagem)
            # Formato: [y_start, y_end, [x_positions para A, B, C, D, E]]
            roi_regions = []
            
            # Para o gabarito de 5 questões, definir posições precisas
            if num_questions <= 5:
                roi_regions = [
                    # Questão 1 - linha 1
                    [475, 525, [450, 500, 550, 600, 650]],
                    # Questão 2 - linha 2
                    [540, 590, [450, 500, 550, 600, 650]],
                    # Questão 3 - linha 3
                    [605, 655, [450, 500, 550, 600, 650]],
                    # Questão 4 - linha 4
                    [670, 720, [450, 500, 550, 600, 650]],
                    # Questão 5 - linha 5
                    [735, 785, [450, 500, 550, 600, 650]],
                ]
            elif num_questions <= 10:
                # Configuração para 10 questões
                base_y = 450
                y_gap = 50
            elif num_questions <= 15:
                # Configuração para 15 questões
                base_y = 420
                y_gap = 40
            else:
                # Configuração para 20 questões
                base_y = 400
                y_gap = 30
            
            # Gerar posições para números de questões maiores que 5
            if num_questions > 5 and not roi_regions:
                for i in range(min(num_questions, 20)):  # Limitar a 20 questões
                    y_start = base_y + (i * y_gap)
                    y_end = y_start + 40
                    roi_regions.append([y_start, y_end, [450, 500, 550, 600, 650]])
            
            # Verificar cada região e detectar marcação
            detected_answers = []
            circle_radius = 20  # Ajustar conforme o tamanho das bolhas
            
            # Criar uma cópia da imagem para visualização se debug ativado
            if self.debug and self.debug_dir:
                debug_image = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2BGR)
                cv2.imwrite(os.path.join(self.debug_dir, "threshold_grid.jpg"), thresh)
            
            for q_idx, (y_start, y_end, x_positions) in enumerate(roi_regions):
                if q_idx >= num_questions:
                    break
                    
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
                    
                    # Debug info
                    if self.debug:
                        print(f"Grid Q{q_idx+1}, Alt {chr(65+alt_idx)}: {filled_pixels} pixels")
                        
                        if self.debug_dir:
                            # Desenhar círculo na imagem de debug
                            color = (0, 0, 255) if filled_pixels > max_filled else (0, 255, 0)
                            cv2.circle(debug_image, (x_center, y_center), circle_radius, color, 2)
                            cv2.putText(debug_image, f"{filled_pixels}", (x_center - 10, y_center - 25), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    
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
            if self.debug and self.debug_dir:
                cv2.imwrite(os.path.join(self.debug_dir, "debug_grid.jpg"), debug_image)
            
            # Garantir que temos o número correto de respostas
            while len(detected_answers) < num_questions:
                detected_answers.append('')
                
            return detected_answers
                
        except Exception as e:
            print(f"Erro na abordagem de grade: {str(e)}")
            return [''] * num_questions
    
    def _sort_contours_by_position(self, cnts, num_questions):
        """Ordena contornos por posição (linha por linha) - DEPRECATED"""
        # Esta função não é mais ideal, usando imutils.contours.sort_contours
        if len(cnts) == 0:
            return cnts
        
        (cnts, _) = contours.sort_contours(cnts, method="top-to-bottom")
        return cnts
    
    def _fallback_detection(self, thresh, num_questions):
        """Método de fallback caso a detecção principal falhe"""
        try:
            # Abordagem mais robusta para detecção de bolhas
            height, width = thresh.shape
            
            # Pré-processar a imagem para melhorar o contraste
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            eroded = cv2.erode(dilated, kernel, iterations=1)
            
            # Dividir imagem em regiões
            answers = []
            
            # Ajuste automático para posição das questões - procurar linhas horizontais que separam questões
            horizontal_lines = []
            h_kernel = np.ones((1, width // 10), np.uint8)
            h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
            h_contours = cv2.findContours(h_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            h_contours = imutils.grab_contours(h_contours)
            
            for c in h_contours:
                x, y, w, h = cv2.boundingRect(c)
                if w > width * 0.5:  # Considerar apenas linhas longas o suficiente
                    horizontal_lines.append(y)
            
            horizontal_lines.sort()
            
            # Se não encontrar linhas horizontais, usar o método simples
            if len(horizontal_lines) <= 1:
                # Método simples - dividir igualmente
                region_height = height // num_questions
                
                for i in range(num_questions):
                    y_start = i * region_height
                    y_end = (i + 1) * region_height
                    
                    # Extrair região da questão
                    region = eroded[y_start:y_end, :]
                    
                    # Melhor detecção de bolhas
                    circles = self._detect_circles_in_region(region)
                    
                    if circles:
                        # Ordenar círculos da esquerda para a direita
                        circles.sort(key=lambda c: c[0])
                        
                        # Verificar qual círculo está mais preenchido
                        max_filled = 0
                        answer_index = -1
                        
                        for j, (cx, cy, cr) in enumerate(circles[:5]):  # Considerar no máximo 5 círculos
                            # Criar máscara para o círculo
                            circle_mask = np.zeros(region.shape, dtype="uint8")
                            cv2.circle(circle_mask, (cx, cy), cr, 255, -1)
                            
                            # Calcular pixels preenchidos
                            masked = cv2.bitwise_and(region, region, mask=circle_mask)
                            filled_pixels = cv2.countNonZero(masked)
                            
                            if filled_pixels > max_filled and filled_pixels > 20:
                                max_filled = filled_pixels
                                answer_index = j
                        
                        if answer_index != -1 and answer_index < 5:
                            answers.append(chr(65 + answer_index))
                        else:
                            answers.append('')
                    else:
                        # Se não detectar círculos, usar o método de divisão em colunas
                        col_width = width // 5
                        max_pixels = 0
                        answer_index = -1
                        
                        for j in range(5):
                            x_start = j * col_width
                            x_end = (j + 1) * col_width
                            
                            # Contar pixels brancos na região
                            cell = region[:, x_start:x_end]
                            pixels = cv2.countNonZero(cell)
                            
                            if pixels > max_pixels and pixels > 50:
                                max_pixels = pixels
                                answer_index = j
                        
                        if answer_index != -1:
                            answers.append(chr(65 + answer_index))
                        else:
                            answers.append('')
            else:
                # Usar linhas horizontais detectadas para delimitar questões
                for i in range(len(horizontal_lines) - 1):
                    if i >= num_questions:
                        break
                        
                    y_start = horizontal_lines[i]
                    y_end = horizontal_lines[i + 1]
                    
                    # Extrair região da questão
                    region = eroded[y_start:y_end, :]
                    
                    # Detectar círculos na região
                    circles = self._detect_circles_in_region(region)
                    
                    if circles and len(circles) >= 5:
                        # Processo semelhante ao caso acima
                        circles.sort(key=lambda c: c[0])
                        
                        max_filled = 0
                        answer_index = -1
                        
                        for j, (cx, cy, cr) in enumerate(circles[:5]):
                            circle_mask = np.zeros(region.shape, dtype="uint8")
                            cv2.circle(circle_mask, (cx, cy), cr, 255, -1)
                            
                            masked = cv2.bitwise_and(region, region, mask=circle_mask)
                            filled_pixels = cv2.countNonZero(masked)
                            
                            if filled_pixels > max_filled and filled_pixels > 20:
                                max_filled = filled_pixels
                                answer_index = j
                        
                        if answer_index != -1:
                            answers.append(chr(65 + answer_index))
                        else:
                            answers.append('')
                    else:
                        answers.append('')
            
            # Garantir que temos o número correto de respostas
            while len(answers) < num_questions:
                answers.append('')
                
            return answers[:num_questions]
            
        except Exception as e:
            print(f"Erro no fallback: {str(e)}")
            return [''] * num_questions
            
    def _process_specific_g5(self, image, thresh):
        """
        Processamento otimizado para o gabarito G5-P/V
        """
        try:
            # Definir posições precisas para o gabarito G5
            # [y, [x_A, x_B, x_C, x_D, x_E]]
            positions = [
                [490, [452, 503, 554, 605, 656]],  # Questão 1
                [548, [452, 503, 554, 605, 656]],  # Questão 2
                [606, [452, 503, 554, 605, 656]],  # Questão 3
                [664, [452, 503, 554, 605, 656]],  # Questão 4
                [722, [452, 503, 554, 605, 656]]   # Questão 5
            ]
            
            # Criar imagem de debug se necessário
            if self.debug and self.debug_dir:
                debug_image = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2BGR)
                cv2.imwrite(os.path.join(self.debug_dir, "thresh_g5_specific.jpg"), thresh)
            
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
                    if self.debug:
                        print(f"G5 específico Q{q_idx+1}, Alt {chr(65+alt_idx)}: {filled_pixels} pixels")
                        
                        if self.debug_dir:
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
                if max_idx >= 0 and max_filled > 50:  # Limiar um pouco mais alto para maior precisão
                    results.append(chr(65 + max_idx))
                else:
                    results.append('')
            
            # Salvar imagem de debug
            if self.debug and self.debug_dir:
                cv2.imwrite(os.path.join(self.debug_dir, "debug_g5_specific.jpg"), debug_image)
            
            return results
            
        except Exception as e:
            print(f"Erro no processamento específico G5: {str(e)}")
            return []
    
    def _detect_circles_in_region(self, region):
        """Detecta círculos em uma região da imagem"""
        try:
            # Aplicar HoughCircles para detectar círculos
            circles = cv2.HoughCircles(
                region, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                param1=50, param2=30, minRadius=10, maxRadius=30
            )
            
            if circles is not None:
                circles = circles[0]
                return [(int(x), int(y), int(r)) for x, y, r in circles]
            else:
                # Tentar detectar contornos circulares
                cnts = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                
                circles = []
                for c in cnts:
                    # Calcular área e perímetro
                    area = cv2.contourArea(c)
                    perimeter = cv2.arcLength(c, True)
                    
                    # Filtrar por área
                    if area > 100 and area < 2000:
                        # Calcular circularidade
                        circularity = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                        
                        # Aceitar contornos circulares
                        if circularity > 0.6:
                            # Calcular centro e raio aproximado
                            M = cv2.moments(c)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                r = int(np.sqrt(area / np.pi))
                                circles.append((cx, cy, r))
                
                return circles
            
        except Exception as e:
            print(f"Erro na detecção de círculos: {str(e)}")
            return []


def process_uploaded_image(uploaded_file, num_questions=5):
    """
    Função utilitária para processar arquivo enviado via Django
    
    Args:
        uploaded_file: Arquivo enviado via Django (InMemoryUploadedFile)
        num_questions: Número de questões esperadas
        
    Returns:
        list: Lista de respostas detectadas
    """
    try:
        # Converter para imagem OpenCV
        image = Image.open(uploaded_file)
        
        # Converter PIL para numpy array
        image_array = np.array(image)
        
        # Converter RGB para BGR (OpenCV usa BGR)
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Salvar temporariamente para processamento
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            cv2.imwrite(temp_file.name, image_array)
            temp_path = temp_file.name
        
        try:
            # Processar com OMR
            processor = OMRProcessor()
            results = processor.process_omr_image(temp_path, num_questions)
            return results
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"Erro ao processar arquivo enviado: {str(e)}")
        return [''] * num_questions


def test_omr_with_sample():
    """Função de teste com imagem de exemplo"""
    # Implementar teste se necessário
    pass
