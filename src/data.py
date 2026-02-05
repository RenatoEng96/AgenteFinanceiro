import os
import yfinance as yf
import pypdf

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
        shares = info.get('sharesOutstanding', 1)
        if not shares: shares = 1
        net_debt_per_share = net_debt / shares

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

        return {
            "ticker": ticker,
            "cotacao": price,
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
            "beta": info.get('beta', 1.0),
            "fcff_por_acao": fcff_per_share,
            "divida_liquida_por_acao": net_debt_per_share,
            "total_acoes": shares,
            "setor": info.get('sector', 'Unknown'),
            "industria": info.get('industry', 'Unknown'),
            "nome": info.get('longName', ticker)
        }
    except Exception as e:
        print(f"Erro Yahoo ({ticker}): {e}")
        return {}

def ler_pdf_local(caminho: str) -> str:
    """Lê um PDF local e extrai texto das primeiras páginas."""
    if not caminho: return None
    caminho = caminho.strip('"').strip("'")
    if not os.path.exists(caminho): return None
    try:
        with open(caminho, 'rb') as f:
            pdf = pypdf.PdfReader(f)
            # Limita a 20 páginas para não sobrecarregar tokens
            return "\n".join([p.extract_text() for p in pdf.pages[:20] if p.extract_text()])
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return None