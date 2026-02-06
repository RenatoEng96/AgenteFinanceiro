# Memorial de Cálculo - Auditoria do Agente

**Ticker:** WEGE3
**Data:** 2026-02-06 11:50:15
**Versão do Agente:** 2.0 (Audit Mode)

---

## 1. Auditoria de Inputs (Yahoo Finance & PDF)

### Dados Fundamentais Coletados
| Métrica | Valor | Descrição |
|---|---|---|
| ticker | WEGE3.SA | - |
| cotacao | 52.2400 | - |
| market_cap | 219183153152 | - |
| lpa_yahoo | 1.5500 | - |
| vpa_yahoo | 5.3410 | - |
| div_12m | 2.4506 | - |
| dy_anual | 0.0469 | - |
| pl | 33.7032 | - |
| pvp | 9.7809 | - |
| ev_ebitda | 24.8030 | - |
| margem_liq | 0.1567 | - |
| roe | 0.3119 | - |
| crescimento_receita | 0.0420 | - |
| beta | 0.1040 | - |
| fcff_por_acao | 1.6256 | - |
| divida_liquida_por_acao | -0.6479 | - |
| total_acoes | 4195695973 | - |
| setor | Industrials | - |
| industria | Electrical Equipment & Parts | - |
| nome | WEG S.A. | - |
| receita_liquida | 41379594240 | - |
| ebitda | 8762923008 | - |
| lucro_liquido | 6482753024 | - |
| fluxo_caixa_operacional | 6820317184 | - |
| divida_total | 4617108992 | - |
| caixa_total | 7335310848 | - |
| tax_rate_efetiva | 0.3400 | - |
| custo_divida_bruto | 0.1200 | - |
| despesa_financeira | 0 | - |
| divida_liquida_total_reais | -2565732000.0000 | - |
| escala_identificada | Milhares de Reais (R$ mil) | - |
| riscos_citados | 1. Risco tributário sobre lucros auferidos no exterior (exposição estimada em R$ 911,3 milhões); 2. Contingências cíveis possíveis totalizando R$ 442 milhões, incluindo litígios de responsabilidade civil por produtos e seguros. | - |
| moat_score | 9 | - |
| moat_justificativa | A WEG demonstra um fosso econômico robusto evidenciado pelo ROIC de 32,4%, muito acima do custo de capital. Sua vantagem competitiva (Moat) reside na integração vertical, forte investimento em P&D (3,5% da ROL) e flexibilidade produtiva global, que permite redirecionar rotas de exportação para mitigar impactos de legislações tarifárias e incertezas geopolíticas. | - |


## 2. Auditoria Macro & Estratégia

- **Perfil Definido:** PADRAO
### Cálculo do Custo de Capital Próprio (Ke - CAPM)
Formula: $Ke = Rf + Beta \times ERP + Risk_{Country}$
- Rf (Risk Free): 0.15
- Beta: 0.5
- ERP (Equity Risk Premium): 0.06
- Country Risk: 0.025
- **Ke Calculado:** 0.205

### Cálculo do WACC
- Peso Dívida (Wd): 2.06%
- Peso Equity (We): 97.94%
- Custo Dívida Nominal: 12.00%
- Tax Rate Efetiva: 34.00%
- **WACC Final:** 19.74%

## 3. Rastreabilidade do Valuation (DCF)

**Valor Justo Final:** R$ 21.17
**Premissas Usadas:** {'WACC': '19.7%', 'Cresc.': '15.7%'}

### Auditoria Monte Carlo
Resultados Estatísticos:
{
  "Mean": 21.52,
  "Median": 21.2,
  "VaR_5_Percent": 16.35,
  "Upside_95_Percent": 28.02,
  "Std_Dev": 3.76,
  "Upside_Prob": "0.0%",
  "Iterations": 10000
}

## 4. Auditoria da IA (Prompt & Output)

