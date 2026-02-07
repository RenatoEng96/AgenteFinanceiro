from src.macro import MacroEconomia

class Estrategista:
    def __init__(self, dados: dict):
        self.dados = dados
        self.perfil = "Indefinido"
        self.params = {}
        self.macro = MacroEconomia()
    
    def definir_cenario(self) -> tuple:
        roe = self.dados.get('roe', 0)
        beta = self.dados.get('beta') 
        if beta is None: beta = 1.0
        
        moat_score = self.dados.get('moat_score', 5)
        setor = self.dados.get('setor', '')
        
        # Identificação de Setores Especiais
        setores_financeiros = ['Financial', 'Banks', 'Insurance', 'Capital Markets']
        is_financial = any(s in setor for s in setores_financeiros)
        
        setores_commodities = ['Energy', 'Oil', 'Gas', 'Basic Materials', 'Mining', 'Steel']
        is_commodity = any(s in setor for s in setores_commodities) or "Petro" in self.dados.get('nome', '')

        # Define Engine Matemática
        self.params['engine'] = 'FINANCEIRO' if is_financial else 'PADRAO'

        # --- 1. CÁLCULO WACC/Ke ---
        dados_capm = self.macro.calcular_ke(beta)
        ke = dados_capm['ke']
        
        # Ajuste Fino: Exporters/Global Players (WEG, EMBRAER, VALE)
        # Se a empresa tem moat alto e é industrial/material, assumimos receita em Dólar.
        # Isso reduz o Risco País na composição do custo de capital.
        is_global_player = False
        if moat_score >= 8 and (is_commodity or setor in ['Industrials', 'Technology']):
            is_global_player = True
            print(f"   [Estratégia] Global Player detectado ({self.dados['ticker']}). Reduzindo Risco País.")
            # Reduz Ke artificialmente para refletir funding global/receita em hard currency
            ke -= 0.015 # -1.5% no custo de equity
        
        d = self.dados.get('divida_total', 0)
        e_mkt = self.dados.get('market_cap', 0)
        kd_bruto = self.dados.get('custo_divida_bruto', 0.10) 
        tax_rate = self.dados.get('tax_rate_efetiva', 0.34)
        
        wacc_calc = ke
        
        if not is_financial and e_mkt > 0:
            total_cap = d + e_mkt
            w_d = d / total_cap
            w_e = e_mkt / total_cap
            kd_net = kd_bruto * (1 - tax_rate)
            wacc_calc = (ke * w_e) + (kd_net * w_d)
            
            # WACC Floor/Cap (Travas de Sanidade)
            # Piso 8.5% (EUA + Spread min) | Teto 16% (Equity muito arriscado)
            wacc_calc = max(0.085, min(wacc_calc, 0.16))
            
            self.params['wacc_components'] = {
                'Ke': ke, 'Kd_Net': kd_net, 
                'We': w_e, 'Wd': w_d, 'TaxRate': tax_rate
            }

        taxa_desconto = ke if is_financial else wacc_calc

        # --- 2. PERFILAMENTO E CRESCIMENTO (g) ---
        # A ORDEM IMPORTA: Setor Específico > Qualidade (ROE)
        
        if is_financial:
            self.perfil = "FINANCIAL / BANK"
            self.params.update({
                'g_estagio1': 0.075, # Crescimento nominal conservador
                'anos_estagio1': 5,
                'fator_ciclico': 1.0
            })
            
        elif is_commodity:
            # CORREÇÃO CRÍTICA PETROBRAS/VALE
            # Commodities não crescem 9% a.a. Elas crescem com o PIB Global/Inflação.
            self.perfil = "CYCLICAL / COMMODITY"
            self.params.update({
                'g_estagio1': 0.035, # Apenas inflação/PIB (3.5%)
                'anos_estagio1': 5,   # Ciclo curto
                'fator_ciclico': 0.80 # Haircut no fluxo atual (considera que estamos em topo de ciclo?)
            })
            # Se for Global Player Commodity (Vale/Petro), WACC já foi ajustado acima
            
        elif roe > 0.20 and moat_score >= 8:
            # Caso WEGE3, RADL3
            self.perfil = "COMPOUNDER (Elite)"
            self.params.update({
                'g_estagio1': 0.13, # Crescimento forte (13%)
                'anos_estagio1': 10, # Duration longa
                'fator_ciclico': 1.0
            })
            
        elif roe > 0.12:
            self.perfil = "QUALITY (Estável)"
            self.params.update({
                'g_estagio1': 0.08, 
                'anos_estagio1': 7,
                'fator_ciclico': 1.0
            })
            
        else:
            self.perfil = "VALUE / LOW GROWTH"
            self.params.update({
                'g_estagio1': 0.04, 
                'anos_estagio1': 5,
                'fator_ciclico': 0.90
            })

        # --- 3. PREMIO DE MOAT (Ajuste Final) ---
        if moat_score >= 9:
            taxa_desconto -= 0.010 # -1% Bônus de Qualidade Extrema
            self.perfil += " [Moat Premium]"
        
        # Salva WACC Final
        self.params['wacc_base'] = max(0.08, taxa_desconto)
        self.params['capm_data'] = dados_capm
        
        return self.perfil, self.params