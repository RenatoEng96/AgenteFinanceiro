from src.macro import MacroEconomia

class Estrategista:
    def __init__(self, dados: dict):
        self.dados = dados
        self.perfil = "Indefinido"
        self.params = {}
        # Inicializa o motor macroeconómico
        self.macro = MacroEconomia()
    
    def definir_cenario(self) -> tuple:
        """
        Analisa os fundamentos, calcula o WACC Dinâmico (CAPM) e define a Engine de Valuation.
        """
        roe = self.dados.get('roe', 0)
        pl = self.dados.get('pl') or 0
        setor = self.dados.get('setor', '')
        beta = self.dados.get('beta', 1.0)
        moat_score = self.dados.get('moat_score', 5)

        # --- 1. DETECÇÃO DE ENGINE (SETOR) ---
        # Identifica se é Banco/Seguradora para mudar a matemática
        setores_financeiros = ['Financial', 'Banks', 'Insurance', 'Capital Markets']
        is_financial = any(s in setor for s in setores_financeiros)
        
        self.params['engine'] = 'FINANCEIRO' if is_financial else 'PADRAO'

        # --- 2. CÁLCULO EFICIENTE DO CUSTO DE CAPITAL (WACC) ---
        # 1. Custo de Capital Próprio (Ke) via CAPM
        dados_capm = self.macro.calcular_ke(beta)
        ke = dados_capm['ke']
        
        # 2. Dados de Estrutura de Capital
        d = self.dados.get('divida_total', 0)
        e_mkt = self.dados.get('market_cap', 0)
        kd_bruto = self.dados.get('custo_divida_bruto', 0.12)
        tax_rate = self.dados.get('tax_rate_efetiva', 0.34)
        
        wacc_calc = ke # Default fallback
        
        # Se for empresa Não-Financeira, calculamos WACC completo
        if not is_financial and e_mkt > 0:
            # Pesos de Capital (Market Value)
            total_cap = d + e_mkt
            w_d = d / total_cap
            w_e = e_mkt / total_cap
            
            # Custo da Dívida Líquido de IR (Tax Shield)
            kd_net = kd_bruto * (1 - tax_rate)
            
            # Fórmula WACC
            wacc_calc = (ke * w_e) + (kd_net * w_d)
            wacc_calc = max(0.08, wacc_calc) # Floor de segurança
            
            # Atualiza metadados para auditoria
            self.params['wacc_components'] = {
                'Ke': ke, 'Kd_Net': kd_net, 
                'We': w_e, 'Wd': w_d, 
                'TaxRate': tax_rate
            }

        # Para Bancos, usamos Ke puro como taxa de desconto (FCFE/DDM).
        # Para Indústrias, usamos o WACC calculado.
        taxa_desconto = ke if is_financial else wacc_calc

        # --- 3. CLASSIFICAÇÃO E AJUSTES DE RISCO ---
        
        if roe > 0.15 and pl > 15:
            self.perfil = "GROWTH / COMPOUNDER (Alta Qualidade)"
            self.params.update({
                'g_estagio1': min(roe * 0.55, 0.18), # Reinvestimento sustentável
                'anos_estagio1': 10,
                'fator_ciclico': 1.0
            })
        
        elif any(x in setor for x in ['Energy', 'Basic Materials', 'Utilities', 'Mining', 'Oil']):
            self.perfil = "CYCLICAL / COMMODITY (Cíclica)"
            taxa_desconto += 0.015 # Prémio de risco commodities
            self.params.update({
                'g_estagio1': 0.03, # Inflação apenas
                'anos_estagio1': 5,
                'fator_ciclico': 0.75 # Haircut no fluxo
            })
        
        elif roe < 0:
            self.perfil = "DISTRESSED / TURNAROUND"
            taxa_desconto += 0.04 
            self.params.update({
                'g_estagio1': 0.0,
                'anos_estagio1': 3,
                'fator_ciclico': 1.0
            })
        
        elif is_financial:
            self.perfil = "FINANCIAL / BANK (Setor Financeiro)"
            # Bancos maduros crescem próximo ao PIB nominal ou Carteira de Crédito
            self.params.update({
                'g_estagio1': 0.08, # Crescimento nominal carteira (estimado)
                'anos_estagio1': 5,
                'fator_ciclico': 1.0
            })
            
        else:
            self.perfil = "VALUE / INCOME (Renda)"
            self.params.update({
                'g_estagio1': 0.045,
                'anos_estagio1': 6,
                'fator_ciclico': 1.0
            })

        # --- 4. AJUSTE QUALITATIVO (MOAT) ---
        if moat_score >= 8:
            taxa_desconto -= 0.005
            self.perfil += " [Wide Moat]"
        elif moat_score <= 3:
            taxa_desconto += 0.010
            self.perfil += " [No Moat]"
        
        # Trava de segurança Final (WACC/Ke Floor e Cap)
        self.params['wacc_base'] = max(0.08, min(taxa_desconto, 0.25))
        
        # --- 5. AJUSTE MACROECONÔMICO (NOVO) ---
        # Refina o crescimento (g) com base no Ciclo
        contexto = dados_capm.get('contexto_macro', {})
        ciclo = contexto.get('ciclo', 'NEUTRO')
        
        if ciclo.startswith("CONTRACIONISTA"):
            # Juros Reais altos (>6%) punem o crescimento
            self.params['g_estagio1'] = max(0, self.params['g_estagio1'] - 0.015) 
            self.perfil += " [Macro Headwind]"
        elif ciclo.startswith("EXPANSIONISTA"):
            # Juros Reais baixos estimulam, mas mantemos conservadorismo
            self.perfil += " [Macro Tailwind]"
            
        # Guarda os metadados
        self.params['capm_data'] = dados_capm
        
        return self.perfil, self.params