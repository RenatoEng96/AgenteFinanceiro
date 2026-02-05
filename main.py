import os
from src.data import obter_dados_yahoo, ler_pdf_local
from src.strategy import Estrategista
from src.valuation import ValuationEngine
from src.comparables import AnalistaRelativo
from src.ai_agent import AgenteIA
from src.report import gerar_pdf_v11

def main():
    print("\n--- 🤖 AGENTE FINANCEIRO V11 (MODULAR) ---\n")
    ticker = input("Ticker (ex: WEGE3, PETR4): ").strip().upper() or "WEGE3"
    
    # 1. Instancia Agentes
    agente_ia = AgenteIA()

    # 2. Coleta de Dados Básicos
    dados = obter_dados_yahoo(ticker)
    if not dados: return
    
    # 3. Processamento de PDF (Opcional)
    print("\nCaminho do PDF (Enter para pular):")
    path_pdf = input(">> ").strip()
    if path_pdf and os.path.exists(path_pdf):
        texto = ler_pdf_local(path_pdf)
        if texto:
            # IA extrai dívida auditada e Moat Score
            dados_pdf = agente_ia.extrair_dados_pdf(texto, dados['nome'])
            if dados_pdf: dados.update(dados_pdf)

    # 4. Definição de Estratégia
    estrategista = Estrategista(dados)
    perfil, params = estrategista.definir_cenario()
    print(f"\n[ESTRATÉGIA] Perfil: {perfil}")

    # 5. Valuation Engine (Matemática)
    engine = ValuationEngine(dados, params)
    res_valuation = engine.run()
    
    # Exibe resumo do Reverse DCF no console
    rev = res_valuation.get('Reverse_DCF', {})
    print(f"   [REVERSE DCF] Mercado precifica crescimento de {rev.get('Implied_Growth', 0):.1%} a.a.")

    # 6. Comparables (Análise Relativa)
    analista_rel = AnalistaRelativo(dados['ticker'], dados['setor'], dados)
    res_comparables = analista_rel.executar_analise()

    # 7. Geração de Parecer (IA) e PDF
    print("\n--- Gerando Tese de Investimento ---")
    parecer = agente_ia.gerar_parecer_final(dados, res_valuation, res_comparables, perfil)
    
    print("\n" + parecer)
    
    gerar_pdf_v11(dados, res_valuation, res_comparables, parecer, perfil)

if __name__ == "__main__":
    main()