class Estrategista:
    def __init__(self, dados: dict):
        self.dados = dados
        self.perfil = "Indefinido"
        self.params = {}
    
    def definir_cenario(self) -> tuple:
        """
        Analisa os fundamentos para categorizar a empresa e definir inputs do DCF.
        Retorna: (Perfil, Parametros)
        """
        roe = self.dados.get('roe', 0)
        pl = self.dados.get('pl') or 0
        setor = self.dados.get('setor', '')
        divida_liq = self.dados.get('divida_liquida_por_acao', 0)

        # 1. Regras de Classificação
        # Compounders de Alta Qualidade
        if roe > 0.15 and pl > 15:
            self.perfil = "GROWTH / COMPOUNDER (Alta Qualidade)"
            self.params = {
                'g_estagio1': min(roe * 0.55, 0.18), # Limita crescimento a 18% ou reinvestimento sustentável
                'anos_estagio1': 10,                 # Período longo de vantagem competitiva
                'wacc_base': 0.115,                  # WACC menor (menor risco percebido)
                'fator_ciclico': 1.0
            }
        
        # Commodities e Cíclicas
        elif any(x in setor for x in ['Energy', 'Basic Materials', 'Utilities', 'Mining']):
            self.perfil = "CYCLICAL / COMMODITY (Cíclica)"
            self.params = {
                'g_estagio1': 0.03,  # Crescimento próximo à inflação/PIB
                'anos_estagio1': 5,
                'wacc_base': 0.14,   # WACC maior devido à volatilidade
                'fator_ciclico': 0.75 # Haircut no fluxo de caixa atual (assume que estamos em topo de ciclo?)
            }
        
        # Empresas em Prejuízo ou Turnaround
        elif roe < 0:
            self.perfil = "DISTRESSED / TURNAROUND (Prejuízo)"
            self.params = {
                'g_estagio1': 0.0,
                'anos_estagio1': 3,
                'wacc_base': 0.16,
                'fator_ciclico': 1.0
            }
        
        # Vacas Leiteiras (Renda)
        else:
            self.perfil = "VALUE / INCOME (Renda/Estável)"
            self.params = {
                'g_estagio1': 0.045,
                'anos_estagio1': 6,
                'wacc_base': 0.125,
                'fator_ciclico': 1.0
            }

        # 2. Ajuste Fino de Risco (WACC) baseado em Dívida
        # Se tem Caixa Líquido (Dívida negativa), reduz o risco.
        if divida_liq < 0: 
            self.params['wacc_base'] -= 0.005
        
        return self.perfil, self.params