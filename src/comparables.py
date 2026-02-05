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
        # 1. Tenta achar match exato de setor no mapa
        for key, lista in self.mapa_pares.items():
            if key in self.setor:
                # Remove o próprio ticker da lista
                pares = [p for p in lista if p not in self.ticker_alvo and p.replace('.SA','') not in self.ticker_alvo]
                return pares[:3] # Retorna max 3
        
        # 2. Se não achar, tenta fallback por palavras-chave
        if 'Bank' in self.setor: return self.mapa_pares['Financial'][:3]
        if 'Electric' in self.setor: return self.mapa_pares['Utilities'][:3]
        
        return []

    def executar_analise(self) -> dict:
        print(f"\n   -> [Comparables] Iniciando Análise Relativa (Setor: {self.setor})")
        lista_pares = self._identificar_pares()
        
        if not lista_pares:
            print("      Aviso: Nenhum par encontrado automaticamente.")
            return None

        resultados = []
        for par in lista_pares:
            d = obter_dados_yahoo(par)
            if d: resultados.append(d)
        
        if not resultados: return None

        # Médias do Setor (Pares)
        # Filtra valores None ou Zero para não sujar a média
        pls = [d.get('pl') for d in resultados if d.get('pl')]
        evs = [d.get('ev_ebitda') for d in resultados if d.get('ev_ebitda')]
        roes = [d.get('roe') for d in resultados if d.get('roe')]
        
        medias = {
            'pl': statistics.mean(pls) if pls else 0,
            'ev_ebitda': statistics.mean(evs) if evs else 0,
            'roe': statistics.mean(roes) if roes else 0
        }

        # Cálculo de Prêmios/Descontos
        return {
            'pares_usados': [d['ticker'] for d in resultados],
            'dados_pares': resultados,
            'medias_setor': medias,
            'premio_pl': self._calc_premio(self.dados_alvo.get('pl'), medias['pl']),
            'premio_evebitda': self._calc_premio(self.dados_alvo.get('ev_ebitda'), medias['ev_ebitda']),
            'premio_roe': self._calc_premio(self.dados_alvo.get('roe'), medias['roe'])
        }

    def _calc_premio(self, alvo, media):
        if not alvo or not media or media == 0: return 0.0
        return ((alvo - media) / media)