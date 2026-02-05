import requests
import json
from datetime import datetime

class MacroEconomia:
    def __init__(self):
        # API do Banco Central do Brasil (SGS - Sistema Gerenciador de Séries Temporais)
        # Série 432: Taxa de juros - Meta Selic definida pelo Copom (% a.a.)
        self.api_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        
        # Série 13522: IPCA - Acumulado 12 meses (% a.a.)
        self.api_ipca = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"
        
        # Parâmetros Padrão (Fallback em caso de falha da API)
        self.selic_padrao = 11.25
        self.ipca_padrao = 4.50
        self.equity_risk_premium = 0.06  # Prêmio de Risco de Mercado (6%)

    def get_macro_data(self):
        """
        Coleta Selic e IPCA para definir o cenário macro.
        Retorna dicionário com taxas e contexto.
        """
        selic = self._fetch_bcb(self.api_selic, self.selic_padrao, "Selic")
        ipca = self._fetch_bcb(self.api_ipca, self.ipca_padrao, "IPCA")
        
        # Juro Real (Fisher Equation simplificada para taxas baixas ou exata: (1+i)/(1+inf) - 1)
        # Usando fórmula exata para precisão financeira
        juro_real = ((1 + selic/100) / (1 + ipca/100)) - 1
        juro_real_pct = juro_real * 100
        
        # Definição de Ciclo
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
        print(f"   -> [Macro] A consultar {label} no Banco Central...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                dados = response.json()
                valor = float(dados[0]['valor'])
                print(f"      {label} Atual: {valor}%")
                return valor
            else:
                print(f"      [Aviso] Falha na API BCB ({label}). Usando padrão.")
                return default
        except Exception as e:
            print(f"      [Erro Macro] {e}. Usando {label} padrão.")
            return default

    def calcular_ke(self, beta, rf=None):
        """
        Calcula o Custo de Capital Próprio (Ke) via CAPM.
        Ke = Rf + Beta * ERP
        """
        macro_data = self.get_macro_data()
        
        if rf is None:
            rf = macro_data['risk_free']
            
        # Se o Beta for inválido ou muito baixo (ex: < 0.4), ajustamos para um mínimo conservador
        # para evitar taxas de desconto irrealisticamente baixas.
        beta_ajustado = max(0.5, beta) if beta else 1.0
        
        ke = rf + (beta_ajustado * self.equity_risk_premium)
        
        return {
            'ke': round(ke, 4),
            'rf_usado': rf,
            'beta_usado': beta_ajustado,
            'erp_usado': self.equity_risk_premium,
            'contexto_macro': macro_data
        }
