import json
import os
from google import genai
from google.genai import types
import config  # Importa do arquivo config.py na raiz

class AgenteIA:
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            print("AVISO: API Key não configurada. IA inativa.")
            self.client = None
        else:
            self.client = genai.Client(api_key=config.GOOGLE_API_KEY)
            
    def extrair_dados_pdf(self, texto_pdf: str, nome_empresa: str) -> dict:
        if not self.client or not texto_pdf: return {}
        
        print("   -> [IA] Auditando Dívida e Riscos via PDF...")
        prompt = f"""
        Você é um Auditor Financeiro Sênior. Analise o relatório da {nome_empresa}.
        
        EXTRAÇÃO DE DADOS (Seja conservador):
        1. **Dívida Líquida (Net Debt):** Valor total. Atenção à escala (Milhões vs Bilhões).
        2. **Riscos:** Cite 2 riscos operacionais ou de mercado principais.
        3. **Moat (Vantagem Competitiva):** Identifique se há menção a patentes, custo de troca alto, efeito de rede ou marca forte.
        
        JSON (Responda APENAS o JSON):
        {{
            "divida_liquida_total_reais": float (Valor numérico absoluto ex: 1500000000.00),
            "escala_identificada": "string (ex: Milhões)",
            "riscos_citados": "string resumida",
            "moat_score": int (0 a 10, onde 10 é monopólio e 0 é commodity sem diferencial),
            "moat_justificativa": "string breve"
        }}
        
        TEXTO:
        {texto_pdf[:60000]}
        """
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            # Limpeza
            return json.loads(response.text.strip())
        except Exception as e: 
            print(f"Erro na extração IA: {e}")
            return {}

    def gerar_parecer_final(self, dados: dict, valuation: dict, comparables: dict, perfil: str) -> str:
        if not self.client: return "Parecer indisponível (Sem API Key)."
        
        dcf = valuation.get('DCF_Adaptativo', {})
        rev_dcf = valuation.get('Reverse_DCF', {})
        
        # Prepara texto dos comparables
        texto_comps = "Análise de Pares não disponível."
        if comparables:
            premio = comparables['premio_pl']
            texto_comps = f"A empresa negocia com um {'PRÊMIO' if premio > 0 else 'DESCONTO'} de {abs(premio):.1%} no P/L em relação aos pares: {', '.join(comparables['pares_usados'])}."

        prompt = f"""
        Atue como um Gestor de Portfólio Institucional (Buy Side). Escreva uma tese concisa sobre {dados.get('ticker')}.
        
        DADOS ESTRATÉGICOS:
        - Perfil: {perfil}
        - ROE: {dados.get('roe'):.1%}
        - Moat Score (Qualidade): {dados.get('moat_score', 'N/A')}/10
        
        VALUATION:
        1. DCF Tradicional: Valor Justo R$ {dcf.get('Valor')} (Margem: {dcf.get('Margem')}%)
        2. Reverse DCF (Expectativa do Mercado): O preço atual exige um crescimento implícito de {rev_dcf.get('Implied_Growth', 0):.1%} a.a. Analise se isso é factível para este setor.
        
        RELATIVO:
        {texto_comps}
        
        CONCLUSÃO:
        Dê um veredito claro (COMPRA, MANTER, VENDA) justificando com a assimetria (Valuation) e a qualidade (Moat/Comparables).
        """
        
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Erro ao gerar parecer: {e}"