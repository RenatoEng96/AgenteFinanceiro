SPECS – Especificação Técnica Avançada: Agente AgFin

1. Arquitetura do Sistema e Design Pattern

O AgFin opera sob uma arquitetura de Agentes Autônomos Orquestrados (Hierarchical Agentic Workflow). O sistema não é monolítico; ele divide a tarefa de análise em sub-tarefas especializadas executadas por "personas" de LLM distintas, consolidadas por um orquestrador matemático.

1.1 Diagrama de Componentes

Ingestion Layer (ETL):

YFinance Wrapper: Coleta de dados de mercado (OHLCV) e fundamentais (Financials).

Unstructured Data Parser: Processamento de PDFs (OCR via Tesseract/PyMuPDF) e NLP para extração de "Management Discussion & Analysis".

Core Calculation Engine (Python):

Motor matemático determinístico (NumPy/Pandas).

Motor estocástico (SciPy) para Monte Carlo.

Cognitive Layer (LLM):

Macro Analyst Agent: Analisa conjuntura econômica.

Forensic Accountant Agent: Analisa qualidade dos números (Accruals, itens não recorrentes).

Valuation Strategist Agent: Define premissas de crescimento baseadas em moat e setor.

Presentation Layer:

Gerador de Relatórios (PDF).

2. Motor Matemático de Valuation (The Quant Engine)

Esta seção define o rigor matemático obrigatório para os cálculos do agente.

2.1 Custo Médio Ponderado de Capital (WACC)

O WACC será a taxa de desconto base para o DCF.

$$WACC = K_e \times \frac{E}{E+D} + K_d \times (1 - t) \times \frac{D}{E+D}$$

Onde:

$E$: Valor de mercado do Equity (Market Cap).

$D$: Valor de mercado da Dívida (Total Debt).

$t$: Alíquota efetiva de imposto (Tax Rate).

2.1.1 Custo do Equity ($K_e$) - CAPM Modificado

O modelo deve utilizar o Capital Asset Pricing Model com ajuste de risco país (para empresas em mercados emergentes).

$$K_e = R_f + \beta_L (R_m - R_f) + \lambda_{country}$$

Risk-Free Rate ($R_f$): Yield do título do tesouro de 10 anos (US Treasury para ações globais, NTN-B ou DI Longo para Brasil, ajustado pela paridade de inflação se necessário).

Equity Risk Premium ($R_m - R_f$): Prêmio de risco histórico (ex: Damodaran data).

Country Risk Premium ($\lambda_{country}$): Spread do CDS de 5 anos do país.

2.1.2 Beta Alavancado ($\beta_L$)

O agente não deve usar o Beta bruto do Yahoo Finance cegamente. Ele deve calcular o Beta Bottom-up ou desalavancar o Beta do setor e realavancar pela estrutura de capital da empresa alvo.

$$\beta_U = \frac{\beta_{sector}}{1 + (1-t)(\frac{D}{E})_{sector}}$$

$$\beta_L = \beta_U \times [1 + (1-t_{target})(\frac{D}{E})_{target}]$$

2.2 Fluxo de Caixa Descontado (DCF) - Modelo FCFF

O Valuation principal será baseado no Free Cash Flow to Firm.

2.2.1 Cálculo do FCFF Histórico e Projetado

$$FCFF = EBIT \times (1 - t) + Depreciation \& Amortization - CAPEX - \Delta NWC$$

$\Delta NWC$: Variação do Capital de Giro Líquido (Net Working Capital).

$NWC = (Current Assets - Cash) - (Current Liabilities - Short Term Debt)$.

2.2.2 Valor Presente dos Fluxos Explícitos (PV)

Para um período de projeção $n$ (padrão: 10 anos):

$$PV_{explicit} = \sum_{t=1}^{n} \frac{FCFF_t}{(1 + WACC)^t}$$

2.2.3 Valor Terminal (TV)

O agente deve calcular o TV por dois métodos e criar uma faixa de valor.

Método A: Gordon Growth Model (Perpetuidade)


$$TV_{Gordon} = \frac{FCFF_{n+1}}{WACC - g}$$

Restrição Rígida: $g \leq R_f$ (A empresa não pode crescer mais que a economia para sempre).

Método B: Múltiplos de Saída (Exit Multiple)


$$TV_{Multiple} = EBITDA_{n} \times (EV/EBITDA)_{target}$$

2.2.4 Enterprise Value e Equity Value

$$Enterprise Value (EV) = PV_{explicit} + \frac{TV}{(1 + WACC)^n}$$

$$Equity Value = EV - Net Debt - Minorities + Non Operating Assets$$

$$Fair Price = \frac{Equity Value}{Shares Outstanding}$$

2.3 Modelo Estocástico: Simulação de Monte Carlo

Para capturar a incerteza, o agente executará uma simulação de Monte Carlo com $N=10.000$ iterações.

2.3.1 Vetor de Variáveis Aleatórias

Definimos o vetor de variáveis estocásticas $X = [g_{rev}, \%EBIT, WACC, g_{perp}]$.
Cada variável segue uma distribuição de probabilidade específica:

