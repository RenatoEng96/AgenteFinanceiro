import math
import sys

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
            # Bancos e Seguradoras usam Dividend Discount Model (Gordon + Justified P/B)
            self._valuation_financeiro()
        else:
            # Indústria e Comércio usam DCF Padrão
            self._dcf_adaptativo()
            self._dcf_sensibilidade()
            self._reverse_dcf()
            
        # Executa Monte Carlo para TODOS (Agora genérico)
        self._monte_carlo_simulation()

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
    def _calcular_dcf_isolado(self, wacc, g1, anos_g1, g_perp=None, exit_multiple=None):
        fcff_base = self.dados.get('fcff_por_acao')
        if not fcff_base or fcff_base < 0: return 0 
        
        fator_ciclico = self.params.get('fator_ciclico', 1.0)
        fcff_norm = fcff_base * fator_ciclico
        
        ev_sum = 0
        fluxo = fcff_norm
        
        # Estágio 1: Crescimento Explícito
        for t in range(1, int(anos_g1) + 1):
            fluxo *= (1 + g1)
            ev_sum += fluxo / ((1 + wacc) ** t)
        
        # Estágio 2: Valor Terminal (TV)
        if g_perp is None:
            g2 = 0.03
            g_perp = min(g2, wacc - 0.015) 
        
        fluxo_terminal = fluxo * (1 + g_perp)
        tv_gordon = fluxo_terminal / (wacc - g_perp)
        
        tv_final = tv_gordon
            
        tv_vp = tv_final / ((1 + wacc) ** anos_g1)
        
        equity_value = (ev_sum + tv_vp) - self.net_debt_per_share
        return max(0, equity_value)

    def _dcf_adaptativo(self):
        wacc = self.params['wacc_base']
        g1 = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        # Prepara config para Monte Carlo
        fcff_base = self.dados.get('fcff_por_acao', 0) * self.params.get('fator_ciclico', 1.0)
        self.params['mc_config'] = {
            'base_value': fcff_base,
            'discount_rate': wacc,
            'growth_rate': g1,
            'years': anos,
            'net_debt': self.net_debt_per_share
        }

        valor = self._calcular_dcf_isolado(wacc, g1, anos)
        
        self.resultados['DCF_Adaptativo'] = {
            'Tipo': 'DCF (Fluxo de Caixa)', 
            'Valor': round(valor, 2),
            'Margem': self._calc_margem(valor),
            'Premissas': {'WACC': f"{wacc:.1%}", 'Cresc.': f"{g1:.1%}"}
        }

    def _monte_carlo_simulation(self):
        try:
            import numpy as np
        except ImportError:
            self.resultados['Monte_Carlo'] = {"Erro": "Numpy missing"}
            return

        config_mc = self.params.get('mc_config')
        if not config_mc or config_mc['base_value'] <= 0:
            self.resultados['Monte_Carlo'] = {"Status": "Skipped (Invalid inputs)"}
            return

        N = 10000
        
        val_base = config_mc['base_value']
        rate_base = config_mc['discount_rate']
        g_base = config_mc['growth_rate']
        years = int(config_mc['years'])
        net_debt = config_mc['net_debt']

        # Distribuições
        rate_sim = np.random.normal(rate_base, 0.015, N)
        rate_sim = np.maximum(rate_sim, 0.06) 
        
        g_sim = np.random.normal(g_base, 0.02, N)
        g_perp_sim = np.random.uniform(0.02, 0.04, N)
        g_perp_sim = np.minimum(g_perp_sim, rate_sim - 0.015)
        
        # Vetorização (Gordon 2 Estágios Genérico)
        numerator = 1 - ((1 + g_sim) / (1 + rate_sim)) ** years
        denominator = rate_sim - g_sim
        denominator = np.where(np.abs(denominator) < 0.001, 0.001, denominator)
        
        cf1 = val_base * (1 + g_sim) 
        pv_stage1 = cf1 * (numerator / denominator)
        
        cf_n = val_base * ((1 + g_sim) ** years)
        cf_n1 = cf_n * (1 + g_perp_sim)
        tv = cf_n1 / (rate_sim - g_perp_sim)
        pv_tv = tv / ((1 + rate_sim) ** years)
        
        enterprise_val = pv_stage1 + pv_tv
        equity_val = enterprise_val - net_debt
        equity_val = np.maximum(0, equity_val)
        
        mean_price = np.mean(equity_val)
        var_5 = np.percentile(equity_val, 5)
        var_95 = np.percentile(equity_val, 95)
        std_dev = np.std(equity_val)
        median_price = np.median(equity_val)

        current_price = self.dados.get('cotacao', 0)
        upside_prob = np.mean(equity_val > current_price) if current_price > 0 else 0
        
        self.resultados['Monte_Carlo'] = {
            'Mean': round(mean_price, 2),
            'Median': round(median_price, 2),
            'VaR_5_Percent': round(var_5, 2),
            'Upside_95_Percent': round(var_95, 2),
            'Std_Dev': round(std_dev, 2),
            'Upside_Prob': f"{upside_prob:.1%}",
            'Iterations': N
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
        ke = self.params['wacc_base'] # Ke (Custo de Equity)
        roe = self.dados.get('roe', 0.15)
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo') or 1
        
        payout = 0.50
        g_sustentavel = roe * (1 - payout)
        # Trava: g não pode ser maior que Ke (Gordon)
        g_final = min(g_sustentavel, ke - 0.02)
        
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        div_projetado = (lpa * payout)
        
        # Configura Monte Carlo para Bancos (Equity direto)
        self.params['mc_config'] = {
            'base_value': div_projetado,
            'discount_rate': ke,
            'growth_rate': g_final,
            'years': 5, 
            'net_debt': 0 
        }

        # 1. Modelo de Gordon (Dividendos)
        div_proj_y1 = div_projetado * (1+g_final)
        valor_gordon = div_proj_y1 / (ke - g_final)
        
        # 2. Modelo Justified P/VP
        justified_pvp = (roe - g_final) / (ke - g_final)
        valor_justified = vpa * justified_pvp
        
        valor_final = (valor_gordon + valor_justified) / 2
        
        self.resultados['DCF_Adaptativo'] = {
            'Tipo': 'Modelo de Dividendos (DDM)',
            'Valor': round(valor_final, 2),
            'Margem': self._calc_margem(valor_final),
            'Premissas': {
                'WACC': f"{ke:.1%}", 
                'Cresc.': f"{g_final:.1%}",
                'ROE': f"{roe:.1%}"
            }
        }
        
        # Sensibilidade para Bancos
        ke_range = [ke + 0.01, ke, ke - 0.01]
        g_range = [g_final - 0.01, g_final, g_final + 0.01]
        
        matriz = []
        for g_sens in g_range:
            linha = []
            for k_sens in ke_range:
                if k_sens > g_sens:
                    v = (div_projetado*(1+g_sens)) / (k_sens - g_sens)
                    j_pvp = (roe - g_sens) / (k_sens - g_sens)
                    v_just = vpa * j_pvp
                    linha.append((v + v_just)/2)
                else:
                    linha.append(0)
            matriz.append(linha)
            
        self.resultados['Sensibilidade'] = {
            'Matriz': matriz,
            'Labels_WACC': [f"{k:.1%}" for k in ke_range],
            'Labels_Growth': [f"{g:.1%}" for g in g_range]
        }
        self.resultados['Reverse_DCF'] = {}

    def _calc_margem(self, target):
        price = self.dados.get('cotacao')
        if not price or target == 0: return 0.0
        return round(((target - price) / price) * 100, 1)

    def _forensic_analysis(self):
        flags = []
        score = 10 
        lucro = self.dados.get('lucro_liquido', 0)
        fco = self.dados.get('fluxo_caixa_operacional', 0)
        
        if lucro > 0 and fco > 0:
            ratio_accruals = (lucro - fco) / abs(lucro)
            if ratio_accruals > 0.20:
                flags.append(f"ALERTA: Lucro > FCO em {ratio_accruals:.1%}. Accruals?")
                score -= 2
        elif lucro > 0 and fco < 0:
             flags.append("PERIGO: Lucro positivo com queima de caixa operacional.")
             score -= 4

        div_liq = self.dados.get('total_debt', 0) - self.dados.get('caixa_total', 0) 
        if 'divida_total' in self.dados:
             div_liq = self.dados['divida_total'] - self.dados.get('caixa_total', 0)
        ebitda = self.dados.get('ebitda', 0)
        
        if ebitda > 0:
            lev = div_liq / ebitda
            if lev > 3.5:
                flags.append(f"RISCO: Alavancagem Alta ({lev:.1f}x).")
                score -= 2
            elif lev > 5.0:
                flags.append(f"CRÍTICO: Alavancagem ({lev:.1f}x).")
                score -= 3
        
        if self.dados.get('margem_liq', 0) < -0.05:
            flags.append("ATENÇÃO: Margem Líquida negativa.")
            score -= 1
            
        self.resultados['Forensic'] = {
             'Score': max(0, score),
             'Flags': flags, 
             'Verdict': "Contabilidade Vigorosa" if score >= 8 else "Sinais de Alerta" if score >= 5 else "Alto Risco"
        }