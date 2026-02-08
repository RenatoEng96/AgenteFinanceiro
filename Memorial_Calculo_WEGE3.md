# Memorial de Cálculo - Auditoria do Agente

**Ticker:** WEGE3
**Data:** 2026-02-08 11:35:47
**Versão do Agente:** 2.0 (Audit Mode)

---

## 1. Auditoria de Inputs (Yahoo Finance & PDF)

### Dados Fundamentais Coletados
| Métrica | Valor | Descrição |
|---|---|---|
| ticker | WEGE3.SA | - |
| cotacao | 51.8500 | - |
| market_cap | 217546817536 | - |
| lpa_yahoo | 1.5500 | - |
| vpa_yahoo | 5.3410 | - |
| div_12m | 2.4506 | - |
| dy_anual | 0.0473 | - |
| pl | 33.4516 | - |
| pvp | 9.7079 | - |
| ev_ebitda | 24.6310 | - |
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
| divida_liquida_total_reais | -3484456000.0000 | - |
| escala_identificada | Milhares de Reais (Reais Mil) | - |
| riscos_citados | 1. Risco de Crédito em Contas a Receber: A administração identificou um montante de R$ 110,9 milhões classificado como risco alto de perda e R$ 46,4 milhões como risco médio. 2. Risco Cambial e de Volatilidade de Commodities: Exposição significativa a múltiplas moedas e ao preço do cobre, exigindo uma estrutura complexa de derivativos (NDF e Swaps) para mitigar impactos no resultado financeiro. | - |
| moat_score | 9 | - |
| moat_justificativa | A WEG demonstra um fosso econômico (Moat) excepcional através de sua escala global e diversificação de portfólio (Indústria e Energia). A empresa mantém uma posição de caixa líquido robusta (dívida líquida negativa de R$ 3,48 bilhões), alta eficiência operacional com forte geração de valor adicionado e barreira de entrada tecnológica, além de crescimento inorgânico estratégico, como a recente aquisição da Tupimambá Energia. | - |


## 2. Auditoria Macro & Estratégia

- **Perfil Definido:** PADRAO
### Cálculo do Custo de Capital Próprio (Ke - CAPM)
Formula: $Ke = Rf + Beta \times ERP + Risk_{Country}$
- Rf (Risk Free): 0.115
- Beta: 0.6
- ERP (Equity Risk Premium): 0.055
- Country Risk: 0.02
- **Ke Calculado:** 0.168

### Cálculo do WACC
- Peso Dívida (Wd): 2.08%
- Peso Equity (We): 97.92%
- Custo Dívida Nominal: 12.00%
- Tax Rate Efetiva: 34.00%
- **WACC Final:** 14.15%

## 3. Rastreabilidade do Valuation (DCF)

**Valor Justo Final:** R$ 32.13
**Premissas Usadas:** {'WACC': '14.1%', 'Cresc.': '13.0%'}

