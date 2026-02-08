import os
import yfinance as yf
import pypdf
import re

def obter_dados_yahoo(ticker: str) -> dict:
    """
    Coleta dados fundamentais robustos do Yahoo Finance via biblioteca yfinance.
    
    Args:
        ticker (str): Código da ação (ex: 'WEGE3', 'PETR4').
        
    Returns:
        dict: Dicionário contendo dados financeiros normalizados, incluindo:
            - Estrutura de Capital (Dívida, Caixa).
            - Múltiplos (P/L, EV/EBITDA, P/VP).
            - Rentabilidade (ROE, Margens).
            - Dados calculados (WACC inputs, FCFF estimado).
            
    Tratamento de Erros:
        - Adiciona sufixo '.SA' automaticamente se omitido.
        - Usa valores fallback sensatos para dados faltantes (ex: Tax Rate 34%).
    """
    if not ticker.endswith(".SA") and not ticker.startswith("^"): 
        ticker = f"{ticker}.SA"
    
    print(f"   -> [Data] Coletando dados fundamentais para {ticker}...")
    try:
        acao = yf.Ticker(ticker)
        info = acao.info
        
        # Estrutura de Capital
        total_debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        net_debt = total_debt - cash
        shares = info.get('sharesOutstanding', 1) or 1
        net_debt_per_share = net_debt / shares

        # Dados para WACC
        market_cap = info.get('marketCap', 0)
        interest_expense = info.get('interestExpense', 0) # Despesa financeira (geralmente negativa no yahoo)
        pre_tax_income = info.get('preTaxIncome', 0)
        tax_provision = info.get('taxProvision', 0)
        
        # 1. Taxa de Imposto Efetiva (Tax Rate)
        # Se não houver dados, assume 34% (padrão Brasil)
        tax_rate = 0.34
        if pre_tax_income and pre_tax_income != 0 and tax_provision:
            calc_tax = tax_provision / pre_tax_income
            # Limita entre 0% e 45% para evitar distorções de anos atípicos
            if 0 < calc_tax < 0.45:
                tax_rate = calc_tax
        
        # 2. Custo da Dívida (Kd)
        # Estimation: Interest Expense / Total Debt
        # Se expense vier negativo, inverte sinal.
        cost_of_debt = 0.12 # Fallback conservador (12% a.a)
        if total_debt > 0 and interest_expense:
             # Interest expense costuma vir negativo ou positivo dependendo da versao do yahoo. 
             # Garantimos valor absoluto.
             kd_calc = abs(interest_expense) / total_debt
             # Filtro de sanidade: Kd entre 1% e 30%
             if 0.01 < kd_calc < 0.30:
                 cost_of_debt = kd_calc

        # Fluxo de Caixa (FCFF Estimado)
        ocf = info.get('operatingCashflow', 0)
        capex = info.get('capitalExpenditures', 0)
        
        # Tratamento de Nones
        if ocf is None: ocf = 0
        if capex is None: capex = 0
        
        # Cálculo FCFF
        # Se Capex for negativo (saída), soma-se algebricamente. 
        # Se for positivo (erro de sinal do yahoo), subtrai-se.
        if capex > 0:
            fcff = ocf - capex
        else:
            fcff = ocf + capex
            
        # Fallback se o cálculo manual falhar ou der zero
        if fcff == 0:
            fcff = info.get('freeCashflow', 0)

        fcff_per_share = fcff / shares if fcff else 0

        # Dividendos
        try:
            hist = acao.history(period="1y")
            div_12m = hist['Dividends'].sum() if not hist.empty else 0.0
        except: div_12m = 0.0

        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
        dy = (div_12m / price) if price > 0 else 0.0
        
        # ROE Seguro
        roe = info.get('returnOnEquity')
        if roe is None: roe = 0.10

        # Beta Seguro
        beta_raw = info.get('beta', 1.0)
        if beta_raw is None: beta_raw = 1.0

        return {
            "ticker": ticker,
            "cotacao": price,
            "market_cap": market_cap,
            "lpa_yahoo": info.get('trailingEps'), 
            "vpa_yahoo": info.get('bookValue'),
            "div_12m": div_12m,
            "dy_anual": dy,
            "pl": info.get('trailingPE'),
            "pvp": info.get('priceToBook'),
            "ev_ebitda": info.get('enterpriseToEbitda'),
            "margem_liq": info.get('profitMargins'),
            "roe": roe,
            "crescimento_receita": info.get('revenueGrowth', 0.05),
            "beta": beta_raw,
            "fcff_por_acao": fcff_per_share,
            "divida_liquida_por_acao": net_debt_per_share,
            "total_acoes": shares,
            "setor": info.get('sector', 'Unknown'),
            "industria": info.get('industry', 'Unknown'),
            "nome": info.get('longName', ticker),
            # Dados Forenses & Valuation Avançado
            "receita_liquida": info.get('totalRevenue', 0),
            "ebitda": info.get('ebitda', 0),
            "lucro_liquido": info.get('netIncomeToCommon', 0),
            "fluxo_caixa_operacional": ocf,
            "divida_total": total_debt,
            "caixa_total": cash,
            "tax_rate_efetiva": tax_rate,
            "custo_divida_bruto": cost_of_debt,
            "despesa_financeira": interest_expense
        }
    except Exception as e:
        print(f"Erro Yahoo ({ticker}): {e}")
        return {}

