
class ConsensusCalculator:
    """
    Calculadora de Consenso de Valuation.
    
    Responsabilidade:
    Agregar os resultados de diferentes modelos (DCF, Graham, Bazin, Múltiplos)
    e gerar um "Fair Value" ponderado, reduzindo o viés de um único método.
    """
    def __init__(self, valuation_results: dict, comparables_results: dict, weights: dict):
        self.val_res = valuation_results
        self.comp_res = comparables_results
        self.weights = weights
        self.consensus = {}

    def calculate(self) -> dict:
        """
        Executa a ponderação dos valores.
        """
        values = []
        
        # 1. Coleta Valores do DCF (Intrinsic)
        dcf_val = 0
        if 'DCF_Adaptativo' in self.val_res:
             dcf_val = self.val_res['DCF_Adaptativo'].get('Valor', 0)
        
        # 2. Coleta Valores Clássicos (Classic)
        # Média entre Graham e Bazin (se disponíveis)
        classic_vals = []
        graham = self.val_res.get('Graham', {}).get('Valor', 0)
        if graham > 0: classic_vals.append(graham)
        
        bazin = self.val_res.get('Bazin', {}).get('Preco_Teto', 0)
        if bazin > 0: classic_vals.append(bazin)
        
        classic_avg = sum(classic_vals) / len(classic_vals) if classic_vals else 0
        
        # 3. Coleta Valores Relativos (Multiples)
        # Média dos preços implícitos (Target_PL, Target_EV_EBITDA, Target_PVP)
        rel_vals = []
        if self.comp_res and 'precos_implicitos' in self.comp_res:
            pi = self.comp_res['precos_implicitos']
            for k, v in pi.items():
                if v and v > 0: rel_vals.append(v)
                
        rel_avg = sum(rel_vals) / len(rel_vals) if rel_vals else 0

        # --- SANITY CHECK (Travas de Segurança) ---
        # Impede que um método distorcido (ex: erro de base dados) contamine o consenso
        valid_values = [v for v in [dcf_val, classic_avg, rel_avg] if v > 0]
        if valid_values:
            mediana = sorted(valid_values)[len(valid_values)//2]
            limite_superior = mediana * 2.5 # Teto: 250% da mediana
            
            if dcf_val > limite_superior: 
                dcf_val = limite_superior
            if classic_avg > limite_superior: 
                classic_avg = limite_superior
            if rel_avg > limite_superior: 
                rel_avg = limite_superior

        # --- CÁLCULO PONDERADO ---
        # Normaliza pesos se algum componente for 0
        w_dcf = self.weights.get('DCF', 0.4)
        w_cls = self.weights.get('Classic', 0.2)
        w_mul = self.weights.get('Multiples', 0.4)
        
        final_value = 0
        total_weight = 0
        
        if dcf_val > 0:
            final_value += dcf_val * w_dcf
            total_weight += w_dcf
            
        if classic_avg > 0:
            final_value += classic_avg * w_cls
            total_weight += w_cls
            
        if rel_avg > 0:
            final_value += rel_avg * w_mul
            total_weight += w_mul
            
        # Se não tiver nada, retorna 0
        consensus_price = 0
        if total_weight > 0:
            consensus_price = final_value / total_weight
            
        self.consensus = {
            'Consensus_Price': round(consensus_price, 2),
            'Breakdown': {
                'DCF_Value': round(dcf_val, 2),
                'Classic_Avg': round(classic_avg, 2),
                'Multiples_Avg': round(rel_avg, 2)
            },
            'Weights_Used': {
                'DCF': w_dcf,
                'Classic': w_cls,
                'Multiples': w_mul
            },
            'Drivers': self._analisar_drivers(dcf_val, classic_avg, rel_avg)
        }
        
        return self.consensus

    def _analisar_drivers(self, dcf, classic, relative):
        drivers = []
        if dcf > relative * 1.2:
            drivers.append("DCF (Crescimento Longo Prazo) puxa valor pra cima.")
        elif relative > dcf * 1.2:
            drivers.append("Múltiplos de Mercado sugerem valor maior que fundamentos implícitos.")
        
        if classic > dcf * 1.2:
            drivers.append("Ativos/Dividendos (Bazin/Graham) dão suporte forte ao preço.")
            
        return drivers
