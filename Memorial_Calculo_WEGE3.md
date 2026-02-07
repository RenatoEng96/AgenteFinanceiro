# Memorial de Cálculo - Auditoria do Agente

**Ticker:** WEGE3
**Data:** 2026-02-06 16:45:34
**Versão do Agente:** 2.0 (Audit Mode)

---

## 1. Auditoria de Inputs (Yahoo Finance & PDF)

### Dados Fundamentais Coletados
| Métrica | Valor | Descrição |
|---|---|---|
| ticker | WEGE3.SA | - |
| cotacao | 51.7300 | - |
| market_cap | 217043353600 | - |
| lpa_yahoo | 1.5500 | - |
| vpa_yahoo | 5.3410 | - |
| div_12m | 2.4506 | - |
| dy_anual | 0.0474 | - |
| pl | 33.3742 | - |
| pvp | 9.6855 | - |
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
| riscos_citados | 1. Risco tributário de R$ 911,3 milhões referente a autuações da Receita Federal sobre lucros auferidos no exterior (contingência possível). 2. Contingências cíveis que totalizam R$ 322,8 milhões, incluindo disputas relevantes com a Mapfre Seguros Gerais S.A. (R$ 119,2 milhões). | - |
| moat_score | 9 | - |
| moat_justificativa | A WEG demonstra um fosso econômico (Moat) excepcional, sustentado por um ROIC de 32,4%, significativamente superior ao seu custo de capital. A companhia possui alta eficiência operacional através da verticalização e diversificação global, o que permite flexibilidade produtiva para mitigar riscos geopolíticos. O investimento constante em P&D (3,5% da receita) e a liderança em soluções para a transição energética (T&D e Mobilidade Elétrica) garantem barreiras de entrada tecnológicas e escala competitiva. | - |


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
- Peso Dívida (Wd): 2.08%
- Peso Equity (We): 97.92%
- Custo Dívida Nominal: 12.00%
- Tax Rate Efetiva: 34.00%
- **WACC Final:** 19.74%

## 3. Rastreabilidade do Valuation (DCF)

**Valor Justo Final:** R$ 21.18
**Premissas Usadas:** {'WACC': '19.7%', 'Cresc.': '15.7%'}

