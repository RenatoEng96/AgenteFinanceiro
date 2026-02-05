import math

class ValuationEngine:
    def __init__(self, dados: dict, estrategia_params: dict):
        self.dados = dados
        self.params = estrategia_params
        self.resultados = {}
        
        # Ajusta dívida
        divida_pdf = self.dados.get('divida_liquida_total_reais')
        if divida_pdf is not None:
            self.net_debt_per_share = divida_pdf / self.dados.get('total_acoes', 1)
        else:
            self.net_debt_per_share = self.dados.get('divida_liquida_por_acao', 0)

    def run(self) -> dict:
        # Métodos Universais
        self._graham()
        self._bazin()
        self._peter_lynch()
        self._forensic_analysis()
        
        # Seleção de Engine Específica
        engine_type = self.params.get('engine', 'PADRAO')
        
        if engine_type == 'FINANCEIRO':
            # Bancos e Seguradoras usam Dividend Discount Model
            self._valuation_financeiro()
        else:
            # Indústria e Comércio usam DCF Padrão
            self._dcf_adaptativo()
            self._dcf_sensibilidade()
            self._reverse_dcf()
            
        return self.resultados

    def _graham(self):
        """VI = Raiz(22.5 * LPA * VPA)"""
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo')
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo')
        
        if lpa and vpa and lpa > 0 and vpa > 0:
            vi = math.sqrt(22.5 * lpa * vpa)
            self.resultados['Graham'] = {'Valor': round(vi, 2), 'Margem': self._calc_margem(vi)}
        else:
            self.resultados['Graham'] = {'Valor': 0, 'Margem': 'N/A'}

    def _bazin(self):
        """Preço Teto = Dividendos / 6%"""
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
        """Fair PE = Growth + Yield"""
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        if lpa > 0:
            g_proj = self.params['g_estagio1'] * 100
            dy = (self.dados.get('dy_anual') or 0) * 100
            multiplicador_justo = min(g_proj + dy, 40.0)
            fair_value = lpa * multiplicador_justo
            
            self.resultados['Peter_Lynch'] = {
                'Valor': round(fair_value, 2),
                'Margem': self._calc_margem(fair_value),
                'Multiplicador_Justo': f"{multiplicador_justo:.1f}x"
            }

    # --- ENGINE 1: DCF PADRÃO (INDÚSTRIA) ---
    def _calcular_dcf_isolado(self, wacc, g1, anos_g1):
        fcff_base = self.dados.get('fcff_por_acao')
        if not fcff_base or fcff_base < 0: return 0 
        
        fator_ciclico = self.params['fator_ciclico']
        fcff_norm = fcff_base * fator_ciclico
        
        ev_sum = 0
        fluxo = fcff_norm
        
        for t in range(1, anos_g1 + 1):
            fluxo *= (1 + g1)
            ev_sum += fluxo / ((1 + wacc) ** t)
            
        g2 = 0.03
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
            'Tipo': 'DCF (Fluxo de Caixa)', # Label para o relatório
            'Valor': round(valor, 2),
            'Margem': self._calc_margem(valor),
            'Premissas': {'WACC': f"{wacc:.1%}", 'Cresc.': f"{g1:.1%}"}
        }

    def _dcf_sensibilidade(self):
        wacc_base = self.params['wacc_base']
        g_base = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        wacc_range = [wacc_base + 0.01, wacc_base, wacc_base - 0.01] 
        g_range = [g_base - 0.015, g_base, g_base + 0.015]           
        
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
        target_price = self.dados.get('cotacao')
        if not target_price or target_price <= 0: return

        wacc = self.params['wacc_base']
        anos = self.params['anos_estagio1']
        
        low, high = -0.20, 0.80 
        implied_g = 0
        
        for _ in range(30):
            mid = (low + high) / 2
            val = self._calcular_dcf_isolado(wacc, mid, anos)
            
            if abs(val - target_price) < 0.10: 
                implied_g = mid
                break
            elif val > target_price: high = mid 
            else: low = mid 
        
        self.resultados['Reverse_DCF'] = {
            'Implied_Growth': implied_g,
            'Target_Price': target_price
        }

    # --- ENGINE 2: FINANCEIRO (BANCOS/SEGURADORAS) ---
    def _valuation_financeiro(self):
        """
        Para bancos, usamos o Modelo de Gordon Modificado (Dividendos) e Justified P/B.
        Fórmula Gordon: P = D1 / (Ke - g)
        Fórmula Justified P/B: (ROE - g) / (Ke - g)
        """
        ke = self.params['wacc_base'] # Ke (Custo de Equity)
        roe = self.dados.get('roe', 0.15)
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo') or 1
        
        # Payout Ratio estimado (Bancos BR pagam ~50% historicamente)
        payout = 0.50
        
        # Crescimento Sustentável (Sustainable Growth Rate)
        # g = ROE * (1 - Payout)
        g_sustentavel = roe * (1 - payout)
        
        # Trava de Segurança Matemática:
        # Se g >= Ke, o modelo explode (valor infinito).
        # Em bancos de alta qualidade (ROE 20%), g pode ser > Ke (14%).
        # Nesses casos, limitamos o g perpétuo a Ke - 2% para conservadorismo.
        g_final = min(g_sustentavel, ke - 0.02)
        
        # D1 = Dividendo projetado próximo ano
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        div_projetado = (lpa * payout) * (1 + g_final)
        
        # 1. Modelo de Gordon (Dividendos)
        valor_gordon = div_projetado / (ke - g_final)
        
        # 2. Modelo Justified P/VP (Excesso de Retorno)
        # Multiplo Justo = (ROE - g) / (Ke - g)
        justified_pvp = (roe - g_final) / (ke - g_final)
        valor_justified = vpa * justified_pvp
        
        # Média dos dois métodos financeiros
        valor_final = (valor_gordon + valor_justified) / 2
        
        self.resultados['DCF_Adaptativo'] = {
            'Tipo': 'Modelo de Dividendos (DDM)', # Sobrescreve label DCF
            'Valor': round(valor_final, 2),
            'Margem': self._calc_margem(valor_final),
            'Premissas': {
                'WACC': f"{ke:.1%}",  # Usamos Ke como WACC para manter compatibilidade com o report
                'Cresc.': f"{g_final:.1%}",
                'ROE': f"{roe:.1%}"
            }
        }
        
        # Gera Sensibilidade para Bancos (Ke vs g)
        ke_range = [ke + 0.01, ke, ke - 0.01]
        g_range = [g_final - 0.01, g_final, g_final + 0.01]
        
        matriz = []
        for g_sens in g_range:
            linha = []
            for k_sens in ke_range:
                # Gordon simples para sensibilidade
                if k_sens > g_sens:
                    v = div_projetado / (k_sens - g_sens)
                    # Média com Justified P/B (assumindo ROE constante)
                    justified_pvp = (roe - g_sens) / (k_sens - g_sens)
                    v_just = vpa * justified_pvp
                    linha.append((v + v_just)/2)
                else:
                    linha.append(0)
            matriz.append(linha)
            
        self.resultados['Sensibilidade'] = {
            'Matriz': matriz,
            'Labels_WACC': [f"{k:.1%}" for k in ke_range],
            'Labels_Growth': [f"{g:.1%}" for g in g_range]
        }
        
        # OBS: Para bancos, não fazemos Reverse DCF de fluxo de caixa operacional,
        # pois a métrica é distorcida. Deixamos vazio ou adaptamos futuramente.
        self.resultados['Reverse_DCF'] = {}

    def _calc_margem(self, target):
        price = self.dados.get('cotacao')
        if not price or target == 0: return 0.0
        return round(((target - price) / price) * 100, 1)

    def _forensic_analysis(self):
        """
        Realiza checagens de qualidade contábil e solvência.
        1. Beneish M-Score Simplificado (Fluxo vs Lucro)
        2. Solvência (Dívida Liq / EBITDA)
        3. Altman Z-Score Simplificado (Proxy)
        """
        flags = []
        score = 10 # Começa com nota 10
        
        # 1. Earnings Quality (Lucro Líquido vs FCO)
        lucro = self.dados.get('lucro_liquido', 0)
        fco = self.dados.get('fluxo_caixa_operacional', 0)
        
        if lucro > 0 and fco > 0:
            ratio_accruals = (lucro - fco) / abs(lucro)
            # Se o Lucro é muito maior que o Caixa (> 20% acima), pode indicar contabilização agressiva
            if ratio_accruals > 0.20:
                flags.append(f"ALERTA: Lucro Líquido excede FCO em {ratio_accruals:.1%}. Possível 'Accruals' excessivos.")
                score -= 2
        elif lucro > 0 and fco < 0:
             flags.append("PERIGO: Empresa lucra mas queima caixa operacional (Divergência Grave).")
             score -= 4

        # 2. Solvência (Alavancagem)
        div_liq = self.dados.get('total_debt', 0) - self.dados.get('caixa_total', 0) 
        # Fallback de divida liquida se nao vier no get anterior (mas data.py ja calcula)
        # Vamos usar o que veio no self.dados
        ebitda = self.dados.get('ebitda', 0)
        
        # Recalcula net debt caso nao tenha vindo direto
        if 'divida_total' in self.dados:
             div_liq = self.dados['divida_total'] - self.dados.get('caixa_total', 0)

        if ebitda > 0:
            lev = div_liq / ebitda
            if lev > 3.5:
                flags.append(f"RISCO: Alavancagem Alta (Dívida Líq/EBITDA = {lev:.1f}x).")
                score -= 2
            elif lev > 5.0:
                flags.append(f"CRÍTICO: Alavancagem Perigosa ({lev:.1f}x). Risco de Solvência.")
                score -= 3
        
        # 3. Margem Líquida Negativa Recorrente (Proxy de Z-Score fraco)
        if self.dados.get('margem_liq', 0) < -0.05:
            flags.append("ATENÇÃO: Margens Líquidas profundamente negativas. Queima de valor.")
            score -= 1
            
        self.resultados['Forensic'] = {
             'Score': max(0, score),
             'Flags': flags, 
             'Verdict': "Contabilidade Vigorosa" if score >= 8 else "Sinais de Alerta" if score >= 5 else "Alto Risco Contábil"
        }