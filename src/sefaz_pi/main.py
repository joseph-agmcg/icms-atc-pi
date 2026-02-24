"""
Ponto de entrada da aplicação ICMS Antecipado (SEFAZ-PI).
Sem argumentos: abre a interface gráfica (Excel + lote).
Com --excel <caminho>: executa a automação em lote para o arquivo informado (opcional: --headless).
"""

import argparse
import asyncio
import sys
from pathlib import Path

from sefaz_pi.automacao_sefaz_pi import AutomacaoAntecipacaoParcialPI
from sefaz_pi.excel_filiais import extrair_todos_os_dados, obter_dados_para_dae
from sefaz_pi.gui_app import main as gui_main
from sefaz_pi.logger import configurar_logger_da_aplicacao

logger = configurar_logger_da_aplicacao(__name__)


async def _rodar_lote(caminho_excel: Path, headless: bool) -> tuple[int, int]:
    """Carrega o Excel, executa o fluxo PI e retorna (sucesso, erro)."""
    linhas, nome_para_indice, mes_ref, ano_ref = extrair_todos_os_dados(caminho_excel)
    lista_dados = obter_dados_para_dae(
        linhas, nome_para_indice, mes_ref=mes_ref, ano_ref=ano_ref
    )
    if not lista_dados:
        logger.warning("Nenhum registro para processar no arquivo.")
        return 0, 0
    automacao = AutomacaoAntecipacaoParcialPI(headless=headless)
    ies_ok, ies_erro = await automacao.executar_fluxo_por_ie_pi(lista_dados)
    return len(ies_ok), len(ies_erro)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ICMS Antecipado (SEFAZ-PI). GUI ou lote por Excel."
    )
    parser.add_argument(
        "--excel",
        type=Path,
        metavar="ARQUIVO",
        help="Caminho do arquivo .xlsx para executar automação em lote (sem abrir GUI).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar navegador em modo headless (apenas com --excel).",
    )
    args = parser.parse_args()

    if args.excel is not None:
        if not args.excel.exists():
            logger.error("Arquivo não encontrado: %s", args.excel)
            sys.exit(1)
        logger.info("Executando lote: %s (headless=%s)", args.excel, args.headless)
        try:
            ok, err = asyncio.run(_rodar_lote(args.excel, args.headless))
            logger.info("Concluído: %d sucesso, %d erro.", ok, err)
        except KeyboardInterrupt:
            logger.warning("Interrompido pelo usuário.")
            sys.exit(130)
        except Exception:
            logger.exception("Falha na execução do lote.")
            sys.exit(1)
        return

    logger.info("Iniciando interface ICMS Antecipado.")
    try:
        gui_main()
    except KeyboardInterrupt:
        logger.warning("Interface encerrada pelo usuário.")
    logger.info("Encerramento.")


if __name__ == "__main__":
    main()
    sys.exit(0)
