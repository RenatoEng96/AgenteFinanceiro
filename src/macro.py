import requests
import json
from datetime import datetime

class MacroEconomia:
    def __init__(self):
        # API do Banco Central do Brasil (SGS - Sistema Gerenciador de Séries Temporais)
        # Série 432: Taxa de juros - Meta Selic definida pelo Copom (% a.a.)
        self.api_bcb = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        
        # Parâmetros Padrão (Fallback em caso de falha da API)
        self.selic_padrao = 11.25
        self.equity_risk_premium = 0.06  # Prêmio de Risco de Mercado (6%)
        self.country_risk_spread = 0.0   # Spread adicional (já embutido na Selic vs Treasury)

    def get_risk_free_rate(self):
        """
        Obtém a Taxa Livre de Risco (Rf) atualizada do Banco Central (Meta Selic).
        Retorna float (ex: 0.1125 para 11.25%)
        """
        print("   -> [Macro] A consultar API do Banco Central (Taxa Selic)...")
        try:
            response = requests.get(self.api_bcb, timeout=5)
            if response.status_code == 200:
                dados = response.json()
                # O valor vem como string "11.25"
                taxa = float(dados[0]['valor'])
                print(f"      Taxa Selic Atual: {taxa}%")
                return taxa / 100
            else:
                print("      [Aviso] Falha na API BCB. A usar taxa padrão.")
                return self.selic_padrao / 100
        except Exception as e:
            print(f"      [Erro Macro] {e}. A usar taxa de contingência.")
            return self.selic_padrao / 100

    def calcular_ke(self, beta, rf=None):
        """
        Calcula o Custo de Capital Próprio (Ke) via CAPM.
        Ke = Rf + Beta * ERP
        """
        if rf is None:
            rf = self.get_risk_free_rate()
            
        # Se o Beta for inválido ou muito baixo (ex: < 0.4), ajustamos para um mínimo conservador
        # para evitar taxas de desconto irrealisticamente baixas.
        beta_ajustado = max(0.5, beta) if beta else 1.0
        
        ke = rf + (beta_ajustado * self.equity_risk_premium)
        
        return {
            'ke': round(ke, 4),
            'rf_usado': rf,
            'beta_usado': beta_ajustado,
            'erp_usado': self.equity_risk_premium
        }