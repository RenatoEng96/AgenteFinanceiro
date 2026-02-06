import json
import os
from google import genai
from google.genai import types
import config

class AgenteIA:
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            print("AVISO: API Key não configurada. IA inativa.")
            self.client = None
        else:
            self.client = genai.Client(api_key=config.GOOGLE_API_KEY)
            
    def extrair_dados_pdf(self, texto_pdf: str, nome_empresa: str) -> dict:
        """
        Analisa o RELATÓRIO COMPLETO (100% das páginas).
        """
        if not self.client or not texto_pdf: return {}
        
        print("   -> [IA] Auditando documento completo (Deep Reading)...")
        
        prompt = f"""
        Você é um Analista de Equity Research Sênior especializado em Auditoria Contábil.
        Você recebeu o TEXTO COMPLETO do relatório da {nome_empresa}.
        
        SUA MISSÃO:
        Cruzar os dados do Balanço/DRE com as NOTAS EXPLICATIVAS para encontrar a verdade econômica.
        
        1. **Dívida Líquida Ajustada:**
           - Procure na seção de "Endividamento" ou Notas Explicativas.
           - Some empréstimos, debêntures e financiamentos (Curto + Longo Prazo).
           - Subtraia o Caixa e Equivalentes.
           - ATENÇÃO À ESCALA: O relatório está em Milhares ou Milhões? Converta para o valor Real Absoluto (ex: 5.4 Bilhões = 5400000000).
        
        2. **Riscos e Processos (Auditoria Forense):**
           - Varra o texto por "Processos Judiciais", "Contingências", "Risco Regulatório".
           - Cite os 2 riscos mais graves mencionados pela administração ou auditoria.
        
        3. **Qualidade & Moat (Fosso Econômico):**
           - Baseado na "Mensagem da Administração" e visão estratégica.
           - Score de 0 a 10.
        
        OUTPUT JSON OBRIGATÓRIO:
        {{
            "divida_liquida_total_reais": float,
            "escala_identificada": "string",
            "riscos_citados": "string",
            "moat_score": int,
            "moat_justificativa": "string"
        }}
        
        DOCUMENTO COMPLETO:
        {texto_pdf}
        """
        
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            return json.loads(response.text.strip())
        except Exception as e: 
            print(f"   [IA ERRO] Falha na extração: {e}")
            return {}

    def gerar_parecer_final(self, dados: dict, valuation: dict, comparables: dict, perfil: str, params: dict = None) -> str:
        if not self.client: return "Parecer indisponível (Sem API Key)."
        
        dcf = valuation.get('DCF_Adaptativo', {})
        rev_dcf = valuation.get('Reverse_DCF', {})
        forensic = valuation.get('Forensic', {})
        
        # Extração de Contexto Macro
        macro_text = "Cenário não informado."
        if params and 'capm_data' in params:
            m = params['capm_data'].get('contexto_macro', {})
            macro_text = f"Selic {m.get('selic')}% | IPCA {m.get('ipca')}% | Juro Real {m.get('juro_real'):.2f}% | Ciclo: {m.get('ciclo')}"
        
        # Extração de Forensic
        forensic_text = "Nenhuma anomalia detectada."
        if forensic and forensic.get('Flags'):
            forensic_text = "\n".join([f"- {flag}" for flag in forensic['Flags']])
        
        moat_txt = dados.get('moat_justificativa', 'N/A')
        riscos = dados.get('riscos_citados', 'N/A')
        
        # Extração de Sensibilidade (Min/Max)
        sensibilidade = valuation.get('Sensibilidade', {})
        min_val = 0
        max_val = 0
        if sensibilidade and sensibilidade.get('Matriz'):
            flat_list = [item for sublist in sensibilidade['Matriz'] for item in sublist]
            min_val = min(flat_list)
            max_val = max(flat_list)
        
        # Formata Comparables com dados novos
        texto_comps = "Dados de pares insuficientes."
        if comparables:
            desc_pl = comparables.get('desconto_pl', 0)
            implied_pl = comparables['precos_implicitos'].get('Target_PL', 0)
            status_pl = "DESCONTO" if desc_pl < 0 else "PRÊMIO"
            texto_comps = f"""
            A empresa negocia com {status_pl} de {abs(desc_pl):.1%} no P/L em relação à média do setor.
            Se negociasse no múltiplo médio de P/L dos pares, a ação valeria R$ {implied_pl:.2f}.
            """

        # Extração de Monte Carlo
        monte_carlo = valuation.get('Monte_Carlo', {})
        mc_text = "Simulação não realizada."
        if 'Mean' in monte_carlo:
            mc_text = f"""
            - Preço Médio: R$ {monte_carlo['Mean']} | Mediana: R$ {monte_carlo['Median']}
            - Cenário Pessimista (VaR 5%): R$ {monte_carlo['VaR_5_Percent']}
            - Cenário Otimista (95%): R$ {monte_carlo['Upside_95_Percent']}
            - Probabilidade de Upside (vs R$ {dados.get('cotacao')}): {monte_carlo['Upside_Prob']}
            """
        elif 'Status' in monte_carlo:
            mc_text = f"Simulação abortada: {monte_carlo['Status']}"

        prompt = f"""
        Atue como um SÓCIO SÊNIOR de um Fundo Multi-Estratégia Global. Escreva um MEMORANDO DE INVESTIMENTO de alta convicção sobre {dados.get('ticker')}.
        
        MINDSET:
        - Use "First Principles Thinking": Questione os consensos. Por que a empresa lucra? O fosso é real?
        - Seja Cético: Assuma que o mercado é eficiente, a menos que provado o contrário.
        - Macro-Aware: Conecte o ciclo econômico (Juro Real, Inflação) com a tese micro.
        
        CONTEXTO ECONÔMICO (MACRO):
        {macro_text}
        -> Se o Ciclo for CONTRACIONISTA (Juro Real alto), penalize teses de crescimento longo e valorize fluxo de caixa hoje.
        -> Se o Ciclo for EXPANSIONISTA, valorize duration e crescimento.

        DADOS DA EMPRESA:
        - Ticker: {dados.get('ticker')} ({dados.get('nome')})
        - Cotação: R$ {dados.get('cotacao')} | Market Cap: R$ {dados.get('market_cap', 0)/1e9:.2f}B
        - Perfil Estratégico: {perfil}
        - ROE: {dados.get('roe'):.1%} | Margem Líq: {dados.get('margem_liq', 0):.1%}
        - Múltiplos: P/L {dados.get('pl')}x | EV/EBITDA {dados.get('ev_ebitda')}x | P/VP {dados.get('pvp')}x | DY {dados.get('dy_anual'):.1%}
        - Moat Score: {dados.get('moat_score', 'N/A')}/10 ({moat_txt})

        AUDITORIA & VALUATION:
        1. VALUATION INTRÍNSECO (DCF):
           - Valor Justo (Determinístico): R$ {dcf.get('Valor')} (Margem: {dcf.get('Margem')}%)
           - WACC Usado: {dcf.get('Premissas', {}).get('WACC')} | Crescimento (g): {dcf.get('Premissas', {}).get('Cresc.')}
           - Reverse DCF: O mercado precifica crescimento implícito de {rev_dcf.get('Implied_Growth', 0):.1%} a.a. (Se aplicável).

        2. SIMULAÇÃO DE MONTE CARLO (PROBABILÍSTICA):
           {mc_text}

        3. VALUATION RELATIVO (PARES):
           - {texto_comps}
        
        4. AUDITORIA FORENSE (QUALIDADE CONTÁBIL):
           - Score de Qualidade: {forensic.get('Score', 10)}/10
           - Alertas detectados pelo algoritmo:
           {forensic_text}
           
        5. RISCOS REPORTADOS:
           - {riscos}

        ESTRUTURA OBRIGATÓRIA DO MEMORANDO:
        ## 1. Executive Summary & Veredito
        Comece com a conclusão. COMPRA (Buy), MANTER (Hold) ou VENDA (Sell). Defina o "Target Price" (use o DCF como base, ajustado pelo seu julgamento qualitativo). Resuma a tese em 3 bullets matadores.

        ## 2. A Tese Micro vs. O Cenário Macro
        Como essa empresa navega o ciclo atual ({macro_text})? A inflação/juros ajudam ou atrapalham?
        
        ## 3. Qualidade & Fosso (The Moat)
        O Moat é durável? A empresa tem poder de preço? Analise o ROE vs Custo de Capital.

        ## 4. Valuation Intrínseco & Cenários
        Discuta o Valor Justo do DCF ({dcf.get('Valor')}) e compare com os múltiplos.
        ANÁLISE DE SENSIBILIDADE (Stress Test):
        - O modelo indica um range de valor entre R$ {min_val:.2f} (Cenário Pessimista) e R$ {max_val:.2f} (Cenário Otimista).
        - Com base nisso, quão segura é a Margem de Segurança atual?
        *Comente explicitamente sobre os alertas da Auditoria Forense se houverem.*

        ## 5. Riscos do "Bear Case"
        O que pode destruir essa tese? (Regulação, concorrência, ciclo, fraude contábil). Seja brutal.

        TOM DE VOZ:
        Direto, analítico, sofisticado. Evite clichês ("empresa sólida"). Use dados para suportar adjetivos.
        """
        
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt
            )
            return response.text, prompt
        except Exception as e:
            return f"Erro ao gerar parecer: {e}", prompt