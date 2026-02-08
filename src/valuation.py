import math
import sys

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

class ValuationEngine:
    """
    Motor matemático que executa múltiplos modelos de precificação.
    
    Modelos Implementados:
    1. Graham: Valor Intrínseco Clássico (focado em ativos e lucros).
    2. Bazin: Preço Teto baseado em dividendos (focado em renda).
    3. Peter Lynch: Valor Justo baseado em crescimento (PEG Ratio).
    4. DCF Adaptativo: Fluxo de Caixa Descontado ajustado ao perfil da empresa.
    5. Valuation Financeiro (DDM): Modelo de Dividendos para Bancos.
    6. Monte Carlo: Simulação probabilística de cenários.
    7. Auditoria Forense: Checagem de qualidade dos lucros (Accruals).
    """
    def __init__(self, dados: dict, estrategia_params: dict):
        self.dados = dados
        self.params = estrategia_params
        self.resultados = {}
        
        divida_pdf = self.dados.get('divida_liquida_total_reais')
        if divida_pdf is not None:
            self.net_debt_per_share = divida_pdf / self.dados.get('total_acoes', 1)
        else:
            self.net_debt_per_share = self.dados.get('divida_liquida_por_acao', 0)

    def run(self) -> dict:
        self._graham()
        self._bazin()
        self._peter_lynch()
        self._forensic_analysis()
        
        engine_type = self.params.get('engine', 'PADRAO')
        if engine_type == 'FINANCEIRO':
            self._valuation_financeiro()
        else:
            self._dcf_adaptativo()
            self._dcf_sensibilidade()
            self._reverse_dcf()
            
        self._monte_carlo_simulation()
        return self.resultados

    # Métodos Graham, Bazin, Lynch
    def _graham(self):
        """
        Fórmula de Benjamin Graham: VI = Raiz(22.5 * LPA * VPA).
        Ideal para empresas industriais e de valor.
        """
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo')
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo')
        if lpa and vpa and lpa > 0 and vpa > 0:
            vi = math.sqrt(22.5 * lpa * vpa)
            self.resultados['Graham'] = {'Valor': round(vi, 2), 'Margem': self._calc_margem(vi)}
        else:
            self.resultados['Graham'] = {'Valor': 0, 'Margem': 'N/A'}

    def _bazin(self):
        """
        Método Décio Bazin: Preço Justo = Yield Esperado (6%).
        Foca em empresas pagadoras de dividendos.
        """
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
        """
        Fair Value = LPA * (Crescimento + Dividend Yield).
        Se PEG Ratio < 1, é barato. Aqui calculamos o valor onde PEG seria 1.
        """
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        if lpa > 0:
            g_proj = self.params.get('g_estagio1', 0.10) * 100
            dy = (self.dados.get('dy_anual') or 0) * 100
            # Peter Lynch Cap: Crescimento > 25% é insustentável
            multiplicador_justo = min(g_proj + dy, 30.0)
            fair_value = lpa * multiplicador_justo
            self.resultados['Peter_Lynch'] = {
                'Valor': round(fair_value, 2),
                'Margem': self._calc_margem(fair_value),
                'Multiplicador_Justo': f"{multiplicador_justo:.1f}x"
            }

    # --- DCF CORE OTIMIZADO ---
    def _calcular_dcf_isolado(self, wacc, g1, anos_g1, g_perp=None):
        """
        Núcleo de cálculo do Discounted Cash Flow (2 Estágios).
        
        Args:
            wacc (float): Taxa de desconto.
            g1 (float): Taxa de crescimento no estágio explícito.
            anos_g1 (int): Duração do estágio explícito.
            g_perp (float): Crescimento na perpetuidade (terminal).
            
        Returns:
            float: Valor Justo por Ação (Equity Value per Share).
        """
        fcff_base = self.dados.get('fcff_por_acao')
        if not fcff_base or fcff_base <= 0: return 0 
        
        # Fator Cíclico: Ajusta fluxo base se estivermos em pico de ciclo
        fator_ciclico = self.params.get('fator_ciclico', 1.0)
        fcff_norm = fcff_base * fator_ciclico
        
        ev_sum = 0
        fluxo = fcff_norm
        
        # Estágio 1: Crescimento Explícito
        for t in range(1, int(anos_g1) + 1):
            fluxo *= (1 + g1)
            ev_sum += fluxo / ((1 + wacc) ** t)
        
        # Estágio 2: Perpetuidade com Travas de Sanidade
        if g_perp is None:
            # TRAVA DE COMMODITIES:
            # Se for commodity, g_perp não pode passar da inflação global (2.5%)
            if "COMMODITY" in self.params.get('perfil_raw', str(self.params)): 
                g_padrao = 0.025
            else:
                g_padrao = 0.045 # Brasil Normal
            
            # g_perp nunca > WACC - 1.5%
            g_perp = min(g_padrao, wacc - 0.015)
        
        fluxo_terminal = fluxo * (1 + g_perp)
        denominator = max(0.02, wacc - g_perp) # Floor de 2% no denominador
        tv_gordon = fluxo_terminal / denominator
        
        tv_vp = tv_gordon / ((1 + wacc) ** anos_g1)
        
        enterprise_value = ev_sum + tv_vp
        equity_value = enterprise_value - self.net_debt_per_share
        
        return max(0, equity_value)

    def _dcf_adaptativo(self):
        """
        Configura os parâmetros do DCF com base na Estratégia e executa o cálculo.
        Se FCFF for negativo, tenta usar uma Proxy baseada em EBITDA (se disponível).
        """
        wacc = self.params['wacc_base']
        g1 = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        # FCFF Handling e Proxy
        fcff_raw = self.dados.get('fcff_por_acao', 0)
        ebitda_share = (self.dados.get('ebitda', 0) / self.dados.get('total_acoes', 1))
        
        # Se FCFF negativo, usa proxy 40% EBITDA (mais conservador que 50%)
        using_proxy = False
        if fcff_raw <= 0 and ebitda_share > 0:
            print("   [Valuation] Usando Proxy de Caixa (40% EBITDA).")
            fcff_proxy = ebitda_share * 0.40 
            fcff_raw = fcff_proxy
            using_proxy = True

        self.params['mc_config'] = {
            'base_value': fcff_raw,
            'discount_rate': wacc,
            'growth_rate': g1,
            'years': anos,
            'net_debt': self.net_debt_per_share,
            'is_commodity': "COMMODITY" in str(self.params)
        }
        
        bkp_fcff = self.dados.get('fcff_por_acao')
        self.dados['fcff_por_acao'] = fcff_raw
        
        valor = self._calcular_dcf_isolado(wacc, g1, anos)
        
        self.dados['fcff_por_acao'] = bkp_fcff

        self.resultados['DCF_Adaptativo'] = {
            'Tipo': 'DCF (Fluxo de Caixa)' if not using_proxy else 'DCF (Proxy EBITDA)', 
            'Valor': round(valor, 2),
            'Margem': self._calc_margem(valor),
            'Premissas': {'WACC': f"{wacc:.1%}", 'Cresc.': f"{g1:.1%}"}
        }

    def _monte_carlo_simulation(self):
        """
        Executa 10.000 simulações variando:
        - WACC (Taxa de Desconto).
        - Crescimento (g).
        - Perpetuidade.
        
        Objetivo: Entender a distribuição de probabilidade do valor justo.
        Gera VaR (Value at Risk) e Probabilidade de Upside.
        """
        if not NUMPY_AVAILABLE:
            self.resultados['Monte_Carlo'] = {"Erro": "Biblioteca 'numpy' não instalada."}
            return

        config_mc = self.params.get('mc_config')
        if not config_mc or config_mc.get('base_value', 0) <= 0:
            self.resultados['Monte_Carlo'] = {"Status": "Skipped"}
            return

        N = 10000
        val_base = config_mc['base_value']
        rate_base = config_mc['discount_rate']
        g_base = config_mc['growth_rate']
        years = int(config_mc['years'])
        net_debt = config_mc['net_debt']
        is_commodity = config_mc.get('is_commodity', False)

        # Simulação com Distribuições Ajustadas
        rate_sim = np.random.normal(rate_base, 0.012, N)
        rate_sim = np.maximum(rate_sim, 0.075)
        
        g_sim = np.random.normal(g_base, 0.015, N)
        
        # Perpetuidade Diferenciada
        if is_commodity:
            g_perp_sim = np.random.uniform(0.01, 0.03, N) # 1% a 3% para commodities
        else:
            g_perp_sim = np.random.uniform(0.03, 0.055, N) # 3% a 5.5% para outros

        g_perp_sim = np.minimum(g_perp_sim, rate_sim - 0.01) # Garante denominador positivo
        
        # Vetorização Gordon
        numerator = 1 - ((1 + g_sim) / (1 + rate_sim)) ** years
        denominator = np.where((rate_sim - g_sim) < 0.001, 0.001, rate_sim - g_sim)
        
        pv_stage1 = (val_base * (1 + g_sim)) * (numerator / denominator)
        
        cf_n = val_base * ((1 + g_sim) ** years)
        cf_n1 = cf_n * (1 + g_perp_sim)
        tv_denom = np.where((rate_sim - g_perp_sim) < 0.001, 0.001, rate_sim - g_perp_sim)
        tv = cf_n1 / tv_denom
        pv_tv = tv / ((1 + rate_sim) ** years)
        
        equity_val = np.maximum(0, (pv_stage1 + pv_tv) - net_debt)
        
        self.resultados['Monte_Carlo'] = {
            'Mean': round(np.mean(equity_val), 2),
            'Median': round(np.median(equity_val), 2),
            'VaR_5_Percent': round(np.percentile(equity_val, 5), 2),
            'Upside_95_Percent': round(np.percentile(equity_val, 95), 2),
            'Std_Dev': round(np.std(equity_val), 2),
            'Upside_Prob': f"{np.mean(equity_val > self.dados.get('cotacao', 0)):.1%}",
            'Iterations': N
        }

    def _dcf_sensibilidade(self):
        wacc_base = self.params['wacc_base']
        g_base = self.params['g_estagio1']
        anos = self.params['anos_estagio1']
        
        # Proxy temporário para sensibilidade
        fcff_raw = self.dados.get('fcff_por_acao', 0)
        ebitda_share = (self.dados.get('ebitda', 0) / self.dados.get('total_acoes', 1))
        using_proxy = False
        if fcff_raw <= 0 and ebitda_share > 0:
            self.dados['fcff_por_acao'] = ebitda_share * 0.40
            using_proxy = True
            
        wacc_range = [wacc_base + 0.01, wacc_base, wacc_base - 0.01] 
        g_range = [g_base - 0.01, g_base, g_base + 0.01]           
        
        matriz = []
        for g in g_range:
            linha = []
            for w in wacc_range:
                val = self._calcular_dcf_isolado(w, g, anos)
                linha.append(val)
            matriz.append(linha)
            
        if using_proxy: self.dados['fcff_por_acao'] = fcff_raw

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
        
        # Proxy temporário
        fcff_raw = self.dados.get('fcff_por_acao', 0)
        ebitda_share = (self.dados.get('ebitda', 0) / self.dados.get('total_acoes', 1))
        using_proxy = False
        if fcff_raw <= 0 and ebitda_share > 0:
             self.dados['fcff_por_acao'] = ebitda_share * 0.40
             using_proxy = True

        low, high = -0.15, 0.40 
        implied_g = 0
        for _ in range(30):
            mid = (low + high) / 2
            val = self._calcular_dcf_isolado(wacc, mid, anos)
            if abs(val - target_price) < 0.50: 
                implied_g = mid
                break
            elif val > target_price: high = mid 
            else: low = mid 
            
        if using_proxy: self.dados['fcff_por_acao'] = fcff_raw

        self.resultados['Reverse_DCF'] = {
            'Implied_Growth': implied_g,
            'Target_Price': target_price
        }

    # FINANCIERO E FORENSIC MANTIDOS IGUAIS (mas inclusos no arquivo final)
    def _valuation_financeiro(self):
        ke = self.params['wacc_base'] 
        roe = self.dados.get('roe', 0.15)
        vpa = self.dados.get('vpa_oficial') or self.dados.get('vpa_yahoo') or 1
        payout = 0.50
        g_sustentavel = roe * (1 - payout)
        g_final = min(g_sustentavel, ke - 0.02)
        lpa = self.dados.get('lpa_oficial') or self.dados.get('lpa_yahoo') or 0
        div_projetado = (lpa * payout)
        
        self.params['mc_config'] = {
            'base_value': div_projetado, 'discount_rate': ke,
            'growth_rate': g_final, 'years': 5, 'net_debt': 0 
        }
        denominator = max(0.01, ke - g_final)
        valor_final = ((div_projetado * (1+g_final)) / denominator + (vpa * (roe - g_final) / denominator)) / 2
        
        self.resultados['DCF_Adaptativo'] = {
            'Tipo': 'Modelo de Dividendos (DDM)',
            'Valor': round(valor_final, 2),
            'Margem': self._calc_margem(valor_final),
            'Premissas': {'WACC': f"{ke:.1%}", 'Cresc.': f"{g_final:.1%}", 'ROE': f"{roe:.1%}"}
        }
        self.resultados['Sensibilidade'] = {} 
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
            ratio = (lucro - fco) / abs(lucro)
            if ratio > 0.20:
                flags.append(f"ALERTA: Lucro > FCO em {ratio:.1%}. Accruals?")
                score -= 2
        elif lucro > 0 and fco < 0:
             flags.append("PERIGO: Queima de Caixa Operacional com Lucro Contábil.")
             score -= 4
        self.resultados['Forensic'] = {'Score': max(0, score), 'Flags': flags}