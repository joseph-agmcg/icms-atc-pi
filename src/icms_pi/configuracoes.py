"""Constantes e configurações comuns do sistema ICMS-PI.

Inclui: URL do portal DAR Web, timeouts, configurações de lote, pastas de saída/erro.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- URL do portal ---
URL_PORTAL_DARWEB_SEFAZ_PI = "https://webas.sefaz.pi.gov.br/darweb/faces/views/index.xhtml"

# --- Timeouts (milissegundos) ---
TIMEOUT_PAGINA_CARREGAR_MS = 30_000
TIMEOUT_AGUARDAR_ELEMENTO_MS = 15_000

# --- Configurações de lote ---
INTERVALO_ENTRE_EXECUCOES_MS = 10_000
QUANTIDADE_POR_VEZ = 1

# --- Pastas (variáveis de ambiente) ---
PASTA_SAIDA_RESULTADOS = os.getenv("PASTA_SAIDA_RESULTADOS", "resultados")
PASTA_CAPTURAS_DE_TELA_ERROS = os.getenv("PASTA_CAPTURAS_DE_TELA_ERROS", "capturas_erros")

_raiz_projeto = Path(__file__).resolve().parent.parent.parent
PASTA_SAIDA_RESULTADOS_ABSOLUTA = _raiz_projeto / PASTA_SAIDA_RESULTADOS
PASTA_CAPTURAS_ERROS_ABSOLUTA = _raiz_projeto / PASTA_CAPTURAS_DE_TELA_ERROS

