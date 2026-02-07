AgFin - Agente Financeiro com IA (V12) 📈🤖

AgFin é um sistema avançado de análise fundamentalista e valuation automatizado. Ele combina a precisão matemática de modelos financeiros clássicos (DCF, Graham, Bazin) com a capacidade cognitiva de Grandes Modelos de Linguagem (LLMs - Google Gemini) para gerar teses de investimento de nível institucional.

O sistema não olha apenas para o preço; ele entende o contexto macroeconômico, a qualidade do negócio (Moat) e os riscos ocultos em relatórios contábeis.

🚀 Funcionalidades Principais

🧠 Inteligência & Auditoria

Leitura Inteligente de PDFs: O agente lê relatórios anuais/trimestrais (ITR/DFP), focando estrategicamente nas mensagens da administração e notas explicativas para extrair endividamento real e riscos jurídicos.

Auditoria Forense: Algoritmo que cruza Fluxo de Caixa Operacional vs. Lucro Líquido para detectar sinais de contabilidade agressiva (Accruals).

Economic Moat Score: Classificação qualitativa da vantagem competitiva da empresa (0 a 10).

📊 Motores de Valuation (Matemática Rigorosa)

Fluxo de Caixa Descontado (DCF): Modelo adaptativo que ajusta projeções baseadas no ciclo (Commodity vs. Growth vs. Utilities).

Ajuste Global Player: Redução de Risco País para exportadoras (ex: WEG, Vale).

Trava de Commodities: Limitação de crescimento perpétuo para empresas cíclicas.

Modelo de Dividendos (DDM): Engine específica para Bancos e Seguradoras (Gordon + Justified P/VP).

Simulação de Monte Carlo: 10.000 iterações para gerar intervalos de confiança, VaR (Value at Risk) e probabilidade de upside.

Reverse DCF: Calcula o crescimento implícito que o mercado está a precificar no valor atual da ação.

Valuation Relativo: Comparação de múltiplos (P/L, EV/EBITDA, P/VP) com pares do setor.

Modelos Clássicos: Graham (Valor Intrínseco), Bazin (Preço Teto de Dividendos) e Peter Lynch (PEG Ratio).

🌎 Contexto Macroeconômico

Integração com Banco Central: Coleta automática de Selic e IPCA em tempo real.

WACC Dinâmico: Cálculo do Custo Médio Ponderado de Capital ajustado ao Risco Brasil e ao ciclo de juros (Contracionista/Expansionista).

📑 Saída (Output)

Relatório PDF Profissional: Gera um PDF completo com Dashboard, Tabelas de Valuation, Heatmaps de Sensibilidade e o Memorando de Investimento escrito pela IA.

🛠️ Instalação e Configuração

Pré-requisitos

Python 3.10 ou superior.

Uma chave de API do Google Gemini (Google AI Studio).

1. Clonar e Instalar Dependências

# Clone o repositório
git clone [https://github.com/seu-usuario/AgFin.git](https://github.com/seu-usuario/AgFin.git)
cd AgFin

# Instale as bibliotecas necessárias
pip install google-genai yfinance pypdf reportlab numpy requests


2. Configurar a API Key

Importante: Por segurança, recomenda-se usar variáveis de ambiente.

No Linux/Mac:

export GOOGLE_API_KEY="SUA_CHAVE_AQUI"


No Windows (PowerShell):

$env:GOOGLE_API_KEY="SUA_CHAVE_AQUI"


Alternativamente (apenas para testes locais), você pode editar o arquivo config.py, mas cuidado para não commitar sua chave.

▶️ Como Usar

Execute o arquivo principal:

python main.py


O sistema irá solicitar:

Ticker da Ação: (ex: WEGE3, PETR4, ITUB4). O sufixo .SA é adicionado automaticamente.

Caminho do PDF (Opcional): Caminho local para um relatório da empresa (ex: C:\Docs\Relatorio_WEG_2025.pdf). Se deixar em branco, o agente usará apenas dados do Yahoo Finance.

Validação Interativa: O sistema pedirá confirmação se encontrar dados críticos zerados ou suspeitos.

Resultado:
Ao final, o sistema exibe o parecer no terminal e gera um arquivo PDF na pasta raiz: Relatorio_Deep_Analysis_[TICKER]_[DATA].pdf.

🗂️ Estrutura do Projeto

AgFin/
│
├── main.py              # Ponto de entrada (Orquestrador)
├── config.py            # Configurações e Chaves de API
├── verify_math.py       # Script de teste unitário dos cálculos
│
├── src/
│   ├── ai_agent.py      # Integração com Google Gemini (Auditoria e Redação)
│   ├── data.py          # Coleta (Yahoo Finance) e Leitura de PDF
│   ├── macro.py         # Dados do Banco Central e Cálculo de Ke/Risk Free
│   ├── strategy.py      # Definição de Perfil (Growth/Value) e WACC
│   ├── valuation.py     # Motores Matemáticos (DCF, Monte Carlo, etc.)
│   ├── comparables.py   # Análise de Múltiplos Relativos
│   ├── forensic.py      # (Integrado no Valuation) Análise de Qualidade Contábil
│   ├── report.py        # Geração do PDF com ReportLab
│   └── memorial.py      # Log de auditoria dos cálculos
│
└── README.md            # Documentação


⚠️ Isenção de Responsabilidade (Disclaimer)

Esta ferramenta é apenas para fins educacionais e informativos. O AgFin utiliza inteligência artificial e modelos matemáticos que podem conter imprecisões.

Não é recomendação de investimento.

Os preços-alvo gerados são estimativas baseadas em premissas que podem não se concretizar.

Sempre realize sua própria Due Diligence antes de investir.

Desenvolvido como um assistente para investidores que buscam profundidade analítica.