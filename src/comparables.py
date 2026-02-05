import statistics
import config
from src.data import obter_dados_yahoo

class AnalistaRelativo:
    def __init__(self, ticker_alvo: str, setor_alvo: str, dados_alvo: dict):
        self.ticker_alvo = ticker_alvo
        self.setor = setor_alvo
        self.dados_alvo = dados_alvo
        self.mapa_pares = config.SECTOR_PEERS_MAP

    def _identificar_pares(self) -> list:
        # Tenta achar match exato de setor no mapa
        for key, lista in self.mapa_pares.items():
            if key in self.setor:
                # Remove o próprio ticker e variações (ex: PETR3 vs PETR4)
                root_ticker = self.ticker_alvo[:4]
                pares = [p for p in lista if root_ticker not in p]
                return pares[:4] # Aumentado para até 4 pares para melhor estatística
        
        # Fallback
        if 'Bank' in self.setor or 'Financial' in self.setor: return self.mapa_pares['Financial'][:4]
        if 'Electric' in self.setor: return self.mapa_pares['Utilities'][:4]
        return []

    def executar_analise(self) -> dict:
        print(f"\n   -> [Comparables] Iniciando Valuation Relativo (Setor: {self.setor})")
        lista_pares = self._identificar_pares()
        
        if not lista_pares:
            print("      Aviso: Nenhum par encontrado automaticamente.")
            return None

        resultados_pares = []
        for par in lista_pares:
            d = obter_dados_yahoo(par)
            if d: resultados_pares.append(d)
        
        if not resultados_pares: return None

        # --- 1. CÁLCULO DAS MÉDIAS DO SETOR ---
        # Usamos listas limpas para evitar None ou zeros que distorcem a média
        def media_clean(chave):
            vals = [d.get(chave) for d in resultados_pares if d.get(chave) is not None and d.get(chave) != 0]
            return statistics.mean(vals) if vals else 0

        avg_pl = media_clean('pl')
        avg_evebitda = media_clean('ev_ebitda')
        avg_pvp = media_clean('pvp')
        avg_roe = media_clean('roe')
        
        medias = {
            'pl': avg_pl,
            'ev_ebitda': avg_evebitda,
            'pvp': avg_pvp,
            'roe': avg_roe
        }

        # --- 2. VALUATION IMPLÍCITO (PREÇO JUSTO VIA MÚLTIPLOS) ---
        # Matemática: Se a empresa negociasse na média do setor, quanto ela valeria?
        
        precos_implicitos = {}
        
        # A) Via P/L: Preço = LPA * P/L_Médio
        lpa = self.dados_alvo.get('lpa_yahoo')
        if lpa and lpa > 0 and avg_pl > 0:
            precos_implicitos['Target_PL'] = lpa * avg_pl
        
        # B) Via P/VP: Preço = VPA * P/VP_Médio
        vpa = self.dados_alvo.get('vpa_yahoo')
        if vpa and vpa > 0 and avg_pvp > 0:
            precos_implicitos['Target_PVP'] = vpa * avg_pvp

        # C) Via EV/EBITDA (Mais complexo):
        # EV_Implícito = EBITDA_Alvo * EV/EBITDA_Médio
        # Equity_Value = EV_Implícito - Dívida_Líquida
        # Preço = Equity_Value / Ações
        
        # Recalcula EBITDA do alvo (aproximado) se não tiver explícito
        # EBITDA = EV / (EV/EBITDA) ou operando reverso, mas vamos usar dados diretos se possível
        # Como o Yahoo não dá EBITDA por ação direto sempre, derivamos:
        # EBITDA Total ~ (EBITDA Margin * Revenue) ou via Enterprise Value
        
        # Tentativa simplificada via dados per share calculados no src/data.py
        # Vamos assumir que temos EV/EBITDA do alvo. 
        # EBITDA_implied = (EV_Alvo / EV_EBITDA_Alvo) -> Se tivermos esses dados
        
        # Abordagem robusta: Usar o EV/EBITDA do alvo para achar o EBITDA implícito atual, 
        # depois aplicar o múltiplo do setor.
        ev_ebitda_alvo = self.dados_alvo.get('ev_ebitda')
        divida_liq_acao = self.dados_alvo.get('divida_liquida_por_acao', 0)
        cotacao = self.dados_alvo.get('cotacao', 0)
        
        if ev_ebitda_alvo and ev_ebitda_alvo > 0 and avg_evebitda > 0:
            # Engenharia reversa para achar "EBITDA por ação" aproximado (proxy)
            # EV_por_acao = Cotacao + Divida_Liq_por_acao
            ev_por_acao_atual = cotacao + divida_liq_acao
            ebitda_por_acao = ev_por_acao_atual / ev_ebitda_alvo
            
            # Agora projeta
            ev_por_acao_justo = ebitda_por_acao * avg_evebitda
            preco_justo_evebitda = ev_por_acao_justo - divida_liq_acao
            precos_implicitos['Target_EV_EBITDA'] = max(0, preco_justo_evebitda) # Não pode ser negativo

        return {
            'pares_usados': [d['ticker'] for d in resultados_pares],
            'dados_pares': resultados_pares,
            'medias_setor': medias,
            'precos_implicitos': precos_implicitos,
            # Métricas relativas para o texto da IA
            'desconto_pl': self._calc_diff(self.dados_alvo.get('pl'), avg_pl),
            'desconto_evebitda': self._calc_diff(self.dados_alvo.get('ev_ebitda'), avg_evebitda)
        }

    def _calc_diff(self, alvo, media):
        if not alvo or not media or media == 0: return 0.0
        # Retorna negativo se alvo < media (Desconto), positivo se prêmio
        return ((alvo - media) / media)