### Auditoria Monte Carlo
Resultados Estatísticos:
{
  "Mean": 21.49,
  "Median": 27.64,
  "VaR_5_Percent": 0.0,
  "Upside_95_Percent": 35.05,
  "Std_Dev": 13.48,
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
        - Cotação: R$ 51.85 | Market Cap: R$ 217.55B
        - Perfil Estratégico: COMPOUNDER (Elite) [Moat Premium]
        - ROE: 31.2% | Margem Líq: 15.7%
        - Múltiplos: P/L 33.451614x | EV/EBITDA 24.631x | P/VP 9.707919x | DY 4.7%
        - Moat Score: 9/10 (A WEG demonstra um fosso econômico (Moat) excepcional através de sua escala global e diversificação de portfólio (Indústria e Energia). A empresa mantém uma posição de caixa líquido robusta (dívida líquida negativa de R$ 3,48 bilhões), alta eficiência operacional com forte geração de valor adicionado e barreira de entrada tecnológica, além de crescimento inorgânico estratégico, como a recente aquisição da Tupimambá Energia.)

        AUDITORIA & VALUATION:
        1. VALUATION INTRÍNSECO (DCF):
           - Valor Justo (Determinístico): R$ 32.13 (Margem: -38.0%)
           - WACC Usado: 14.1% | Crescimento (g): 13.0%
           - Reverse DCF: O mercado precifica crescimento implícito de 20.2% a.a. (Se aplicável).

        2. SIMULAÇÃO DE MONTE CARLO (PROBABILÍSTICA):
           
            - Preço Médio: R$ 21.49 | Mediana: R$ 27.64
            - Cenário Pessimista (VaR 5%): R$ 0.0
            - Cenário Otimista (95%): R$ 35.05
            - Probabilidade de Upside (vs R$ 51.85): 0.0%
            

        3. VALUATION RELATIVO (PARES):
           - 
            A empresa negocia com DESCONTO de 18.6% no P/L em relação à média do setor.
            Se negociasse no múltiplo médio de P/L dos pares, a ação valeria R$ 63.68.
            
        
        4. AUDITORIA FORENSE (QUALIDADE CONTÁBIL):
           - Score de Qualidade: 10/10
           - Alertas detectados pelo algoritmo:
           Nenhuma anomalia detectada.
           
        5. RISCOS REPORTADOS:
           - 1. Risco de Crédito em Contas a Receber: A administração identificou um montante de R$ 110,9 milhões classificado como risco alto de perda e R$ 46,4 milhões como risco médio. 2. Risco Cambial e de Volatilidade de Commodities: Exposição significativa a múltiplas moedas e ao preço do cobre, exigindo uma estrutura complexa de derivativos (NDF e Swaps) para mitigar impactos no resultado financeiro.

        ESTRUTURA OBRIGATÓRIA DO MEMORANDO:
        ## 1. Executive Summary & Veredito
        Comece com a conclusão. COMPRA (Buy), MANTER (Hold) ou VENDA (Sell). Defina o "Target Price" (use o DCF como base, ajustado pelo seu julgamento qualitativo). Resuma a tese em 3 bullets matadores.

        ## 2. A Tese Micro vs. O Cenário Macro
        Como essa empresa navega o ciclo atual (Selic 15.0% | IPCA 4.26% | Juro Real 10.30% | Ciclo: CONTRACIONISTA (Aperto Monetário))? A inflação/juros ajudam ou atrapalham?
        
        ## 3. Qualidade & Fosso (The Moat)
        O Moat é durável? A empresa tem poder de preço? Analise o ROE vs Custo de Capital.

        ## 4. Valuation Intrínseco & Cenários
        Discuta o Valor Justo do DCF (32.13) e compare com os múltiplos.
        ANÁLISE DE SENSIBILIDADE (Stress Test):
        - O modelo indica um range de valor entre R$ 26.93 (Cenário Pessimista) e R$ 38.95 (Cenário Otimista).
        - Com base nisso, quão segura é a Margem de Segurança atual?
        *Comente explicitamente sobre os alertas da Auditoria Forense se houverem.*

        ## 5. Riscos do "Bear Case"
        O que pode destruir essa tese? (Regulação, concorrência, ciclo, fraude contábil). Seja brutal.

        TOM DE VOZ:
        Direto, analítico, sofisticado. Evite clichês ("empresa sólida"). Use dados para suportar adjetivos.
        
```

### Resposta Recebida (Raw)
**PARA:** Comitê de Investimentos – Global Multi-Strategy Fund
**DE:** Sócio Sênior de Equities
**DATA:** 23 de Maio de 2024
**ASSUNTO:** MEMORANDO DE INVESTIMENTO: WEG S.A. (WEGE3.SA) – Tese de Exaustão de Valuation e Risco de Duration.

---

## 1. Executive Summary & Veredito

**VEREDITO: VENDA (SELL) / UNDERWEIGHT**
**Target Price (FY24): R$ 32.13 (Baseado em DCF)**
**Upside/Downside:** -38.0%

**Resumo da Tese:**
1.  **Hurdle Rate Proibitivo:** Em um cenário de Juro Real de 10.30%, o custo de oportunidade para carregar uma empresa de *growth* com P/L de 33x torna-se matematicamente insustentável. A WEG é uma máquina de capital, mas o preço atual exige uma execução perfeita que o ciclo macro não perdoa.
2.  **Desconexão Intrínseca:** O mercado precifica um crescimento implícito de 20.2% a.a. (Reverse DCF). Embora a WEG seja um *compounder* histórico, a reversão à média da economia global e a saturação de mercados maduros tornam essa meta excessivamente otimista.
3.  **A Armadilha do Relativo:** O desconto de 18.6% frente aos pares globais é uma miragem tática. Não reflete a "barateza" da WEG, mas sim a sobrevalorização do setor industrial global em um momento de contração monetária, onde múltiplos deveriam estar comprimindo, não expandindo.

---

## 2. A Tese Micro vs. O Cenário Macro

Vivemos um cenário de **Aperto Monetário Severo (Selic 15.0%)**. Do ponto de vista de *First Principles*, o valor de uma empresa é o valor presente dos seus fluxos de caixa futuros descontados a uma taxa que reflita o risco e o tempo.

*   **O Conflito:** A WEG possui uma *duration* longa. Teses de crescimento são as mais penalizadas quando o Juro Real sobe (atualmente em 10.30%). O fluxo de caixa que a WEG gerará em 2028 vale muito menos hoje do que valia há 24 meses.
*   **Resiliência Operacional vs. Realidade Financeira:** Embora a WEG navegue bem na inflação (repassando custos via eficiência), o custo de capital (WACC de 14.1%) "come" grande parte da geração de valor para o acionista. Em ciclos contracionistas, o mercado migra de *crescimento futuro* para *fluxo de caixa imediato*. Com um DY de 4.7%, a WEG não oferece proteção de renda comparada à renda fixa soberana brasileira.

---

## 3. Qualidade & Fosso (The Moat)

A qualidade da WEG é inquestionável, mas precisamos separar o **negócio** da **ação**. 

*   **ROE de 31.2%:** Indica uma vantagem competitiva (Moat) real. A WEG não vende apenas motores; ela vende eficiência energética e integração sistêmica. Sua dívida líquida negativa (R$ 3,48 bi) é um porto seguro em tempos de crédito caro.
*   **Poder de Preço:** A verticalização permite que a WEG mantenha margens líquidas de 15.7% mesmo com volatilidade em commodities (Cobre/Aço). 
*   **Veredito sobre o Moat:** O fosso é 9/10, sustentado por custos de troca (switching costs) elevados e escala. No entanto, o Moat protege o lucro, mas não protege o múltiplo de mercado contra uma reprecificação sistêmica de ativos de risco.

---

## 4. Valuation Intrínseco & Cenários

O mercado está ignorando a gravidade. 

*   **DCF Determinístico:** Nosso modelo aponta um Valor Justo de **R$ 32.13**. A cotação atual de R$ 51.85 representa um prêmio de 61% sobre o valor intrínseco.
*   **Simulação de Monte Carlo:** A probabilidade de *upside* estatístico é de **0.0%**. Mesmo em nosso cenário otimista (95º percentil), o valor chega a R$ 35.05, ainda muito abaixo do preço de tela.
*   **Análise de Sensibilidade:**
    *   *Cenário Bear (Stress Test):* R$ 26.93. Se houver desaceleração industrial global e o crescimento cair para um dígito, o papel colapsa.
    *   *Audit Forense:* O Score 10/10 confirma que o lucro é "limpo" (não há manipulação contábil), o que torna o *downside* puramente uma questão de preço/expectativa, e não de fraude.

---

## 5. Riscos do "Bear Case" (O que pode destruir a tese?)

Como céticos, devemos listar o que pode invalidar nossa recomendação de venda:

1.  **Deterioração de Crédito Oculta:** O montante de R$ 110,9 milhões em risco alto de perda nas contas a receber pode ser a ponta do iceberg se o cenário macro brasileiro degradar a solvência de clientes industriais menores.
2.  **Risco Cambial e Derivativos:** A estrutura complexa de NDFs e Swaps para mitigar o Cobre e o Câmbio é eficiente, mas em eventos de "cauda" (black swan), o custo de hedge pode disparar, comprimindo a margem líquida.
3.  **O "Custo da Perfeição":** Quando uma empresa negocia a 33x lucro, qualquer crescimento reportado de 15% (que seria excelente para qualquer outra empresa) é lido pelo mercado como uma falha épica, gerando liquidações forçadas.

**CONCLUSÃO DO SÓCIO:**
A WEG é uma joia da indústria brasileira, mas o preço atual é um tributo ao otimismo cego. Em um mundo de Selic a 15%, não pagamos 33x lucro por crescimento incerto. **Recomendamos a redução imediata de exposição (Underweight), visando realocação em ativos com maior margem de segurança ou retorno sobre capital ajustado ao risco.**

---
*Assinado,*

**Senior Partner**
*Global Multi-Strategy Fund*