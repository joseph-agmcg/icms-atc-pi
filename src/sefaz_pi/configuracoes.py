"""
Constantes, seletores, URLs e timeouts do projeto ICMS Antecipado (SEFAZ-PI).
Carrega variáveis de ambiente do .env — nenhum outro módulo deve usar load_dotenv ou os.environ.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- URL do portal ---
URL_PORTAL_DARWEB_SEFAZ_PI = "https://webas.sefaz.pi.gov.br/darweb/faces/views/index.xhtml"

# --- SEFAZ-PI: ICMS Antecipado (DAR Web) ---
# Menu inicial
SELETOR_PI_MENU_ICMS = "a.portalPanelLink"
# Seleção de código (select + opção)
SELETOR_PI_SELECT_CODIGO = "select[name=\"j_idt43\"]"
VALOR_OPCAO_PI_ANTECIPACAO_PARCIAL = "113011 - ICMS – ANTECIPAÇÃO PARCIAL"
# Formulário geral (formCasoGeral) — IDs com ":" usam [id="..."] (CSS não aceita : em #id)
SELETOR_PI_CAMPO_IE = "#j_idt45"
SELETOR_PI_PERIODO_REFERENCIA = "[id=\"formCasoGeral:fieldPeriodo\"]"
SELETOR_PI_DATA_VENCIMENTO = "[id=\"formCasoGeral:j_idt64:calendar_input\"]"
SELETOR_PI_DATA_PAGAMENTO = "[id=\"formCasoGeral:j_idt68:calendar_input\"]"
SELETOR_PI_VALOR_PRINCIPAL = "[id=\"formCasoGeral:j_idt70:input\"]"
# Botões de ação (span.ui-button-text com texto distinto)
SELETOR_PI_BOTAO_AVANCAR = "span.ui-button-text"  # Avançar (após código ou após IE)
SELETOR_PI_BOTAO_CALCULAR_IMPOSTO = "span.ui-button-text"  # Calcular Imposto (após preencher Valor Principal)
SELETOR_PI_BOTAO_ACAO = "span.ui-button-text"

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