Crescimento de Receita ($g_{rev}$): Distribuição Normal $N(\mu, \sigma)$ baseada na volatilidade histórica da receita e projeções do setor.

Margem EBIT ($\%EBIT$ ): Distribuição Triangular $T(min, mode, max)$ ou Beta-PERT, limitando margens irrealistas.

WACC: Distribuição Normal $N(\mu, \sigma)$ para capturar a volatilidade dos juros e do beta.

2.3.2 Algoritmo de Simulação

Para cada iteração $i \in \{1, ..., N\}$:

Amostrar $X_i$ das distribuições definidas.

Recalcular todo o fluxo de caixa $FCFF_i$ projetado.

Calcular $Price_i$.

Armazenar no vetor de resultados $R$.

2.3.3 Output Estatístico

VaR (Value at Risk): Percentil 5% da distribuição de preços.

Intervalo de Confiança: $[P_{25}, P_{75}]$.

Probabilidade de Upside: $P(Price_{sim} > Price_{market}) = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}_{Price_i > Price_{current}}$.

2.4 Modelos de "Checagem de Sanidade"

2.4.1 Modelo de Décio Bazin (Focado em Dividendos)

Para empresas maduras/dividend growth:


$$Price_{fair} = \frac{DPS}{0.06}$$

Onde $DPS$ é o Dividendo Por Ação médio dos últimos 3 anos (ajustado).

2.4.2 Fórmula de Benjamin Graham (Valor Intrínseco Clássico)

Adaptada para evitar distorções modernas, mas mantendo a essência do "Deep Value":


$$V = \sqrt{22.5 \times EPS \times BVPS}$$

$EPS$: Lucro por ação.

$BVPS$: Valor patrimonial por ação.

2.4.3 Reverse DCF

Calcula qual é o crescimento implícito no preço atual da ação.
Isolar $g$ na equação do DCF tal que $PV(g) = Price_{current}$.

Se $g_{implied} > g_{fundamental}$, a ação está cara.

3. Engenharia de Prompt e Estratégia Cognitiva

O "LLM Core" não deve receber apenas dados brutos. Ele deve ser guiado por instruções de sistema rigorosas (System Prompts) que definem sua "Persona".

3.1 Persona: The Institutional Analyst

O prompt do sistema deve conter as seguintes diretrizes explícitas:

ROLE: Você é um Analista de Investimentos Sênior CFA Charterholder com 20 anos de experiência em Buy-Side.

TONE: Profissional, cético, baseado em dados e objetivo. Evite adjetivos exagerados ("incrível", "explodindo"). Use termos técnicos precisos.

PRIME DIRECTIVE: Sua prioridade é proteger o capital do investidor. Você prefere cometer um erro do Tipo II (deixar de comprar uma boa ação) do que um erro do Tipo I (comprar uma ação ruim/fraudulenta).

DATA HANDLING:

Diferencie claramente entre Reported GAAP e Non-GAAP/Adjusted.

Ao analisar PDFs, busque ativamente por notas de rodapé que indiquem riscos ocultos (passivos contingentes, mudanças contábeis).

3.2 Chain-of-Thought (CoT) para Análise Qualitativa

Para a análise de "Moat" (Vantagem Competitiva), o prompt deve forçar um raciocínio passo-a-passo:

Identificar o Moat: (Network Effect, Switching Cost, Cost Advantage, Intangibles).

Validar com Dados: O moat está aparecendo nos números? (Ex: Se diz ter "Pricing Power", a Margem Bruta é estável ou crescente? O ROIC é superior ao WACC?).

Durabilidade: Esse moat é sustentável por 10 anos? (Risk assessment).

4. Pipeline de Processamento de Dados (ETL)

4.1 Input - Yahoo Finance API (yfinance)

Coletar dados brutos e calcular métricas derivadas (TTM - Trailing Twelve Months):

income_statement: Revenue, Cost of Revenue, Operating Expenses, Interest Expense, Tax Provision.

balance_sheet: Cash, Receivables, Inventory, PP&E, Goodwill, Payables, Long Term Debt.

cash_flow: Depreciation, Stock Based Compensation, Capex.

4.2 Input - PDF Parser

Ferramenta: PyMuPDF ou OCR para extração de texto.

Técnica: Keyword Spotting em torno de "Outlook", "Guidance", "Risks", "Litigation".

Filtro de Ruído: Remover disclaimers padrão e linguagem de marketing ("boilerplates").

4.3 Normalização

Ajustar EBIT para remover itens não recorrentes identificados no PDF (ex: ganho na venda de ativos, multas regulatórias).

Padronizar datas fiscais para anos civis se necessário para comparabilidade setorial.


5. Stack Tecnológico Sugerido

Linguagem: Python 3.10+

Dados Financeiros: yfinance, alpha_vantage (backup).

Cálculo Numérico: numpy (vetorização), pandas (séries temporais), scipy.stats (distribuições para Monte Carlo).

LLM Interface: Gemini API.

Document Processing: unstructured, pdfplumber.