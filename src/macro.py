import requests
import json
from datetime import datetime

class MacroEconomia:
    def __init__(self):
        # API do Banco Central do Brasil (SGS)
        self.api_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        self.api_ipca = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"
        
        # Parâmetros Padrão
        self.selic_padrao = 11.25
        self.ipca_padrao = 4.50
        
        # AJUSTE 1: Prêmios de Risco Calibrados para Brasil
        self.equity_risk_premium = 0.055  # ERP Global/Brasil (5.5% é padrão Damodaran/Mercado)
        self.country_risk_premium = 0.020 # Spread CDS Brasil (aprox 200bps)

    def get_macro_data(self):
        selic = self._fetch_bcb(self.api_selic, self.selic_padrao, "Selic")
        ipca = self._fetch_bcb(self.api_ipca, self.ipca_padrao, "IPCA")
        
        juro_real = ((1 + selic/100) / (1 + ipca/100)) - 1
        juro_real_pct = juro_real * 100
        
        ciclo = "NEUTRO"
        if juro_real_pct > 6.0: ciclo = "CONTRACIONISTA (Aperto Monetário)"
        elif juro_real_pct < 3.0: ciclo = "EXPANSIONISTA (Estímulo)"
        
        return {
            'selic': selic,
            'ipca': ipca,
            'juro_real': juro_real_pct,
            'ciclo': ciclo,
            'risk_free': selic / 100
        }

    def _fetch_bcb(self, url, default, label):
        print(f"   -> [Macro] Consultando {label}...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                dados = response.json()
                valor = float(dados[0]['valor'])
                return valor
            return default
        except Exception:
            return default

    def calcular_ke(self, beta, rf=None):
        """
        Calcula o Custo de Equity (Ke).
        MELHORIA: Normalização da Taxa Livre de Risco para Valuation.
        """
        macro_data = self.get_macro_data()
        
        if rf is None:
            rf_spot = macro_data['risk_free']
            
            # MELHORIA CRÍTICA: Normalização do Risk Free para Longo Prazo.
            # Se a Selic estiver em "Stress" (>12%), o mercado não precifica perpetuidade a 12%.
            # O mercado usa a ponta longa da curva (DI Futuro), que tende a convergir para ~10.5% a 11%.
            # Se a Selic estiver artificialmente baixa (<6%), corrigimos para cima.
            rf_valuation = rf_spot
            
            if rf_spot > 0.125: # Se Selic > 12.5%
                print(f"      [Macro Ajuste] Selic Spot ({rf_spot:.1%}) muito alta para Valuation de Longo Prazo.")
                rf_valuation = 0.115 # Teto conservador para Rf de longo prazo (11.5%)
                print(f"      [Macro Ajuste] Usando Rf Normalizada: {rf_valuation:.1%}")
                
            elif rf_spot < 0.06: # Se Selic < 6% (Artificialmente baixa)
                rf_valuation = 0.085 # Piso prudencial
                
            rf = rf_valuation
            
        # Beta Sanitization: Evita Betas quebrados do Yahoo (ex: 0.1 ou 2.5 para utilities)
        beta_ajustado = max(0.60, min(beta, 1.6)) if beta else 1.0
        
        # Fórmula CAPM: Rf + Beta*ERP + Country
        ke = rf + (beta_ajustado * self.equity_risk_premium) + self.country_risk_premium
        
        return {
            'ke': round(ke, 4),
            'rf_usado': rf,
            'beta_usado': beta_ajustado,
            'erp_usado': self.equity_risk_premium,
            'risk_country_usado': self.country_risk_premium,
            'contexto_macro': macro_data
        }