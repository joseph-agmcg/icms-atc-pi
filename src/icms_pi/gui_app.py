"""Interface desktop com CustomTkinter para o sistema ICMS-PI (ATC, NORMAL, DIFAL)."""

import asyncio
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from icms_pi import configuracoes
from icms_pi.excel_filiais import (
    extrair_todos_os_dados,
    obter_dados_para_dae,
    obter_ies_dos_dados,
    _obter_chave_ie,
)
from icms_pi.logger import configurar_logger_da_aplicacao
from atc.automacao_sefaz_pi import AutomacaoAntecipacaoParcialPI, _valor_atc_invalido


logger = configurar_logger_da_aplicacao(__name__)


PROCESSOS_ICMS_PI: list[tuple[str, str]] = [
    ("antecipado", "ICMS Antecipado PI"),
    ("normal", "ICMS Normal PI"),
    ("difal", "ICMS Difal PI"),
]

_PROCESSO_POR_ID: dict[str, str] = {pid: nome for pid, nome in PROCESSOS_ICMS_PI}


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def _nome_processo_legivel(processo_id: str) -> str:
    return _PROCESSO_POR_ID.get(processo_id, processo_id)


def _ie_para_exibicao(ie: str | None) -> str:
    if ie is None:
        return ""
    s = str(ie).strip()
    return s.replace(".", "").replace("-", "").replace("/", "")


def _formato_intervalo_ms(ms: int) -> str:
    if ms >= 60_000:
        return f"{ms // 60_000} min"
    if ms >= 1_000:
        return f"{ms // 1_000} s"
    return f"{ms} ms"


def _contar_executaveis_ignoradas(
    lista_dados: list[dict[str, object]],
) -> tuple[int, int]:
    executaveis = sum(
        1 for item in lista_dados if not _valor_atc_invalido(item.get("valor_atc"))
    )
    return executaveis, len(lista_dados) - executaveis


# ---------------------------------------------------------------------------
# Execução em background (thread separada)
# ---------------------------------------------------------------------------

def _executar_lote_em_background(
    lista_dados: list[dict[str, object]],
    processos_ids: list[str],
    headless: bool,
    result_callback=None,
) -> None:
    if not processos_ids:
        return

    total = len(lista_dados)
    intervalo_txt = _formato_intervalo_ms(configuracoes.INTERVALO_ENTRE_EXECUCOES_MS)
    logger.info(
        "Iniciando lote: %d registros, processos=%s, intervalo=%s, headless=%s",
        total, processos_ids, intervalo_txt, headless,
    )

    def _worker() -> None:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            ies_ok: list[str] = []
            ies_erro: list[tuple[str, str]] = []

            async def _rodar_antecipado() -> None:
                automacao = AutomacaoAntecipacaoParcialPI(headless=headless)
                ok, erro = await automacao.executar_fluxo_por_ie_pi(lista_dados)
                ies_ok.extend(ok)
                ies_erro.extend(erro)

            if "antecipado" in processos_ids:
                loop.run_until_complete(_rodar_antecipado())

            if result_callback is not None:
                result_callback(ies_ok, ies_erro)
        finally:
            try:
                loop.close()
            except Exception:
                logger.exception("Falha ao fechar event loop da GUI.")

    threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Janela de visualização dos dados extraídos
# ---------------------------------------------------------------------------

