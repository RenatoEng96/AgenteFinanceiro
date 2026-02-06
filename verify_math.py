import sys
import os
import numpy as np
sys.path.append(os.getcwd())

from src.valuation import ValuationEngine
from src.strategy import Estrategista

# Mock Data simulating WEGE3
mock_data = {
    'ticker': 'WEGE3',
    'cotacao': 40.0,
    'fcff_por_acao': 1.50,
    'divida_liquida_por_acao': -0.50, # Caixa Liquido
    'market_cap': 160000, # milhoes
    'divida_total': 1000,
    'tax_rate_efetiva': 0.15,
    'custo_divida_bruto': 0.08,
    'beta': 0.8,
    'roe': 0.25,
    'pl': 25,
    'setor': 'Industrials',
    'moat_score': 9,
    'moat_justificativa': 'Strong Brand & Tech'
}

# Mock Strategy execution
print(">>> 1. Testing Strategy (WACC Calculation)...")
strat = Estrategista(mock_data)
# Mock Macro dependency manually
strat.macro.get_macro_data = lambda: {'selic': 11.25, 'ipca': 4.5, 'juro_real': 6.5, 'ciclo': 'NEUTRO', 'risk_free': 0.1125}
strat.macro.equity_risk_premium = 0.06
strat.macro.country_risk_premium = 0.025

perfil, params = strat.definir_cenario()
print(f"Perfil: {perfil}")
print(f"Params: {params}")

# Validate WACC
# Ke = Rf (11.25) + Beta(0.8)*ERP(6.0) + Country(2.5) = 11.25 + 4.8 + 2.5 = 18.55%
ke_expected = 0.1125 + (0.8 * 0.06) + 0.025
print(f"Ke Expected: {ke_expected:.2%}")
print(f"Ke Calculated: {params['wacc_components']['Ke']:.2%}")

# WACC = Ke*We + Kd*(1-t)*Wd
# E = 160000, D = 1000 -> Equity dominant (~99%)
# So WACC should be very close to Ke
print(f"WACC Final: {params['wacc_base']:.2%}")

# Mock Valuation execution
print("\n>>> 2. Testing Valuation Engine (Monte Carlo)...")
engine = ValuationEngine(mock_data, params)
# engine._monte_carlo_simulation() # Called inside runs? No, manual call for test
engine._monte_carlo_simulation()
mc = engine.resultados.get('Monte_Carlo', {})

print("Monte Carlo Results:")
print(mc)

if 'Mean' in mc:
    print("SUCCESS: Monte Carlo ran successfully.")
else:
    print("FAILURE: Monte Carlo did not produce results.")

# engine._dcf_adaptativo()
engine._dcf_adaptativo()
dcf = engine.resultados.get('DCF_Adaptativo')
print("\nDCF Standard Results:")
print(dcf)
