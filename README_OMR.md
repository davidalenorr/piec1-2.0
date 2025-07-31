# Funcionalidade OMR (Optical Mark Recognition) - Documentação

## Visão Geral
A funcionalidade OMR implementada permite o escaneamento automático de gabaritos preenchidos usando OpenCV para detectar marcações e calcular notas automaticamente.

## Como Usar a Funcionalidade OMR

### 1. Pré-requisitos
- Prova criada no sistema com gabarito gerado
- Aluno cadastrado na disciplina
- Imagem do gabarito preenchido (formato JPG, PNG)

### 2. Processo de Escaneamento

#### Passo 1: Acessar a Disciplina
1. Faça login no sistema
2. Navegue até a disciplina desejada
3. Visualize a lista de alunos

#### Passo 2: Iniciar Processo OMR
1. Clique no botão "Ações" do aluno desejado
2. Selecione a avaliação (1VA, 2VA, 3VA, Final)
3. O modal "Escaneamento OMR" será aberto

#### Passo 3: Configurar Escaneamento
1. **Selecionar Prova**: Escolha a prova correspondente ao gabarito
2. **Upload da Imagem**: Faça upload da foto do gabarito preenchido
3. **Iniciar Escaneamento**: Clique em "📷 Escanear Gabarito"

#### Passo 4: Revisar Resultado
1. O sistema processará a imagem usando OpenCV
2. Será exibido:
   - Respostas detectadas (ex: "1: A, 2: B, 3: C...")
   - Nota calculada (ex: "8.5/10 (17/20 acertos)")
3. Revise os resultados

#### Passo 5: Aplicar Nota
1. Se estiver satisfeito com o resultado, clique em "✅ Aplicar Nota"
2. A nota será registrada no sistema para o aluno
3. O modal será fechado e a página atualizada

## Especificações Técnicas

### Formatos de Imagem Suportados
- JPG/JPEG
- PNG
- Recomendado: Alta resolução (mínimo 800x600)

### Algoritmo de Detecção
- **Pré-processamento**: Escala de cinza, filtro Gaussiano
- **Detecção**: Threshold adaptativo + detecção de contornos
- **Filtragem**: Contornos circulares com área entre 100-2000 pixels
- **Análise**: Contagem de pixels preenchidos por alternativa

### Requisitos da Imagem
1. **Qualidade**: Imagem nítida, bem iluminada
2. **Ângulo**: Gabarito alinhado (sem rotação excessiva)
3. **Contraste**: Marcações escuras em fundo claro
4. **Limpeza**: Sem rabiscos ou marcações desnecessárias

## Troubleshooting

### Problema: Respostas Não Detectadas
**Possíveis Causas:**
- Imagem de baixa qualidade
- Marcações muito claras
- Gabarito mal alinhado

**Soluções:**
- Tirar nova foto com melhor iluminação
- Usar caneta/lápis mais escuro
- Alinhar o gabarito corretamente

### Problema: Detecção Incorreta
**Possíveis Causas:**
- Marcações múltiplas na mesma questão
- Rabiscos no gabarito
- Sombras na imagem

**Soluções:**
- Garantir apenas uma marcação por questão
- Limpar o gabarito antes de fotografar
- Usar iluminação uniforme

### Problema: Erro no Upload
**Possíveis Causas:**
- Arquivo muito grande
- Formato não suportado
- Problema de conectividade

**Soluções:**
- Reduzir tamanho da imagem
- Converter para JPG
- Verificar conexão com internet

## Estrutura dos Arquivos

### Backend
- `cadastro/omr_processor.py`: Processador principal OMR
- `cadastro/views.py`: View `processar_omr()` 
- `cadastro/models.py`: Modelos `GabaritoProva`, `ResultadoAluno`

### Frontend
- `detalhe_disciplina.html`: Interface do modal OMR
- `style.css`: Estilos dos modais
- JavaScript: Funções `executarOMR()` e `aplicarNota()`

### Dependências
- OpenCV (`opencv-python`)
- NumPy (`numpy`)
- Pillow (`Pillow`)
- imutils (`imutils`)

## API Endpoints

### POST /cadastro/processar_omr/
**Parâmetros:**
- `prova_id`: ID da prova
- `aluno_matricula`: Matrícula do aluno
- `avaliacao`: Tipo de avaliação (1VA, 2VA, etc.)
- `foto_gabarito`: Arquivo de imagem

**Resposta:**
```json
{
  "success": true,
  "respostas_detectadas": ["A", "B", "C", "D", "E"],
  "acertos": 4,
  "total": 5,
  "nota": 8.0,
  "detalhes": {
    "prova_id": 1,
    "aluno_matricula": "12345",
    "avaliacao": "1VA"
  }
}
```

### POST /cadastro/aplicar_nota_omr/
**Parâmetros:**
- `matricula`: Matrícula do aluno
- `avaliacao`: Tipo de avaliação
- `nota`: Nota a ser aplicada

**Resposta:**
```json
{
  "success": true,
  "message": "Nota aplicada com sucesso"
}
```

## Limitações Atuais

1. **Formato de Gabarito**: Funciona melhor com gabaritos de múltipla escolha padrão
2. **Qualidade da Imagem**: Requer imagens de boa qualidade
3. **Tipos de Marcação**: Otimizado para marcações circulares preenchidas
4. **Quantidade de Questões**: Testado para 5-20 questões

## Melhorias Futuras

1. **Detecção de Orientação**: Correção automática de rotação
2. **Machine Learning**: Treinamento para diferentes tipos de marcação
3. **Validação Visual**: Interface para correção manual
4. **Batch Processing**: Processamento de múltiplos gabaritos
5. **Relatórios**: Dashboard com estatísticas de escaneamento

## Testando a Funcionalidade

Para testar localmente:
```bash
# Executar teste com imagens de exemplo
python cadastro/test_omr.py

# Verificar dependências
pip list | grep opencv
pip list | grep numpy
```

## Suporte

Para problemas ou dúvidas:
1. Verificar logs do Django no terminal
2. Conferir console do navegador (F12)
3. Testar com imagens de exemplo da pasta `gabaritos para teste/`