def _mostrar_janela_dados_extraidos(
    parent: ctk.CTk,
    caminho: Path,
    dados_extraidos: list[dict[str, object]],
    nomes_colunas: list[str],
    nome_para_indice: dict[str, int],
) -> None:
    if not dados_extraidos or not nomes_colunas:
        messagebox.showinfo("Dados", "Nenhum dado extraído para exibir.")
        return

    janela = ctk.CTkToplevel(parent)
    janela.title("Dados extraídos do Excel")
    janela.geometry("920x520")
    janela.minsize(500, 340)

    ctk.CTkLabel(
        janela,
        text=(
            f"Arquivo: {caminho.name}  |  "
            f"{len(dados_extraidos)} linhas  |  "
            f"{len(nomes_colunas)} colunas"
        ),
        font=ctk.CTkFont(size=12),
    ).pack(pady=8)

    texto = ctk.CTkTextbox(
        janela, font=ctk.CTkFont(family="Consolas", size=12), wrap="none",
    )
    texto.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    colunas = nomes_colunas
    larguras = [max(len(str(col)), 4) for col in colunas]
    for i, col in enumerate(colunas):
        larguras[i] = max(
            larguras[i],
            max(
                (len(str(linha.get(col, "") or "")) for linha in dados_extraidos[:100]),
                default=0,
            ),
        )
        larguras[i] = min(larguras[i], 30)

    def _cel(s: object, w: int) -> str:
        ss = "" if s is None else str(s).strip()
        return (ss[: w - 2] + "..") if len(ss) > w else ss.ljust(w)

    ie_key = _obter_chave_ie(nome_para_indice)

    linha_cab = " | ".join(_cel(col, larguras[i]) for i, col in enumerate(colunas))
    sep = "-+-".join("-" * w for w in larguras)
    linhas_txt = [linha_cab, sep]
    for linha in dados_extraidos:
        def _valor_celula(col: str, idx: int, _linha=linha) -> str:
            v = _linha.get(col)
            if ie_key and col == ie_key and v is not None:
                return _cel(_ie_para_exibicao(str(v)), larguras[idx])
            return _cel(v, larguras[idx])
        linhas_txt.append(
            " | ".join(_valor_celula(col, i) for i, col in enumerate(colunas))
        )

    texto.insert("1.0", "\n".join(linhas_txt))
    texto.configure(state="disabled")


