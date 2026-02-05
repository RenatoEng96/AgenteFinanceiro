import math

class ValuationEngine:
    def __init__(self, dados: dict, estrategia_params: dict):
        self.dados = dados
        self.params = estrategia_params
        self.resultados = {}
        
        # Ajusta dívida (prioriza PDF se houver)
        divida_pdf = self.dados.get('divida_liquida_total_reais')
        if divida_pdf is not None:
            self.net_debt_per_share = divida_pdf / self.dados.get('total_acoes', 1)
        else:
            self.net_debt_per_share = self.dados.get('divida_liquida_por_acao', 0)

    def run(self) -> dict:
        self._graham()
        self._bazin()
        self._peter_lynch()
        self._dcf_adaptativo() 
        self._dcf_sensibilidade()
        self._reverse_dcf()
        return self.resultados

    def _graham(self):
        """Fórmula Clássica de Graham: VI = Raiz(22.5 * LPA * VPA)"""
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo')
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo')
        
        if lpa and vpa and lpa > 0 and vpa > 0:
            vi = math.sqrt(22.5 * lpa * vpa)
            self.resultados['Graham'] = {'Valor': round(vi, 2), 'Margem': self._calc_margem(vi)}
        else:
            self.resultados['Graham'] = {'Valor': 0, 'Margem': 'N/A'}

    def _bazin(self):
        """Preço Teto Bazin: Dividendos / 6%"""
        div = self.dados.get('div_12m')
        if div and div > 0:
            teto = div / 0.06
            self.resultados['Bazin'] = {
                'Preco_Teto': round(teto, 2),
                'Yield_Atual': f"{self.dados.get('dy_anual', 0):.1%}",
                'Margem': self._calc_margem(teto)
            }
        else:
            self.resultados['Bazin'] = {'Preco_Teto': 0, 'Margem': 'N/A'}

    def _peter_lynch(self):
        """Lynch Fair Value: PEG Ratio simplificado"""
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        if lpa > 0:
            g_proj = self.params['g_estagio1'] * 100
            dy = (self.dados.get('dy_anual') or 0) * 100
            # Multiplicador = Growth + Yield (Limitado a 40x para sanidade)
            multiplicador_justo = min(g_proj + dy, 40.0)
            fair_value = lpa * multiplicador_justo
            
            self.resultados['Peter_Lynch'] = {
                'Valor': round(fair_value, 2),
                'Margem': self._calc_margem(fair_value),
                'Multiplicador_Justo': f"{multiplicador_justo:.1f}x"
            }

    def _calcular_dcf_isolado(self, wacc, g1, anos_g1):
        """
        Função auxiliar pura para calcular DCF dado um WACC e um Crescimento.
        Usada pelo DCF Principal, Sensibilidade e Reverse DCF.
        """
        fcff_base = self.dados.get('fcff_por_acao')
        if not fcff_base or fcff_base < 0: return 0 
        
        fator_ciclico = self.params['fator_ciclico']
        fcff_norm = fcff_base * fator_ciclico
        
        ev_sum = 0
        fluxo = fcff_norm
        
        # Estágio 1: Crescimento Explícito
        for t in range(1, anos_g1 + 1):
            fluxo *= (1 + g1)
            ev_sum += fluxo / ((1 + wacc) ** t)
            
        # Estágio 2: Perpetuidade (Gordon Growth)
        g2 = 0.03 # Perpetuidade inflacionária (3%)
        # Fórmula Valor Terminal: [FCFF_n * (1+g2)] / (WACC - g2)
        # Se WACC <= g2, o modelo quebra (divisão por zero ou negativo), então travamos g2
        g_perpetuidade = min(g2, wacc - 0.01)
        
        vt = (fluxo * (1 + g_perpetuidade)) / (wacc - g_perpetuidade)
        vt_vp = vt / ((1 + wacc) ** anos_g1)
        
        equity_value = (ev_sum + vt_vp) - self.net_debt_per_share
        return max(0, equity_value)

    def _dcf_adaptativo(self):
        wacc = self.params['wacc_base']
        g1 = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        valor = self._calcular_dcf_isolado(wacc, g1, anos)
        
        self.resultados['DCF_Adaptativo'] = {
            'Valor': round(valor, 2),
            'Margem': self._calc_margem(valor),
            'Premissas': {'WACC': f"{wacc:.1%}", 'Cresc_Fase1': f"{g1:.1%}", 'Anos': anos}
        }

    def _dcf_sensibilidade(self):
        wacc_base = self.params['wacc_base']
        g_base = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        wacc_range = [wacc_base + 0.01, wacc_base, wacc_base - 0.01] # +1%, Base, -1%
        g_range = [g_base - 0.015, g_base, g_base + 0.015]           # -1.5%, Base, +1.5%
        
        matriz = []
        for g in g_range:
            linha = []
            for w in wacc_range:
                val = self._calcular_dcf_isolado(w, g, anos)
                linha.append(val)
            matriz.append(linha)
            
        self.resultados['Sensibilidade'] = {
            'Matriz': matriz,
            'Labels_WACC': [f"{w:.1%}" for w in wacc_range],
            'Labels_Growth': [f"{g:.1%}" for g in g_range]
        }

    def _reverse_dcf(self):
        """
        Engenharia Reversa: Qual 'g' (Crescimento) justifica o preço atual?
        Usa Método da Bisseção.
        """
        target_price = self.dados.get('cotacao')
        if not target_price or target_price <= 0: return

        wacc = self.params['wacc_base']
        anos = self.params['anos_estagio1']
        
        low, high = -0.20, 0.80 # Range de busca (-20% a +80% crescimento a.a.)
        implied_g = 0
        
        for _ in range(30):
            mid = (low + high) / 2
            val = self._calcular_dcf_isolado(wacc, mid, anos)
            
            if abs(val - target_price) < 0.10: # Convergência (10 centavos)
                implied_g = mid
                break
            elif val > target_price:
                high = mid # Preço calculado alto demais -> Reduz crescimento
            else:
                low = mid # Preço calculado baixo demais -> Aumenta crescimento
        
        self.resultados['Reverse_DCF'] = {
            'Implied_Growth': implied_g,
            'Target_Price': target_price
        }

    def _calc_margem(self, target):
        price = self.dados.get('cotacao')
        if not price or target == 0: return 0.0
        return round(((target - price) / price) * 100, 1)