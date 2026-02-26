"""Módulo de navegação e interação com o browser."""

from atc.navegacao.acoes_pagina import (
    aguardar_pagina_carregar,
    clicar_em_elemento_por_texto,
    clicar_em_link_por_texto,
    preencher_campo_data_mascarado,
    tirar_captura_de_tela_em_erro,
)

__all__ = [
    "aguardar_pagina_carregar",
    "clicar_em_elemento_por_texto",
    "clicar_em_link_por_texto",
    "preencher_campo_data_mascarado",
    "tirar_captura_de_tela_em_erro",
]
