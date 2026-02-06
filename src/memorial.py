import os
from datetime import datetime
import json

class MemorialLog:
    def __init__(self, ticker):
        self.ticker = ticker
        self.sections = []
        self.data_store = {}

    def add_section(self, title, content):
        self.sections.append(f"## {title}\n\n{content}\n")

    def register_data(self, key, data):
        self.data_store[key] = data

    def gerar_markdown(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md = [f"# Memorial de Cálculo - Auditoria do Agente\n"]
        md.append(f"**Ticker:** {self.ticker}")
        md.append(f"**Data:** {timestamp}")
        md.append(f"**Versão do Agente:** 2.0 (Audit Mode)\n")
        
        md.append("---\n")
        
        # 1. Input Data Audit
        md.append("## 1. Auditoria de Inputs (Yahoo Finance & PDF)\n")
        dados = self.data_store.get('dados_yahoo', {})
        md.append("### Dados Fundamentais Coletados")
        md.append("| Métrica | Valor | Descrição |")
        md.append("|---|---|---|")
        for k, v in dados.items():
            val_fmt = v
            if isinstance(v, float):
                val_fmt = f"{v:.4f}"
            md.append(f"| {k} | {val_fmt} | - |")
        md.append("\n")

        # 2. Macro & Strategy Audit
        md.append("## 2. Auditoria Macro & Estratégia\n")
        params = self.data_store.get('params_estrategia', {})
        if params:
            md.append(f"- **Perfil Definido:** {params.get('engine', 'N/A')}")
            capm = params.get('capm_data', {})
            md.append("### Cálculo do Custo de Capital Próprio (Ke - CAPM)")
            md.append(f"Formula: $Ke = Rf + Beta \\times ERP + Risk_{{Country}}$")
            md.append(f"- Rf (Risk Free): {capm.get('rf_usado')}")
            md.append(f"- Beta: {capm.get('beta_usado')}")
            md.append(f"- ERP (Equity Risk Premium): {capm.get('erp_usado')}")
            md.append(f"- Country Risk: {capm.get('risk_country_usado')}")
            md.append(f"- **Ke Calculado:** {capm.get('ke')}")
            
            wacc_comps = params.get('wacc_components', {})
            if wacc_comps:
                md.append("\n### Cálculo do WACC")
                md.append(f"- Peso Dívida (Wd): {self._fmt_pct(wacc_comps.get('Wd'))}")
                md.append(f"- Peso Equity (We): {self._fmt_pct(wacc_comps.get('We'))}")
                md.append(f"- Custo Dívida Nominal: {self._fmt_pct(dados.get('custo_divida_bruto'))}")
                md.append(f"- Tax Rate Efetiva: {self._fmt_pct(wacc_comps.get('TaxRate'))}")
                md.append(f"- **WACC Final:** {self._fmt_pct(params.get('wacc_base'))}")
        
        # 3. Valuation Trace
        md.append("\n## 3. Rastreabilidade do Valuation (DCF)\n")
        valuation = self.data_store.get('valuation_results', {})
        dcf = valuation.get('DCF_Adaptativo', {})
        if dcf:
            md.append(f"**Valor Justo Final:** R$ {dcf.get('Valor')}")
            md.append(f"**Premissas Usadas:** {dcf.get('Premissas')}")
            # Note: Detailed cash flows are not currently exposed by valuation.py return dict.
            # We would need to modify valuation.py to return 'debug_data' to show year-by-year flows.
            # For now, we show what we have.
        
        mc = valuation.get('Monte_Carlo', {})
        if mc:
            md.append("\n### Auditoria Monte Carlo")
            md.append("Resultados Estatísticos:")
            md.append(json.dumps(mc, indent=2))

        # 4. Auditoria LLM
        md.append("\n## 4. Auditoria da IA (Prompt & Output)\n")
        md.append("### Contexto Enviado ao LLM (Prompt)")
        md.append("```text")
        md.append(self.data_store.get('llm_prompt', 'N/A'))
        md.append("```\n")
        
        md.append("### Resposta Recebida (Raw)")
        md.append(self.data_store.get('llm_response', 'N/A'))

        return "\n".join(md)

    def _fmt_pct(self, val):
        if val is None: return "N/A"
        try: return f"{val:.2%}"
        except: return str(val)

    def salvar(self):
        filename = f"Memorial_Calculo_{self.ticker}.md"
        content = self.gerar_markdown()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[AUDIT] Memorial de cálculo salvo em: {os.path.abspath(filename)}")
