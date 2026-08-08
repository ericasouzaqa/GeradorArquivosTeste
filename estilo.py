import os
import sys
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk, ImageEnhance

    PIL_DISPONIVEL = True

except ImportError:
    PIL_DISPONIVEL = False


# ============================================================
# CORES
# ============================================================

COR_FUNDO = "#EAF0F7"
COR_CARD = "#FFFFFF"
COR_TEXTO = "#1E293B"
COR_TEXTO_SECUNDARIO = "#64748B"

COR_DESTAQUE = "#2563EB"
COR_DESTAQUE_HOVER = "#1D4ED8"

COR_STATUS = "#F1F5F9"
COR_BORDA = "#D8E0EA"
COR_SUCESSO = "#15803D"


# ============================================================
# FONTES
# ============================================================

FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_SUBTITULO = ("Segoe UI", 10)
FONTE_SECAO = ("Segoe UI", 11, "bold")
FONTE_NORMAL = ("Segoe UI", 10)
FONTE_BOTAO = ("Segoe UI", 10, "bold")
FONTE_RODAPE = ("Segoe UI", 9)


# ============================================================
# DIRETÓRIO DOS ARQUIVOS
# ============================================================

def obter_diretorio_base():
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS

        return os.path.dirname(
            sys.executable
        )

    return os.path.dirname(
        os.path.abspath(__file__)
    )


DIRETORIO_ATUAL = obter_diretorio_base()


# ============================================================
# ARQUIVOS
# ============================================================

CAMINHO_CAPA = os.path.join(
    DIRETORIO_ATUAL,
    "capa.png"
)

CAMINHO_ICONE = os.path.join(
    DIRETORIO_ATUAL,
    "icone.ico"
)


# ============================================================
# ESTILO
# ============================================================

def configurar_estilo():
    estilo = ttk.Style()

    try:
        estilo.theme_use("vista")

    except tk.TclError:
        try:
            estilo.theme_use("clam")

        except tk.TclError:
            pass

    estilo.configure(
        "Acao.TButton",
        font=FONTE_BOTAO,
        padding=(18, 9)
    )

    estilo.map(
        "Acao.TButton",
        background=[
            ("active", COR_DESTAQUE_HOVER)
        ],
        foreground=[
            ("active", "#FFFFFF")
        ]
    )

    estilo.configure(
        "Lote.TCheckbutton",
        font=FONTE_NORMAL
    )

    return estilo


# ============================================================
# ÍCONE
# ============================================================

def aplicar_icone(janela):
    if not os.path.exists(CAMINHO_ICONE):
        return False

    try:
        janela.iconbitmap(
            CAMINHO_ICONE
        )

        return True

    except tk.TclError:
        return False

    except Exception:
        return False


# ============================================================
# FUNDO / CAPA
# ============================================================

def criar_fundo(janela, largura, altura):
    if not PIL_DISPONIVEL:
        return None

    if not os.path.exists(CAMINHO_CAPA):
        return None

    try:
        imagem = Image.open(
            CAMINHO_CAPA
        ).convert("RGB")

        proporcao = max(
            largura / imagem.width,
            altura / imagem.height
        )

        nova_largura = int(
            imagem.width * proporcao
        )

        nova_altura = int(
            imagem.height * proporcao
        )

        imagem = imagem.resize(
            (
                nova_largura,
                nova_altura
            ),
            Image.Resampling.LANCZOS
        )

        esquerda = (
            nova_largura - largura
        ) // 2

        topo = (
            nova_altura - altura
        ) // 2

        imagem = imagem.crop(
            (
                esquerda,
                topo,
                esquerda + largura,
                topo + altura
            )
        )

        imagem = ImageEnhance.Brightness(
            imagem
        ).enhance(1.08)

        imagem = ImageEnhance.Contrast(
            imagem
        ).enhance(0.82)

        camada_branca = Image.new(
            "RGB",
            (
                largura,
                altura
            ),
            "white"
        )

        imagem = Image.blend(
            imagem,
            camada_branca,
            0.25
        )

        imagem_tk = ImageTk.PhotoImage(
            imagem
        )

        return imagem_tk

    except Exception:
        return None


# ============================================================
# LINKS
# ============================================================

def configurar_link(label, callback):
    label.configure(
        cursor="hand2"
    )

    label.bind(
        "<Button-1>",
        lambda event: callback()
    )

    label.bind(
        "<Enter>",
        lambda event: label.configure(
            foreground=COR_DESTAQUE
        )
    )

    label.bind(
        "<Leave>",
        lambda event: label.configure(
            foreground="#FFFFFF"
        )
    )