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
        Foca em Notas Explicativas, Endividamento Real e Vantagens Competitivas.
        """
        if not self.client or not texto_pdf: return {}
        
        print("   -> [IA] Auditando documento completo (Deep Reading)...")
        
        # Prompt Otimizado para Contexto Longo
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
            "escala_identificada": "string (ex: 'R$ Milhares' ou 'R$ Milhões')",
            "riscos_citados": "string (Resumo curto dos riscos reais encontrados)",
            "moat_score": int,
            "moat_justificativa": "string (Baseada em evidências do texto)"
        }}
        
        DOCUMENTO COMPLETO:
        {texto_pdf}
        """
        
        try:
            # Atenção: Chamada padrão (não-streaming) para garantir JSON válido no final
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 # Temperatura baixa para precisão numérica máxima
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
        
        # Formata Comparables
        texto_comps = "N/A"
        if comparables:
            premio = comparables.get('premio_pl', 0)
            texto_comps = f"Negocia com {'PRÊMIO' if premio > 0 else 'DESCONTO'} de {abs(premio):.1%} vs pares."

        prompt = f"""
        Escreva um MEMORANDO DE INVESTIMENTO PROFISSIONAL (Hedge Fund Style) sobre {dados.get('ticker')}.
        
        CONTEXTO ESTRATÉGICO:
        - Empresa: {dados.get('nome')}
        - Perfil: {perfil}
        - Moat Score: {dados.get('moat_score', 'N/A')}/10 ({moat_txt})
        
        VALUATION & NUMBERS:
        - Preço Tela: R$ {dados.get('cotacao')}
        - Valor Justo (DCF): R$ {dcf.get('Valor')} (Upside: {dcf.get('Margem')}%)
        - Expectativa Implícita (Reverse DCF): Mercado precifica crescimento de {rev_dcf.get('Implied_Growth', 0):.1%} a.a.
        - Relativo: {texto_comps}
        
        RISCOS AUDITADOS (Do PDF Completo):
        - {riscos}
        
        ESTRUTURA DO PARECER:
        1. **Tese de Investimento:** Por que ter (ou não) esse papel? Use os dados do Moat.
        2. **Análise de Valor:** O DCF e os Múltiplos conversam? O mercado está racional?
        3. **Fatores de Risco:** Comente os riscos extraídos do PDF.
        4. **Veredito Final:** (COMPRA FORTE / COMPRA / MANTER / VENDA).
        """
        
        try:
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Erro ao gerar parecer: {e}"