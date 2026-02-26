"""Configurações específicas do processo ICMS Normal (Imposto, Juros e Multa): código 113000."""

# --- SEFAZ-PI: ICMS Normal (DAR Web, 113000) ---

# Menu inicial
SELETOR_PI_MENU_ICMS = "a.portalPanelLink"

# Seleção de código
SELETOR_PI_SELECT_CODIGO = 'select[name="j_idt43"]'
VALOR_OPCAO_PI_IMPOSTO_JUROS_MULTA = "113000 - ICMS - APURAÇÃO NORMAL"

# IE e substituição tributária
SELETOR_PI_CAMPO_IE = "#fieldInscricaoEstadual"
SELETOR_PI_SUBSTITUICAO = "#cmbSubstituicao"
VALOR_SUBSTITUICAO_NAO = "NÃO"

# Botão Avançar
SELETOR_PI_BOTAO_AVANCAR = "span.ui-button-text"

# Formulário geral
SELETOR_PI_PERIODO_REFERENCIA = '[id="formCasoGeral:j_idt67"]'
SELETOR_PI_DATA_VENCIMENTO = '[id="formCasoGeral:j_idt70:calendar_input"]'
SELETOR_PI_DATA_PAGAMENTO = '[id="formCasoGeral:j_idt75:calendar_input"]'
SELETOR_PI_VALOR_PRINCIPAL = '[id="formCasoGeral:j_idt78:input"]'

# Ação
SELETOR_PI_BOTAO_CALCULAR_IMPOSTO = "span.ui-button-text"