### Contexto Enviado ao LLM (Prompt)
```text

        Atue como um SÓCIO SÊNIOR de um Fundo Multi-Estratégia Global. Escreva um MEMORANDO DE INVESTIMENTO de alta convicção sobre WEGE3.SA.
        
        MINDSET:
        - Use "First Principles Thinking": Questione os consensos. Por que a empresa lucra? O fosso é real?
        - Seja Cético: Assuma que o mercado é eficiente, a menos que provado o contrário.
        - Macro-Aware: Conecte o ciclo econômico (Juro Real, Inflação) com a tese micro.
        
        CONTEXTO ECONÔMICO (MACRO):
        Selic 15.0% | IPCA 4.26% | Juro Real 10.30% | Ciclo: CONTRACIONISTA (Aperto Monetário)
        -> Se o Ciclo for CONTRACIONISTA (Juro Real alto), penalize teses de crescimento longo e valorize fluxo de caixa hoje.
        -> Se o Ciclo for EXPANSIONISTA, valorize duration e crescimento.

        DADOS DA EMPRESA:
        - Ticker: WEGE3.SA (WEG S.A.)
        - Cotação: R$ 52.24 | Market Cap: R$ 219.18B
        - Perfil Estratégico: GROWTH / COMPOUNDER (Alta Qualidade) [Wide Moat] [Macro Headwind]
        - ROE: 31.2% | Margem Líq: 15.7%
        - Múltiplos: P/L 33.703228x | EV/EBITDA 24.803x | P/VP 9.78094x | DY 4.7%
        - Moat Score: 9/10 (A WEG demonstra um fosso econômico robusto evidenciado pelo ROIC de 32,4%, muito acima do custo de capital. Sua vantagem competitiva (Moat) reside na integração vertical, forte investimento em P&D (3,5% da ROL) e flexibilidade produtiva global, que permite redirecionar rotas de exportação para mitigar impactos de legislações tarifárias e incertezas geopolíticas.)

        AUDITORIA & VALUATION:
        1. VALUATION INTRÍNSECO (DCF):
           - Valor Justo (Determinístico): R$ 21.17 (Margem: -59.5%)
           - WACC Usado: 19.7% | Crescimento (g): 15.7%
           - Reverse DCF: O mercado precifica crescimento implícito de 30.8% a.a. (Se aplicável).

        2. SIMULAÇÃO DE MONTE CARLO (PROBABILÍSTICA):
           
            - Preço Médio: R$ 21.52 | Mediana: R$ 21.2
            - Cenário Pessimista (VaR 5%): R$ 16.35
            - Cenário Otimista (95%): R$ 28.02
            - Probabilidade de Upside (vs R$ 52.24): 0.0%
            

        3. VALUATION RELATIVO (PARES):
           - 
            A empresa negocia com DESCONTO de 17.7% no P/L em relação à média do setor.
            Se negociasse no múltiplo médio de P/L dos pares, a ação valeria R$ 63.47.
            
        
        4. AUDITORIA FORENSE (QUALIDADE CONTÁBIL):
           - Score de Qualidade: 10/10
           - Alertas detectados pelo algoritmo:
           Nenhuma anomalia detectada.
           
        5. RISCOS REPORTADOS:
           - 1. Risco tributário sobre lucros auferidos no exterior (exposição estimada em R$ 911,3 milhões); 2. Contingências cíveis possíveis totalizando R$ 442 milhões, incluindo litígios de responsabilidade civil por produtos e seguros.

        ESTRUTURA OBRIGATÓRIA DO MEMORANDO:
        ## 1. Executive Summary & Veredito
        Comece com a conclusão. COMPRA (Buy), MANTER (Hold) ou VENDA (Sell). Defina o "Target Price" (use o DCF como base, ajustado pelo seu julgamento qualitativo). Resuma a tese em 3 bullets matadores.

        ## 2. A Tese Micro vs. O Cenário Macro
        Como essa empresa navega o ciclo atual (Selic 15.0% | IPCA 4.26% | Juro Real 10.30% | Ciclo: CONTRACIONISTA (Aperto Monetário))? A inflação/juros ajudam ou atrapalham?
        
        ## 3. Qualidade & Fosso (The Moat)
        O Moat é durável? A empresa tem poder de preço? Analise o ROE vs Custo de Capital.

        ## 4. Valuation Intrínseco & Cenários
        Discuta o Valor Justo do DCF (21.17) e compare com os múltiplos.
        ANÁLISE DE SENSIBILIDADE (Stress Test):
        - O modelo indica um range de valor entre R$ 18.09 (Cenário Pessimista) e R$ 25.02 (Cenário Otimista).
        - Com base nisso, quão segura é a Margem de Segurança atual?
        *Comente explicitamente sobre os alertas da Auditoria Forense se houverem.*

        ## 5. Riscos do "Bear Case"
        O que pode destruir essa tese? (Regulação, concorrência, ciclo, fraude contábil). Seja brutal.

        TOM DE VOZ:
        Direto, analítico, sofisticado. Evite clichês ("empresa sólida"). Use dados para suportar adjetivos.
        
```

### Resposta Recebida (Raw)
**MEMORANDO INTERNO: COMITÊ DE INVESTIMENTOS – GLOBAL MULTI-STRATEGY FUND**
**PARA:** Partners e Gestores de Portfólio
**DE:** Sócio Sênior de Estratégia Industrial
**DATA:** 22 de Maio de 2024
**ASSUNTO:** WEGE3.SA (WEG S.A.) – Tese de Desinvestimento/Underweight

---

## 1. Executive Summary & Veredito

**VEREDITO: VENDA (SELL) / UNDERWEIGHT**
**TARGET PRICE: R$ 28.50** (Ajustado pela qualidade, mas ancorado na realidade do custo de capital).

A WEG é, indiscutivelmente, a "joia da coroa" do setor industrial brasileiro. No entanto, o papel de um gestor de fundos não é colecionar troféus, mas sim retornos ajustados ao risco. A atual cotação de R$ 52.24 representa um descolamento severo entre a excelência operacional (Micro) e a gravidade econômica (Macro).

