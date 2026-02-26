"""Configurações específicas do processo ICMS Antecipado (ATC): seletores e opção 113011."""

# --- SEFAZ-PI: ICMS Antecipado (DAR Web, processo 113011) ---

# Menu inicial
SELETOR_PI_MENU_ICMS = "a.portalPanelLink"

# Seleção de código (select + opção)
SELETOR_PI_SELECT_CODIGO = 'select[name="j_idt43"]'
VALOR_OPCAO_PI_ANTECIPACAO_PARCIAL = "113011 - ICMS – ANTECIPAÇÃO PARCIAL"

# Formulário geral (formCasoGeral) — IDs com ":" usam [id="..."] (CSS não aceita : em #id)
SELETOR_PI_CAMPO_IE = "#j_idt45"
SELETOR_PI_PERIODO_REFERENCIA = '[id="formCasoGeral:fieldPeriodo"]'
SELETOR_PI_DATA_VENCIMENTO = '[id="formCasoGeral:j_idt64:calendar_input"]'
SELETOR_PI_DATA_PAGAMENTO = '[id="formCasoGeral:j_idt68:calendar_input"]'
SELETOR_PI_VALOR_PRINCIPAL = '[id="formCasoGeral:j_idt70:input"]'

# Botões de ação (span.ui-button-text com texto distinto)
SELETOR_PI_BOTAO_AVANCAR = "span.ui-button-text"  # Avançar (após código ou após IE)
SELETOR_PI_BOTAO_CALCULAR_IMPOSTO = "span.ui-button-text"  # Calcular Imposto (após preencher Valor Principal)
SELETOR_PI_BOTAO_ACAO = "span.ui-button-text"

