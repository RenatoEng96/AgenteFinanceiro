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

    def gerar_parecer_final(self, dados: dict, valuation: dict, comparables: dict, perfil: str) -> str:
        if not self.client: return "Parecer indisponível (Sem API Key)."
        
        dcf = valuation.get('DCF_Adaptativo', {})
        rev_dcf = valuation.get('Reverse_DCF', {})
        moat_txt = dados.get('moat_justificativa', 'N/A')
        riscos = dados.get('riscos_citados', 'N/A')
        
        # Formata Comparables com dados novos
        texto_comps = "Dados de pares insuficientes."
        if comparables:
            desc_pl = comparables.get('desconto_pl', 0)
            desc_ev = comparables.get('desconto_evebitda', 0)
            implied_pl = comparables['precos_implicitos'].get('Target_PL', 0)
            
            status_pl = "DESCONTO" if desc_pl < 0 else "PRÊMIO"
            texto_comps = f"""
            A empresa negocia com {status_pl} de {abs(desc_pl):.1%} no P/L em relação à média do setor.
            Se negociasse no múltiplo médio de P/L dos pares, a ação valeria R$ {implied_pl:.2f}.
            """

        prompt = f"""
        Escreva um MEMORANDO DE INVESTIMENTO PROFISSIONAL (Hedge Fund Style - Longo e Detalhado) sobre {dados.get('ticker')}.
        Seja extremamente rigoroso na matemática. Use termos técnicos (Upside, CAGR, WACC, Moat).
        
        CONTEXTO ESTRATÉGICO:
        - Empresa: {dados.get('nome')}
        - Perfil: {perfil}
        - Moat Score: {dados.get('moat_score', 'N/A')}/10 ({moat_txt})
        
        1. ANÁLISE INTRÍNSECA (DCF & Modelos Absolutos):
        - Preço Tela: R$ {dados.get('cotacao')}
        - Valor Justo (DCF): R$ {dcf.get('Valor')} (Margem: {dcf.get('Margem')}%)
        - Premissas do DCF: WACC de {dcf.get('Premissas', {}).get('WACC')} e Crescimento (g) de {dcf.get('Premissas', {}).get('Cresc.')}.
        - Expectativa Implícita (Reverse DCF): O mercado precifica um crescimento de {rev_dcf.get('Implied_Growth', 0):.1%} a.a. para justificar o preço atual.
        
        2. ANÁLISE RELATIVA (Múltiplos de Mercado):
        - {texto_comps}
        - Compare a qualidade da empresa (ROE: {dados.get('roe'):.1%}) com a média do setor. Se o ROE for maior e o P/L menor, destaque a ASSIMETRIA CLARA.
        
        3. RISCOS AUDITADOS (Forensics):
        - {riscos}
        
        ESTRUTURA OBRIGATÓRIA DO MEMORANDO:
        ## 1. Tese de Investimento (The Pitch)
        Explique o racional qualitativo e quantitativo. Relacione o Moat Score com a capacidade de gerar caixa.
        
        ## 2. Valuation: O Confronto de Modelos
        Discuta a discrepância entre o DCF (Valor Intrínseco) e os Múltiplos (Valor Relativo). Qual modelo devemos confiar mais neste caso dado o perfil da empresa?
        
        ## 3. Análise de Riscos (The Bear Case)
        Não seja superficial. Analise os riscos citados e o impacto no WACC.
        
        ## 4. Veredito e Recomendação
        Defina claramente: COMPRA (Buy), MANTER (Hold) ou VENDA (Sell). Justifique com a Margem de Segurança.
        """
        
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Erro ao gerar parecer: {e}"