**Tese em 3 pontos fundamentais:**
1.  **A Tirania do Juro Real:** Com um Juro Real de 10.30% (Selic 15%), o custo de oportunidade para carregar um ativo de *duration* longa como a WEG é proibitivo. O mercado ignora que o WACC atual destrói o valor presente de fluxos de caixa distantes.
2.  **Impossibilidade Matemática de Crescimento:** O mercado precifica um crescimento implícito de ~31% a.a. Para uma empresa de R$ 219B de Market Cap, manter esse CAGR em um ciclo industrial global de contração desafia a lógica de retornos decrescentes.
3.  **Margem de Segurança Negativa:** O valuation intrínseco (DCF) aponta para R$ 21.17. Mesmo sendo generoso com o "prêmio de qualidade" da WEG, o prêmio atual de ~146% sobre o valor justo é injustificável.

---

## 2. A Tese Micro vs. O Cenário Macro

A WEG opera sob uma dicotomia perigosa. No **Micro**, a empresa é uma máquina de eficiência: ROIC de 32,4% e integração vertical que protege as margens. No entanto, o **Macro** atual (Ciclo CONTRACIONISTA) é o maior inimigo da tese de *Growth*.

Em um cenário de Selic a 15%, o fluxo de caixa descontado sofre uma compressão de múltiplo natural. Ativos de crescimento são, por definição, "long duration". Quando a taxa de desconto (WACC) sobe para 19.7%, o valor terminal da companhia — que compõe a maior parte do valuation da WEG — evapora. O investidor de WEGE3 está hoje pagando por um cenário de "perfeição econômica" que não condiz com um IPCA de 4.26% e um aperto monetário severo que deve reduzir o CAPEX industrial global.

---

## 3. Qualidade & Fosso (The Moat)

O Moat da WEG é **Wide** e real, mas não é infinito. 
*   **Poder de Preço e Eficiência:** O ROE de 31.2% contra um custo de capital elevado prova que a WEG ainda gera valor econômico (EVA positivo). Sua flexibilidade produtiva permite mitigar riscos tarifários (EUA/China), o que é um ativo estratégico raro.
*   **P&D como Barreira:** O investimento de 3,5% da ROL em inovação garante que ela não seja comoditizada por competidores chineses.

**Contraponto de First Principles:** O Moat justifica o prêmio sobre o valor patrimonial (P/VP 9.78x)? Historicamente, empresas industriais globais de alta qualidade (Siemens, ABB, Schneider) negociam em múltiplos significativamente inferiores. O mercado local brasileiro "santificou" a WEG, transformando-a em um porto seguro, o que inflou o múltiplo para níveis de Big Tech, sem a escalabilidade marginal do software.

---

## 4. Valuation Intrínseco & Cenários

Aqui a tese de "Comprar a qualquer preço" desmorona ante a aritmética:

*   **DCF Determinístico:** O valor de **R$ 21.17** não é um erro de cálculo; é o reflexo de trazer o fluxo de caixa de uma industrial para o presente sob um Juro Real de 10.3%. A margem de segurança de **-59.5%** é um sinal de alerta vermelho.
*   **Stress Test (Monte Carlo):** Mesmo no cenário otimista (95º percentil), o valor alcança apenas **R$ 28.02**. Note que o preço de mercado atual (R$ 52.24) está a quase 100% de distância do topo da nossa simulação probabilística.
*   **Múltiplos Relativos:** O desconto de 17.7% no P/L em relação aos pares é uma **armadilha de valor relativo**. Os pares globais podem estar igualmente sobrevalorizados ou operando em geografias com prêmios de risco distintos. Basear a compra apenas no múltiplo relativo ignorando o DCF é negligência fiduciária.
*   **Auditoria Forense:** Nota 10/10. Não há "esqueletos" contábeis. A queda da tese virá pelo preço, não pela fraude.

---

## 5. Riscos do "Bear Case" (O que pode destruir a tese)

Se você decidir manter o papel, você está ignorando os seguintes riscos brutais:

1.  **De-rating de Múltiplos:** O maior risco não é o lucro cair, mas o múltiplo P/L convergir da média histórica de "growth" (33x) para a média industrial global (15x-18x). Isso implicaria uma queda de 50% sem qualquer alteração nos fundamentos operacionais.
2.  **Exposição Tributária (BEPS/Pillar Two):** O risco de R$ 911 milhões sobre lucros no exterior não é trivial. Em um ambiente de aperto fiscal global, a WEG é um alvo fácil para autoridades tributárias sedentas por arrecadação.
3.  **O Fim do Ciclo de Commodities/Energia:** Se a transição energética global desacelerar por conta das altas taxas de juros (tornando projetos de energia renovável inviáveis no NPV), a demanda pelos produtos de alta margem da WEG sofrerá um choque de realidade.

**CONCLUSÃO DO SÓCIO:**
A WEG é uma empresa extraordinária negociada a um preço irracional. No atual ciclo de Selic a 15%, o capital tem custo. Manter WEGE3 a 33x P/L com um juro real de dois dígitos é uma aposta na "Teoria do Mais Tolo". Recomendamos a liquidação de posições e realocação em ativos com Yield real superior e valuation mais ancorado.

**Status: UNDERWEIGHT.**