### Auditoria Monte Carlo
Resultados Estatísticos:
{
  "Mean": 21.49,
  "Median": 21.19,
  "VaR_5_Percent": 16.21,
  "Upside_95_Percent": 28.02,
  "Std_Dev": 3.79,
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
        - Cotação: R$ 51.73 | Market Cap: R$ 217.04B
        - Perfil Estratégico: GROWTH / COMPOUNDER (Alta Qualidade) [Wide Moat] [Macro Headwind]
        - ROE: 31.2% | Margem Líq: 15.7%
        - Múltiplos: P/L 33.374195x | EV/EBITDA 24.803x | P/VP 9.6854515x | DY 4.7%
        - Moat Score: 9/10 (A WEG demonstra um fosso econômico (Moat) excepcional, sustentado por um ROIC de 32,4%, significativamente superior ao seu custo de capital. A companhia possui alta eficiência operacional através da verticalização e diversificação global, o que permite flexibilidade produtiva para mitigar riscos geopolíticos. O investimento constante em P&D (3,5% da receita) e a liderança em soluções para a transição energética (T&D e Mobilidade Elétrica) garantem barreiras de entrada tecnológicas e escala competitiva.)

        AUDITORIA & VALUATION:
        1. VALUATION INTRÍNSECO (DCF):
           - Valor Justo (Determinístico): R$ 21.18 (Margem: -59.1%)
           - WACC Usado: 19.7% | Crescimento (g): 15.7%
           - Reverse DCF: O mercado precifica crescimento implícito de 30.7% a.a. (Se aplicável).

        2. SIMULAÇÃO DE MONTE CARLO (PROBABILÍSTICA):
           
            - Preço Médio: R$ 21.49 | Mediana: R$ 21.19
            - Cenário Pessimista (VaR 5%): R$ 16.21
            - Cenário Otimista (95%): R$ 28.02
            - Probabilidade de Upside (vs R$ 51.73): 0.0%
            

        3. VALUATION RELATIVO (PARES):
           - 
            A empresa negocia com DESCONTO de 18.6% no P/L em relação à média do setor.
            Se negociasse no múltiplo médio de P/L dos pares, a ação valeria R$ 63.55.
            
        
        4. AUDITORIA FORENSE (QUALIDADE CONTÁBIL):
           - Score de Qualidade: 10/10
           - Alertas detectados pelo algoritmo:
           Nenhuma anomalia detectada.
           
        5. RISCOS REPORTADOS:
           - 1. Risco tributário de R$ 911,3 milhões referente a autuações da Receita Federal sobre lucros auferidos no exterior (contingência possível). 2. Contingências cíveis que totalizam R$ 322,8 milhões, incluindo disputas relevantes com a Mapfre Seguros Gerais S.A. (R$ 119,2 milhões).

        ESTRUTURA OBRIGATÓRIA DO MEMORANDO:
        ## 1. Executive Summary & Veredito
        Comece com a conclusão. COMPRA (Buy), MANTER (Hold) ou VENDA (Sell). Defina o "Target Price" (use o DCF como base, ajustado pelo seu julgamento qualitativo). Resuma a tese em 3 bullets matadores.

        ## 2. A Tese Micro vs. O Cenário Macro
        Como essa empresa navega o ciclo atual (Selic 15.0% | IPCA 4.26% | Juro Real 10.30% | Ciclo: CONTRACIONISTA (Aperto Monetário))? A inflação/juros ajudam ou atrapalham?
        
        ## 3. Qualidade & Fosso (The Moat)
        O Moat é durável? A empresa tem poder de preço? Analise o ROE vs Custo de Capital.

        ## 4. Valuation Intrínseco & Cenários
        Discuta o Valor Justo do DCF (21.18) e compare com os múltiplos.
        ANÁLISE DE SENSIBILIDADE (Stress Test):
        - O modelo indica um range de valor entre R$ 18.10 (Cenário Pessimista) e R$ 25.02 (Cenário Otimista).
        - Com base nisso, quão segura é a Margem de Segurança atual?
        *Comente explicitamente sobre os alertas da Auditoria Forense se houverem.*

        ## 5. Riscos do "Bear Case"
        O que pode destruir essa tese? (Regulação, concorrência, ciclo, fraude contábil). Seja brutal.

        TOM DE VOZ:
        Direto, analítico, sofisticado. Evite clichês ("empresa sólida"). Use dados para suportar adjetivos.
        
```

### Resposta Recebida (Raw)
**PARA:** Comitê de Investimentos (Global Multi-Strategy Fund)
**DE:** Sócio Sênior de Equities
**DATA:** 23 de Maio de 2024
**ASSUNTO:** MEMORANDO DE INVESTIMENTO: WEGE3.SA (WEG S.A.) – A Inexorável Gravidade dos Juros Reais

---

## 1. Executive Summary & Veredito

**VEREDITO: VENDA (SELL)**
**Target Price (12m):** R$ 26.50 (Baseado em DCF ajustado e prêmio de qualidade)
**Upside/Downside:** -48.8%

A WEG é, indiscutivelmente, a melhor operação industrial da América Latina e uma das mais eficientes do globo. No entanto, o papel do gestor de fundos multi-estratégia não é colecionar troféus operacionais, mas arbitrar a diferença entre valor e preço. A R$ 51.73, a WEG está precificada para um cenário de ficção científica macroeconômica.

**Key Takeaways:**
*   **Abismo entre Valor e Preço:** O valor intrínseco (DCF) de R$ 21.18 aponta para uma sobrevalorização severa, ignorando o impacto de um custo de capital (WACC) de 19.7%.
*   **A Tirania do Juro Real:** Com juros reais em 10.30%, o custo de oportunidade para carregar uma tese de *growth* com P/L de 33x é proibitivo.
*   **Exaustão do Crescimento:** O mercado exige um crescimento implícito de 30.7% a.a. para justificar o preço atual. Historicamente, manter esse ritmo em escala global é uma anomalia estatística.

---

## 2. A Tese Micro vs. O Cenário Macro

O mercado brasileiro vive um ciclo **CONTRACIONISTA** severo. Com Selic a 15.0% e IPCA a 4.26%, o Juro Real de 10.30% atua como uma força gravitacional que deveria achatar múltiplos de *duration* longa.

*   **O Paradoxo da WEG:** A empresa é um *proxy* global de crescimento (T&D, Transição Energética), mas está listada em um mercado onde o capital é extremamente caro. 
*   **Impacto no Fluxo de Caixa:** Embora a WEG possua baixa alavancagem financeira, o cenário contracionista reduz o CAPEX industrial de seus clientes domésticos. A tese de que a receita externa (diversificação global) isola a WEG do Brasil é parcialmente verdadeira, mas o *valuation* é feito em BRL sob a taxa de desconto local. A 10.3% de juro real, o "fluxo de caixa de amanhã" vale quase nada hoje. Valorizamos fluxo de caixa presente, e a WEG negocia a um prêmio de crescimento futuro que o macro atual não permite suportar.

---

## 3. Qualidade & Fosso (The Moat)

O *Moat* da WEG é real, profundo e sustentado por *First Principles*:
1.  **Verticalização:** A WEG não é apenas uma montadora; ela produz desde as tintas até os componentes eletrônicos. Isso garante uma margem líquida de 15.7%, resiliente mesmo em choques de cadeia de suprimentos.
2.  **ROIC vs. WACC:** O ROIC de 32.4% é excepcional. A empresa cria valor econômico real. 
3.  **Eficiência de P&D:** O investimento de 3.5% da receita em inovação é direcionado para mercados de alta barreira (Mobilidade Elétrica e Eólica), garantindo que a empresa não se torne uma produtora de *commodities* industriais.

**O veredito do fosso:** O fosso existe, mas está sendo vendido pelo mercado como se fosse uma fortaleza inexpugnável a qualquer taxa de juros. Qualidade não é desculpa para ignorar a matemática financeira.

---

## 4. Valuation Intrínseco & Cenários

O mercado está operando em um viés de confirmação perigoso.

*   **Análise DCF:** Nosso modelo determinístico aponta **R$ 21.18**. A discrepância de -59.1% em relação à cotação atual é um alerta vermelho que não pode ser ignorado por um fundo sênior.
*   **Simulação de Monte Carlo:** Mesmo no cenário otimista (95º percentil), o valor justo atinge apenas **R$ 28.02**. Note que a probabilidade estatística de *upside* contra os R$ 51.73 atuais é de **0.0%**.
*   **Reverse DCF:** Para sustentar o preço atual, a WEG precisaria crescer 30.7% ao ano perpetuamente em um cenário onde o PIB global luta para crescer 3%. É uma aposta em execução perfeita em um ambiente de incerteza geopolítica.
*   **Auditoria Forense:** Score 10/10. Não há "esqueletos". O risco não é contábil, é puramente de **Preço**.

*Observação sobre o Valuation Relativo:* Embora negocie com desconto de 18.6% frente aos pares globais (como ABB, Siemens), essa métrica é enganosa. Os pares globais operam em mercados com taxas de desconto de 4% a 6%, não 19.7%. O "desconto" é uma ilusão de ótica macroeconômica.

---

## 5. Riscos do "Bear Case" (O que pode dar errado?)

Como céticos, devemos olhar para o que o mercado ignora:

1.  **De-rating Agressivo:** Se o mercado parar de precificar a WEG como uma "empresa de tecnologia/crescimento" e passar a vê-la como uma "industrial cíclica", o P/L pode convergir para 15x rapidamente. Isso destruiria 50% do valor de mercado sem que a empresa tenha um único trimestre de prejuízo.
2.  **Risco Tributário:** As autuações de R$ 911,3 milhões sobre lucros no exterior são um risco de cauda. Em um cenário de aperto de liquidez, uma saída de caixa dessa magnitude impactaria o dividend yield, hoje já baixo (4.7%).
3.  **Substituição Tecnológica:** O mercado chinês está despejando motores elétricos e soluções de T&D com subsídios estatais agressivos. O *pricing power* da WEG pode ser testado de forma inédita nos próximos 36 meses.

## Conclusão Final

A WEG é uma empresa 10/10 sendo negociada a um preço 2/10 em termos de margem de segurança. No portfólio deste fundo, priorizamos a preservação de capital e o carrego eficiente. Manter WEGE3 aos preços atuais é ignorar a gravidade dos juros reais de 10%. Recomendamos a **liquidação da posição** ou a montagem de um *hedge* tático via opções de venda (PUTs).

**Sócio Sênior de Equities**
*Global Multi-Strategy Fund*