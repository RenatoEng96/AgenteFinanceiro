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

        # --- 2. CÁLCULO DINÂMICO DO CUSTO DE CAPITAL (CAPM) ---
        # Obtemos o Ke (Custo de Equity) baseado na Selic atual.
        dados_capm = self.macro.calcular_ke(beta)
        ke_base = dados_capm['ke']
        
        # Para Bancos, usamos Ke puro como taxa de desconto.
        # Para Indústrias, usamos WACC (que aqui simplificamos conservadoramente como Ke).
        taxa_desconto = ke_base

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
        
        # Trava de segurança (WACC/Ke Floor e Cap)
        self.params['wacc_base'] = max(0.09, min(taxa_desconto, 0.25))
        
        # Guarda os metadados
        self.params['capm_data'] = dados_capm
        
        return self.perfil, self.params