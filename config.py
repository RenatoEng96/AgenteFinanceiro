import os

# --- CONFIGURAÇÃO DE API ---
# Tenta carregar do ambiente ou usa a string direta (não recomendado para prod, mas ok para dev local)
# Inserir nas aspas "" abaixo a sua chave API do Google Gemini 
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyCsqX07SqTdOWc8aU3kFJQHAUplC8ry0gE")

# --- CONFIGURAÇÃO DE MODELO ---
# Modelos Gemini que funcionam - gemini-2.5-flash - gemini-3-flash-preview - Inserir um deles dentro das aspas abaixo
MODEL_NAME = "gemini-2.5-flash" 

# --- MAPA DE PARES (COMPARABLES) ---
# Dicionário que mapeia setores (em inglês, padrão Yahoo) para tickers da B3
SECTOR_PEERS_MAP = {
    'Financial': ['ITUB4', 'BBDC4', 'BBAS3', 'SANB11'],
    'Financial Services': ['BPAC11', 'B3SA3', 'CIEL3', 'DXCO3'],
    'Basic Materials': ['VALE3', 'GGBR4', 'CSNA3', 'USIM5', 'SUZB3'],
    'Energy': ['PETR4', 'PRIO3', 'VBBR3', 'UGPA3', 'CSAN3'],
    'Utilities': ['ELET3', 'EQTL3', 'CPFE3', 'CMIG4', 'TRPL4'],
    'Consumer Defensive': ['ABEV3', 'CRFB3', 'ASAI3', 'JBSS3', 'BRFS3'],
    'Consumer Cyclical': ['LREN3', 'MGLU3', 'ARZZ3', 'SOMA3', 'VIVA3'],
    'Industrials': ['WEGE3', 'TASA4', 'EMBR3', 'RAIL3', 'AZUL4'],
    'Real Estate': ['CYRE3', 'EZTC3', 'MRVE3', 'HYPE3'], # Hype as vezes cai aqui
    'Healthcare': ['RDOR3', 'HAPV3', 'FLRY3', 'RADL3'],
    'Technology': ['TOTS3', 'LWSA3', 'INTB3']
}

# --- PARÂMETROS PADRÃO DE VALUATION ---
RISK_FREE_RATE_BR = 0.11  # Taxa Livre de Risco (pode ser conectada a API no futuro)
EQUITY_RISK_PREMIUM = 0.05 # Prêmio de Risco Mercado