def ler_pdf_local(caminho: str) -> str:
    """
    Lê partes estratégicas de um PDF local (Relatório Anual/Trimestral).
    
    Estratégia de Leitura "Smart Read":
    - Para economizar tokens da IA e evitar ruído, não lemos o PDF inteiro se for muito grande.
    - Lemos as primeiras 15 páginas (que contêm a Mensagem da Administração e Destaques).
    - Lemos as últimas 10 páginas (que contêm as Demonstrações Financeiras e Notas Explicativas).
    
    Args:
        caminho (str): Caminho absoluto ou relativo para o arquivo PDF.
        
    Returns:
        str: Texto extraído e concatenado das páginas selecionadas. Retorna None se falhar.
    """
    if not caminho: return None
    
    # Tratamento de string do caminho (remove aspas extras que o Windows poe)
    caminho = caminho.strip('"').strip("'")
    
    if not os.path.exists(caminho):
        print(f"   [ERRO] Arquivo não encontrado: {caminho}")
        return None
        
    try:
        print(f"   -> [I/O] Lendo arquivo (Otimizado): {os.path.basename(caminho)}...")
        texto_completo = []
        
        with open(caminho, 'rb') as f:
            pdf = pypdf.PdfReader(f)
            num_paginas = len(pdf.pages)
            print(f"      PDF detectado com {num_paginas} páginas.")
            
            # MELHORIA: Lógica de seleção de páginas estratégicas
            # Lê as primeiras 15 (Contexto, Destaques) e as últimas 10 (Demonstrações, Notas)
            indices_para_ler = list(range(min(15, num_paginas)))
            if num_paginas > 25:
                inicio_final = max(15, num_paginas - 10)
                indices_para_ler += list(range(inicio_final, num_paginas))
            
            # Remove duplicatas e ordena
            indices_para_ler = sorted(list(set(indices_para_ler)))
            print(f"      [Smart Read] Lendo apenas {len(indices_para_ler)} páginas relevantes...")

            for i in indices_para_ler:
                try:
                    page = pdf.pages[i]
                    texto_pag = page.extract_text()
                    if texto_pag:
                        texto_completo.append(f"--- PÁGINA {i+1} ---")
                        texto_completo.append(texto_pag)
                except Exception as ex_pag:
                    print(f"      [Aviso] Erro ao ler pág {i+1}: {ex_pag}")
        
        full_text = "\n".join(texto_completo)
        
        # Limpeza básica para economizar tokens
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        
        print(f"      Leitura concluída. Caracteres extraídos: {len(full_text)}")
        return full_text

    except Exception as e:
        print(f"   [ERRO] Falha ao ler PDF: {e}")
        return None

