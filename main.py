import os
from src.data import obter_dados_yahoo, ler_pdf_local, validar_dados_interativo
from src.strategy import Estrategista
from src.valuation import ValuationEngine
from src.comparables import AnalistaRelativo
from src.ai_agent import AgenteIA
from src.report import gerar_pdf_v11
from src.memorial import MemorialLog

"""
Módulo Principal (Orquestrador) - Agente Financeiro V12
-------------------------------------------------------
Este arquivo é o ponto de entrada da aplicação. Ele coordena o fluxo de execução entre
os diversos agentes especializados (Data, Strategy, Valuation, AI, Report).

Fluxo de Execução:
1. Coleta de Dados (Yahoo Finance).
2. Leitura de Relatórios em PDF (Opcional).
3. Validação Interativa dos Dados (Human-in-the-loop).
4. Definição de Estratégia de Valuation (Growth vs Value vs Commodity).
5. Execução dos Motores de Valuation (DCF, Graham, Bazin, etc.).
6. Análise Relativa (Comparação com pares do setor).
7. Geração da Tese de Investimento via IA (Google Gemini).
8. Geração do Relatório PDF Final.
"""

def main():
    """
    Função principal que orquestra todo o processo de análise.
    Não recebe argumentos via CLI, mas solicita input interativo do usuário.
    """
    print("\n--- AGENTE FINANCEIRO V12 (RIGOROSO) ---\n")
    ticker = input("Ticker (ex: WEGE3, PETR4): ").strip().upper() or "WEGE3"
    
    # 0. Instancia Memorial de Auditoria
    memorial = MemorialLog(ticker)
    
    # 1. Instancia Agentes
    agente_ia = AgenteIA()

    # 2. Coleta de Dados Básicos
    dados = obter_dados_yahoo(ticker)
    if not dados: 
        print("Erro crítico: Dados não encontrados.")
        return
    memorial.register_data('dados_yahoo', dados)
    
    # 3. Processamento de PDF (Opcional)
    print("\nCaminho do PDF (Enter para pular):")
    path_pdf = input(">> ").strip()
    if path_pdf:
        # Remove aspas se o usuário copiou o caminho como "C:\..."
        path_pdf = path_pdf.replace('"', '').replace("'", "")
        if os.path.exists(path_pdf):
            texto = ler_pdf_local(path_pdf)
            if texto:
                # IA extrai dívida auditada e Moat Score
                dados_pdf = agente_ia.extrair_dados_pdf(texto, dados['nome'])
                if dados_pdf: 
                    print("\n[IA AUDITORIA] Dados Extraídos do PDF:")
                    print(f"   > Dívida Líq. Ajustada: R$ {dados_pdf.get('divida_liquida_total_reais', 'N/A')}")
                    print(f"   > Moat Score: {dados_pdf.get('moat_score', 'N/A')}")
                    dados.update(dados_pdf)
        else:
            print("Aviso: Arquivo PDF não encontrado. Seguindo sem auditoria.")

    # 3.1 Validação Interativa (Human-in-the-loop)
    # Garante que dados críticos (como FCFF ou Beta) não sejam zero/None
    dados = validar_dados_interativo(dados)
    
    # 4. Definição de Estratégia
    estrategista = Estrategista(dados)
    perfil, params = estrategista.definir_cenario()
    print(f"\n[ESTRATÉGIA] Perfil: {perfil}")
    memorial.register_data('params_estrategia', params)

    # 5. Valuation Engine (Matemática)
    engine = ValuationEngine(dados, params)
    res_valuation = engine.run()
    memorial.register_data('valuation_results', res_valuation)
    
    # Exibe resumo do Reverse DCF no console
    rev = res_valuation.get('Reverse_DCF', {})
    if rev:
        print(f"   [REVERSE DCF] Mercado precifica crescimento de {rev.get('Implied_Growth', 0):.1%} a.a.")

    # 6. Comparables (Análise Relativa Profunda)
    analista_rel = AnalistaRelativo(dados['ticker'], dados['setor'], dados)
    res_comparables = analista_rel.executar_analise()
    
    if res_comparables:
        precos = res_comparables.get('precos_implicitos', {})
        print(f"   [RELATIVO] Preço Implícito (P/L): R$ {precos.get('Target_PL', 0):.2f}")

    # 7. Geração de Parecer (IA) e PDF
    print("\n--- Gerando Tese de Investimento Detalhada (Hedge Fund Style) ---")
    
    parecer_texto, prompt_usado = agente_ia.gerar_parecer_final(dados, res_valuation, res_comparables, perfil, params)
    memorial.register_data('llm_prompt', prompt_usado)
    memorial.register_data('llm_response', parecer_texto)
    
    print("\n" + parecer_texto)
    
    gerar_pdf_v11(dados, res_valuation, res_comparables, parecer_texto, perfil)
    memorial.salvar()

if __name__ == "__main__":
    main()