# ---------------------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    """Janela principal da aplicação ICMS-PI (GUI unificada)."""

    _MODO_TABELA = "tabela"
    _MODO_SELECAO = "selecao"

    def __init__(self) -> None:
        super().__init__()
        self.title("ICMS-PI — Automação SEFAZ-PI")
        self.geometry("1060x700")
        self.minsize(820, 580)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._caminho_excel: Path | None = None
        self._dados_extraidos: list[dict[str, object]] = []
        self._lista_dados: list[dict[str, object]] = []
        self._nomes_colunas: list[str] = []
        self._nome_para_indice: dict[str, int] = {}
        self._mes_ref: int = 0
        self._ano_ref: int = 0
        self._executando = False

        self._modo_ies = self._MODO_TABELA
        self._vars_selecao: list[tuple[dict[str, object], ctk.BooleanVar]] = []

        self._construir_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _construir_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._criar_cabecalho()
        self._criar_painel_arquivo()
        self._criar_area_central()
        self._criar_barra_status()

    def _criar_cabecalho(self) -> None:
        frame = ctk.CTkFrame(self, corner_radius=0, height=52)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="ICMS-PI",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=(20, 8), pady=10)

        ctk.CTkLabel(
            frame,
            text="Automação SEFAZ-PI  •  ATC / Normal / Difal",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).grid(row=0, column=1, sticky="w", padx=4)

    def _criar_painel_arquivo(self) -> None:
        frame = ctk.CTkFrame(self, corner_radius=8)
        frame.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 0))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="Planilha Excel:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(14, 8), pady=12)

        self._label_arquivo = ctk.CTkLabel(
            frame, text="Nenhum arquivo selecionado.",
            font=ctk.CTkFont(size=12), text_color="gray", anchor="w",
        )
        self._label_arquivo.grid(row=0, column=1, sticky="ew", padx=4)

        self._btn_ver_dados = ctk.CTkButton(
            frame, text="Ver dados extraídos", width=160,
            command=self._ao_ver_dados, state="disabled",
        )
        self._btn_ver_dados.grid(row=0, column=2, padx=(4, 4), pady=12)
        self._btn_ver_dados.grid_remove()

        self._btn_abrir = ctk.CTkButton(
            frame, text="Selecionar arquivo…", width=140,
            command=self._selecionar_arquivo,
        )
        self._btn_abrir.grid(row=0, column=3, padx=(4, 14), pady=12)

    def _criar_area_central(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=2, column=0, sticky="nsew", padx=14, pady=10)
        container.grid_columnconfigure(0, weight=3, uniform="col")
        container.grid_columnconfigure(1, weight=2, uniform="col")
        container.grid_rowconfigure(0, weight=1)

        col_esq = ctk.CTkFrame(container, fg_color="transparent")
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        col_esq.grid_rowconfigure(1, weight=1)
        col_esq.grid_columnconfigure(0, weight=1)

        self._criar_resumo(col_esq)
        self._criar_painel_ies(col_esq)

        col_dir = ctk.CTkFrame(container, fg_color="transparent")
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        col_dir.grid_rowconfigure(1, weight=1)
        col_dir.grid_columnconfigure(0, weight=1)

        self._criar_painel_processos(col_dir)
        self._criar_painel_log(col_dir)

    # --- Cards de resumo ---
    def _criar_resumo(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._lbl_periodo = self._card_info(frame, "Período", "—", 0)
        self._lbl_total = self._card_info(frame, "Total IEs", "0", 1)
        self._lbl_exec = self._card_info(frame, "Executáveis", "0", 2)
        self._lbl_ignor = self._card_info(frame, "Ignoradas", "0", 3)

    def _card_info(
        self, parent: ctk.CTkFrame, titulo: str, valor: str, col: int,
    ) -> ctk.CTkLabel:
        wrapper = ctk.CTkFrame(parent, corner_radius=6)
        wrapper.grid(row=0, column=col, padx=6, pady=8, sticky="ew")
        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrapper, text=titulo, font=ctk.CTkFont(size=11), text_color="gray",
        ).grid(row=0, column=0, pady=(6, 0))

        lbl = ctk.CTkLabel(
            wrapper, text=valor, font=ctk.CTkFont(size=17, weight="bold"),
        )
        lbl.grid(row=1, column=0, pady=(0, 6))
        return lbl

    # --- Painel de IEs (tabela + seleção alternável) ---
    def _criar_painel_ies(self, parent: ctk.CTkFrame) -> None:
        self._frame_ies = ctk.CTkFrame(parent, corner_radius=8)
        self._frame_ies.grid(row=1, column=0, sticky="nsew")
        self._frame_ies.grid_rowconfigure(1, weight=1)
        self._frame_ies.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self._frame_ies, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 2))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Inscrições Estaduais",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self._btn_alternar_modo = ctk.CTkButton(
            header, text="Selecionar IEs", width=130, height=28,
            font=ctk.CTkFont(size=11),
            command=self._alternar_modo_ies, state="disabled",
        )
        self._btn_alternar_modo.grid(row=0, column=1, sticky="e")

        _GRID_CONTEUDO = dict(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        # Modo tabela (textbox)
        self._textbox_ies = ctk.CTkTextbox(
            self._frame_ies, font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled", wrap="none",
        )
        self._textbox_ies.grid(**_GRID_CONTEUDO)

        # Modo seleção (scrollable frame + barra de ações)
        self._container_selecao = ctk.CTkFrame(self._frame_ies, fg_color="transparent")
        self._container_selecao.grid_columnconfigure(0, weight=1)
        self._container_selecao.grid_rowconfigure(0, weight=1)
        self._container_selecao.grid(**_GRID_CONTEUDO)
        self._container_selecao.grid_remove()

        self._grid_conteudo = _GRID_CONTEUDO

        self._frame_scroll_ies = ctk.CTkScrollableFrame(self._container_selecao)
        self._frame_scroll_ies.grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 0))

        barra_selecao = ctk.CTkFrame(self._container_selecao, fg_color="transparent")
        barra_selecao.grid(row=1, column=0, sticky="ew", padx=4, pady=(4, 6))

        ctk.CTkButton(
            barra_selecao, text="Selecionar todas", width=140, height=28,
            font=ctk.CTkFont(size=11), command=self._marcar_todas_ies,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            barra_selecao, text="Desmarcar todas", width=130, height=28,
            font=ctk.CTkFont(size=11), command=self._desmarcar_todas_ies,
        ).pack(side="left", padx=(0, 6))

        self._lbl_contador_selecao = ctk.CTkLabel(
            barra_selecao, text="Selecionadas: 0",
            font=ctk.CTkFont(size=11), text_color="gray",
        )
        self._lbl_contador_selecao.pack(side="left", padx=8)

    # --- Painel de processos + executar ---
    def _criar_painel_processos(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        frame.grid_columnconfigure(0, weight=1)

        row_idx = 0

        ctk.CTkLabel(
            frame, text="Processos",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=row_idx, column=0, sticky="w", padx=12, pady=(8, 2))
        row_idx += 1

        self._vars_processos: dict[str, ctk.BooleanVar] = {}
        for pid, nome in PROCESSOS_ICMS_PI:
            var = ctk.BooleanVar(value=(pid == "antecipado"))
            self._vars_processos[pid] = var
            habilitado = pid == "antecipado"
            cb = ctk.CTkCheckBox(frame, text=nome, variable=var, font=ctk.CTkFont(size=12))
            cb.grid(row=row_idx, column=0, sticky="w", padx=22, pady=2)
            if not habilitado:
                cb.configure(state="disabled")
            row_idx += 1

        ctk.CTkFrame(frame, height=1).grid(
            row=row_idx, column=0, sticky="ew", padx=12, pady=6,
        )
        row_idx += 1

        self._var_headless = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame, text="Headless (navegador oculto)",
            variable=self._var_headless, font=ctk.CTkFont(size=12),
        ).grid(row=row_idx, column=0, sticky="w", padx=22, pady=(0, 4))
        row_idx += 1

        ctk.CTkFrame(frame, height=1).grid(
            row=row_idx, column=0, sticky="ew", padx=12, pady=6,
        )
        row_idx += 1

        self._btn_executar = ctk.CTkButton(
            frame, text="▶  Executar", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green", hover_color="darkgreen",
            command=self._ao_executar, state="disabled",
        )
        self._btn_executar.grid(row=row_idx, column=0, padx=12, pady=(4, 12), sticky="ew")

    # --- Painel de log ---
    def _criar_painel_log(self, parent: ctk.CTkFrame) -> None:
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Log de execução",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        self._textbox_log = ctk.CTkTextbox(
            frame, font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled", wrap="word",
        )
        self._textbox_log.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # --- Barra de status ---
    def _criar_barra_status(self) -> None:
        frame = ctk.CTkFrame(self, corner_radius=0, height=28)
        frame.grid(row=3, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        self._lbl_status = ctk.CTkLabel(
            frame, text="Pronto", font=ctk.CTkFont(size=11),
            text_color="gray", anchor="w",
        )
        self._lbl_status.grid(row=0, column=0, sticky="ew", padx=14, pady=3)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _log(self, msg: str) -> None:
        self._textbox_log.configure(state="normal")
        self._textbox_log.insert("end", msg + "\n")
        self._textbox_log.see("end")
        self._textbox_log.configure(state="disabled")

    def _status(self, msg: str) -> None:
        self._lbl_status.configure(text=msg)

    def _habilitar_botoes(self, habilitado: bool = True) -> None:
        estado = "normal" if habilitado else "disabled"
        self._btn_abrir.configure(state=estado)
        self._btn_executar.configure(state=estado)
        self._btn_alternar_modo.configure(state=estado)
        if habilitado and self._dados_extraidos:
            self._btn_ver_dados.configure(state="normal")
        else:
            self._btn_ver_dados.configure(state=estado)

    # ------------------------------------------------------------------
    # Alternar modo tabela / seleção
    # ------------------------------------------------------------------
    def _alternar_modo_ies(self) -> None:
        if self._modo_ies == self._MODO_TABELA:
            self._mostrar_modo_selecao()
        else:
            self._mostrar_modo_tabela()

    def _mostrar_modo_tabela(self) -> None:
        self._modo_ies = self._MODO_TABELA
        self._container_selecao.grid_remove()
        self._textbox_ies.grid(**self._grid_conteudo)
        self._btn_alternar_modo.configure(text="Selecionar IEs")

    def _mostrar_modo_selecao(self) -> None:
        self._modo_ies = self._MODO_SELECAO
        self._textbox_ies.grid_remove()
        self._container_selecao.grid(**self._grid_conteudo)
        self._btn_alternar_modo.configure(text="Ver tabela")
        self._popular_selecao_ies()

    def _popular_selecao_ies(self) -> None:
        for widget in self._frame_scroll_ies.winfo_children():
            widget.destroy()
        self._vars_selecao.clear()

        for item in self._lista_dados:
            ie = _ie_para_exibicao(item.get("ie") or item.get("ie_digitos") or "")
            val = item.get("valor_atc")
            executavel = not _valor_atc_invalido(val)
            valor_txt = (
                f"{val:.2f}" if isinstance(val, (int, float))
                else (str(val) if val is not None else "—")
            )
            status = "Executável" if executavel else "Ignorada"

            row = ctk.CTkFrame(self._frame_scroll_ies, fg_color="transparent")
            row.pack(fill="x", pady=1)

            var = ctk.BooleanVar(value=executavel)
            if executavel:
                cb = ctk.CTkCheckBox(row, text="", variable=var, width=28)
                cb.pack(side="left", padx=(0, 6), pady=3)
                self._vars_selecao.append((item, var))
            else:
                ctk.CTkLabel(row, text="  —  ", width=36).pack(side="left", padx=(0, 6), pady=3)

            ctk.CTkLabel(
                row, text=ie,
                font=ctk.CTkFont(family="Consolas", size=12), width=130,
            ).pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(
                row, text=valor_txt,
                font=ctk.CTkFont(family="Consolas", size=12), width=100,
            ).pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(
                row, text=status, font=ctk.CTkFont(size=11),
                text_color="green" if executavel else "gray",
            ).pack(side="left", padx=4, pady=3)

        for _, var in self._vars_selecao:
            var.trace_add("write", lambda *_: self._atualizar_contador_selecao())
        self._atualizar_contador_selecao()

    def _marcar_todas_ies(self) -> None:
        for _, var in self._vars_selecao:
            var.set(True)

    def _desmarcar_todas_ies(self) -> None:
        for _, var in self._vars_selecao:
            var.set(False)

    def _atualizar_contador_selecao(self) -> None:
        n = sum(1 for _, var in self._vars_selecao if var.get())
        self._lbl_contador_selecao.configure(text=f"Selecionadas: {n}")

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _selecionar_arquivo(self) -> None:
        if self._caminho_excel is not None:
            trocar = messagebox.askyesno(
                "Trocar planilha",
                "Já existe uma planilha carregada.\n"
                "Deseja selecionar outro arquivo e substituir os dados atuais?",
            )
            if not trocar:
                return

        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo Excel",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")],
        )
        if not caminho:
            return

        self._caminho_excel = Path(caminho)
        logger.info("Arquivo selecionado: %s", self._caminho_excel.resolve())
        self._label_arquivo.configure(text=self._caminho_excel.name, text_color="white")
        self._carregar_planilha()
        self._btn_abrir.configure(text="Trocar arquivo…")

    def _carregar_planilha(self) -> None:
        if self._caminho_excel is None:
            return
        self._status("Carregando planilha…")
        self._log(f"Abrindo: {self._caminho_excel.name}")

        try:
            self._dados_extraidos, self._nome_para_indice, self._mes_ref, self._ano_ref = (
                extrair_todos_os_dados(self._caminho_excel)
            )
            self._nomes_colunas = [
                k for k, _ in sorted(self._nome_para_indice.items(), key=lambda x: x[1])
            ]
            self._lista_dados = obter_dados_para_dae(
                self._dados_extraidos, self._nome_para_indice,
                self._mes_ref, self._ano_ref,
            )
        except Exception as e:
            messagebox.showerror("Erro ao carregar planilha", str(e))
            self._log(f"ERRO: {e}")
            self._status("Falha ao carregar planilha")
            return

        qtd_exec, qtd_ign = _contar_executaveis_ignoradas(self._lista_dados)
        total = len(self._lista_dados)

        self._lbl_periodo.configure(text=f"{self._mes_ref:02d}/{self._ano_ref}")
        self._lbl_total.configure(text=str(total))
        self._lbl_exec.configure(text=str(qtd_exec))
        self._lbl_ignor.configure(text=str(qtd_ign))

        self._preencher_tabela_ies()
        if self._modo_ies == self._MODO_SELECAO:
            self._mostrar_modo_tabela()

        self._btn_ver_dados.configure(state="normal")
        self._btn_ver_dados.grid()
        self._btn_alternar_modo.configure(state="normal" if total > 0 else "disabled")
        self._btn_executar.configure(state="normal" if qtd_exec > 0 else "disabled")

        self._log(
            f"Planilha carregada: {total} registros, "
            f"{qtd_exec} executáveis, período {self._mes_ref:02d}/{self._ano_ref}"
        )
        self._status("Planilha carregada — pronto para executar")
        logger.info(
            "Extração: %d linhas, %d colunas, %d IEs, período %02d/%04d",
            len(self._dados_extraidos), len(self._nomes_colunas),
            total, self._mes_ref, self._ano_ref,
        )

    def _preencher_tabela_ies(self) -> None:
        self._textbox_ies.configure(state="normal")
        self._textbox_ies.delete("1.0", "end")

        header = f"{'#':>4}  {'I.E.':>12}  {'Valor ATC':>14}  {'Status'}\n"
        sep = "─" * 50 + "\n"
        self._textbox_ies.insert("end", header)
        self._textbox_ies.insert("end", sep)

        for idx, item in enumerate(self._lista_dados, 1):
            ie = _ie_para_exibicao(str(item.get("ie", "")))
            valor = item.get("valor_atc")
            if _valor_atc_invalido(valor):
                val_str = "—"
                status = "ignorada"
            else:
                val_str = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                status = "pendente"
            self._textbox_ies.insert("end", f"{idx:>4}  {ie:>12}  {val_str:>14}  {status}\n")

        self._textbox_ies.configure(state="disabled")

    def _ao_ver_dados(self) -> None:
        if not self._dados_extraidos or not self._caminho_excel:
            messagebox.showinfo("Dados", "Nenhum dado extraído para exibir.")
            return
        _mostrar_janela_dados_extraidos(
            self, self._caminho_excel, self._dados_extraidos,
            self._nomes_colunas, self._nome_para_indice,
        )

    # --- Executar ---
    def _ao_executar(self) -> None:
        if self._executando or not self._lista_dados:
            return

        processos = [pid for pid, var in self._vars_processos.items() if var.get()]
        if not processos:
            messagebox.showwarning("Nenhum processo", "Selecione ao menos um processo.")
            return

        if self._modo_ies == self._MODO_SELECAO:
            lista = [item for item, var in self._vars_selecao if var.get()]
            if not lista:
                messagebox.showwarning("Aviso", "Nenhuma I.E. selecionada.")
                return
            descricao_qtd = f"{len(lista)} IE(s) selecionada(s)"
        else:
            lista = [
                item for item in self._lista_dados
                if not _valor_atc_invalido(item.get("valor_atc"))
            ]
            if not lista:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhuma I.E. com valor ATC. Alterne para 'Selecionar IEs' para ver o detalhamento.",
                )
                return
            descricao_qtd = f"{len(lista)} IE(s) executável(is)"

        nomes = ", ".join(_nome_processo_legivel(p) for p in processos)

        confirmacao = messagebox.askyesno(
            "Confirmar execução",
            f"Executar {nomes} para {descricao_qtd}?\n"
            f"Período: {self._mes_ref:02d}/{self._ano_ref}\n"
            f"Headless: {'Sim' if self._var_headless.get() else 'Não'}",
        )
        if not confirmacao:
            return

        self._executando = True
        self._habilitar_botoes(False)
        self._btn_executar.configure(text="⏳  Executando…")
        self._status(f"Executando {descricao_qtd}…")
        self._log(f"\n{'═' * 40}")
        self._log(f"Executando: {nomes}  |  {descricao_qtd}  |  headless={self._var_headless.get()}")
        self._log(f"{'═' * 40}")

        def _ao_finalizar(ies_ok: list[str], ies_erro: list[tuple[str, str]]) -> None:
            self.after(0, self._finalizar_execucao, ies_ok, ies_erro)

        _executar_lote_em_background(
            lista, processos,
            self._var_headless.get(), result_callback=_ao_finalizar,
        )

    def _finalizar_execucao(
        self, ies_ok: list[str], ies_erro: list[tuple[str, str]],
    ) -> None:
        self._executando = False
        self._habilitar_botoes(True)
        self._btn_executar.configure(text="▶  Executar")

        self._log(f"\n{'─' * 40}")
        self._log(f"Concluído: {len(ies_ok)} sucesso, {len(ies_erro)} erro(s)")
        if ies_ok:
            self._log(f"  Sucesso: {', '.join(ies_ok)}")
        if ies_erro:
            for ie, motivo in ies_erro:
                self._log(f"  Erro IE {ie}: {motivo}")
        self._log(f"{'─' * 40}\n")

        total = len(ies_ok) + len(ies_erro)
        if ies_erro:
            self._status(f"Finalizado: {len(ies_ok)}/{total} sucesso, {len(ies_erro)} erro(s)")
        else:
            self._status("Execução concluída com sucesso!")


def main() -> None:
    """Ponto de entrada da GUI ICMS-PI."""
    logger.info("Iniciando interface ICMS-PI.")
    app = App()
    app.mainloop()
    logger.info("Interface encerrada.")


if __name__ == "__main__":
    main()
    sys.exit(0)
