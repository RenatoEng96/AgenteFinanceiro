import os
import yfinance as yf
import pypdf
import re

def obter_dados_yahoo(ticker: str) -> dict:
    """
    Coleta dados fundamentais robustos do Yahoo Finance.
    Adiciona sufixo .SA se necessário.
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
    Lê 100% do conteúdo de um PDF local.
    Realiza limpeza básica para otimizar tokens da IA.
    """
    if not caminho: return None
    
    # Tratamento de string do caminho (remove aspas extras que o Windows poe)
    caminho = caminho.strip('"').strip("'")
    
    if not os.path.exists(caminho):
        print(f"   [ERRO] Arquivo não encontrado: {caminho}")
        return None
        
    try:
        print(f"   -> [I/O] Lendo arquivo completo: {os.path.basename(caminho)}...")
        texto_completo = []
        
        with open(caminho, 'rb') as f:
            pdf = pypdf.PdfReader(f)
            num_paginas = len(pdf.pages)
            print(f"      Processando {num_paginas} páginas...")
            
            for i, page in enumerate(pdf.pages):
                texto_pag = page.extract_text()
                if texto_pag:
                    # Opcional: Adicionar marcador de página para a IA se referenciar
                    texto_completo.append(f"--- PÁGINA {i+1} ---")
                    texto_completo.append(texto_pag)
        
        full_text = "\n".join(texto_completo)
        
        # Limpeza básica para economizar tokens (remove excesso de quebras de linha)
        # Substitui 3 ou mais quebras de linha por apenas duas
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        
        print(f"      Leitura concluída. Total de caracteres: {len(full_text)}")
        return full_text

    except Exception as e:
        print(f"   [ERRO] Falha ao ler PDF: {e}")
        return None