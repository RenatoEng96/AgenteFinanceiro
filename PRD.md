# PRD – Agente de IA para Análise Fundamentalista Avançada

## 1. Visão Geral

Desenvolver um agente de Inteligência Artificial especializado em **análise fundamentalista de ações**, capaz de integrar dados estruturados (Yahoo Finance API), dados não estruturados (PDFs de DRE, releases e relatórios financeiros) e conhecimento financeiro avançado para produzir análises de nível institucional.

O agente deverá avaliar empresas considerando **cenário macroeconômico, setor, características específicas da companhia** e aplicar **múltiplos métodos de valuation**, incluindo abordagens determinísticas e probabilísticas (Monte Carlo).

---

## 2. Objetivo do Produto

Fornecer ao usuário uma **avaliação profunda, crítica e quantitativa** de empresas listadas, permitindo:

* Identificar subavaliação ou superavaliação
* Entender riscos, assimetrias e drivers de valor
* Apoiar decisões de investimento baseadas em dados e probabilidade

---

## 3. Público-Alvo

* Investidores individuais avançados
* Analistas buy-side e sell-side
* Gestores de portfólio quantitativos ou fundamentalistas
* Desenvolvedores de sistemas de apoio à decisão financeira

---

## 4. Escopo Funcional

### 4.1 Entrada de Dados

* Ticker da empresa
* PDFs financeiros (DRE, balanço, fluxo de caixa, releases)

### 4.2 Fontes de Dados

* Yahoo Finance API

  * Preços históricos
  * Indicadores financeiros
  * Demonstrações financeiras padronizadas
* PDFs fornecidos pelo usuário

---

## 5. Funcionalidades Principais

### 5.1 Análise Macroeconômica

* Avaliação do ciclo econômico
* Impacto de juros, inflação e política monetária
* Relação entre macro e custo de capital da empresa

### 5.2 Análise Setorial

* Estrutura competitiva
* Ciclicidade
* Barreiras de entrada
* Sensibilidade a fatores externos

### 5.3 Análise Qualitativa da Empresa

* Modelo de negócios
* Vantagens competitivas (moat)
* Qualidade da gestão
* Riscos operacionais e estratégicos

### 5.4 Análise Quantitativa

* Análise completa de DRE, balanço e fluxo de caixa
* Cálculo de ROIC, WACC, margens, alavancagem
* Avaliação da qualidade da geração de caixa

---

## 6. Valuation

### Métodos Obrigatórios

* Fluxo de Caixa Descontado (DCF)
* Fluxo de Caixa Descontado Reverso
* DCF com Simulação de Monte Carlo
* Valuation por múltiplos
* Método de Bazin
* Método de Graham

Cada método deve apresentar:

* Premissas explícitas
* Valor justo estimado
* Limitações

---

## 7. Outputs Esperados

* Resumo executivo
* Preço justo por método
* Intervalo de valor provável
* Cenários (bear / base / bull)
* Probabilidade de upside
* Principais riscos e gatilhos
* Conclusão objetiva (subavaliada, neutra, superavaliada)

---

## 8. Critérios de Sucesso

* Coerência financeira
* Transparência das premissas
* Capacidade de lidar com incerteza
* Análises reproduzíveis e auditáveis

---

## 9. Fora de Escopo

* Recomendações automáticas de compra/venda sem ressalvas
* Day trade ou trading técnico
* Previsão determinística de preços

---

## 10. Restrições

* Não inventar dados
* Diferenciar fatos, estimativas e opiniões
* g de perpetuidade < WACC
* Reconhecer limitações dos modelos
