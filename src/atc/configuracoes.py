"""Configurações específicas do processo ICMS Antecipado (ATC): seletores e opção 113011."""

# --- SEFAZ-PI: ICMS Antecipado (DAR Web, processo 113011) ---

# Menu inicial
SELETOR_PI_MENU_ICMS = "a.portalPanelLink"

# Seleção de código
SELETOR_PI_SELECT_CODIGO = 'select[name="j_idt43"]'
VALOR_OPCAO_PI_ANTECIPACAO_PARCIAL = "113011 - ICMS – ANTECIPAÇÃO PARCIAL"

# Formulário geral
SELETOR_PI_CAMPO_IE = "#j_idt45"
SELETOR_PI_PERIODO_REFERENCIA = '[id="formCasoGeral:fieldPeriodo"]'
SELETOR_PI_DATA_VENCIMENTO = '[id="formCasoGeral:j_idt64:calendar_input"]'
SELETOR_PI_DATA_PAGAMENTO = '[id="formCasoGeral:j_idt68:calendar_input"]'
SELETOR_PI_VALOR_PRINCIPAL = '[id="formCasoGeral:j_idt70:input"]'

# Ação
SELETOR_PI_BOTAO_AVANCAR = "span.ui-button-text"
SELETOR_PI_BOTAO_CALCULAR_IMPOSTO = "span.ui-button-text"
SELETOR_PI_BOTAO_ACAO = "span.ui-button-text"