def validar_dados_interativo(dados: dict) -> dict:
    """
    Realiza uma validação "Human-in-the-loop" dos dados coletados.
    
    Por que isso é necessário?
    APIs financeiras gratuitas (como Yahoo Finance) frequentemente retornam zeros ou Nones
    para dados críticos (ex: Beta, FCFF, Dívida Líquida), o que quebraria os modelos matemáticos.
    
    Esta função verifica chaves críticas e, se suspeitas, pede ao usuário para
    confirmar ou corrigir o valor manualmente no terminal.
    
    Args:
        dados (dict): Dicionário de dados coletados.
        
    Returns:
        dict: Dicionário de dados corrigido/validado.
    """
    print("\n--- VALIDAÇÃO INTERATIVA DE DADOS ---")
    
    # Schema: key -> {metadata}
    schema = {
        'lpa_yahoo': {
            'nome': 'LPA (Lucro por Ação)', 
            'sugestao': 0.0, 
            'motivo': 'Base para Graham e Valuation Relativo.'
        },
        'vpa_yahoo': {
            'nome': 'VPA (Valor Patrimonial por Ação)', 
            'sugestao': 0.0, 
            'motivo': 'Essencial para Graham e Bancos.'
        },
        'fcff_por_acao': {
            'nome': 'FCFF/Ação (Fluxo de Caixa Livre)', 
            'sugestao': 0.0, 
            'motivo': 'Motor principal do DCF. Se 0, valuation falha.'
        },
        'beta': {
            'nome': 'Beta', 
            'sugestao': 1.0, 
            'motivo': 'Mede o risco sistêmico. Média mercado = 1.0.'
        },
        'roe': {
            'nome': 'ROE', 
            'sugestao': 0.15, 
            'motivo': 'Rentabilidade para crescimento sustentável.'
        },
        'cotacao': {
            'nome': 'Cotação Atual',
            'sugestao': 0.0,
            'motivo': 'Necessário para calcular upside/downside.'
        },
        'margem_liq': {
            'nome': 'Margem Líquida',
            'sugestao': 0.10,
            'motivo': 'Indicador de eficiência e qualidade (Forensic).'
        },
        'ebitda': {
            'nome': 'EBITDA',
            'sugestao': 0.0,
            'motivo': 'Proxy de caixa operacional e múltiplos.'
        },
        'lucro_liquido': {
            'nome': 'Lucro Líquido',
            'sugestao': 0.0,
            'motivo': 'Base para cálculo de payout e accruals.'
        },
        'divida_liquida_por_acao': {
            'nome': 'Dívida Líquida/Ação',
            'sugestao': 0.0,
            'motivo': 'Ajuste do Equity Value.'
        }
    }

    mudou_algo = False
    
    for chave, meta in schema.items():
        valor_atual = dados.get(chave)
        
        # Critério de "Falta de Dado": None ou Zero (para campos que não deveriam ser zero)
        # Beta pode ser zero? Raro. Cotação 0? Erro.
        chk_falta = (valor_atual is None) or (isinstance(valor_atual, (int, float)) and valor_atual == 0)
        
        if chk_falta:
            print(f"\n[ATENÇÃO] Dado suspeito: '{meta['nome']}' está {valor_atual}.")
            print(f"   Motivo: {meta['motivo']}")
            print(f"   Sugestão: {meta['sugestao']}")
            
            try:
                inp = input(f"   >> Digite novo valor (ou Enter para manter {valor_atual}): ").strip()
                if inp:
                    # Tenta converter para float (aceita vírgula ou ponto)
                    novo_val = float(inp.replace(',', '.'))
                    dados[chave] = novo_val
                    print(f"      Atualizado para: {novo_val}")
                    mudou_algo = True
                else:
                    print("      Mantido.")
            except ValueError:
                print("      Entrada inválida. Mantido original.")
                
    if mudou_algo:
        print("\n[OK] Dados atualizados manualmente.")
    else:
        print("\n[OK] Nenhuma alteração realizada.")
        
    return dados