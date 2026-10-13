import sys
import tempfile
import types
import unittest
from pathlib import Path

# O núcleo de geração pode ser testado em ambientes sem Tkinter instalado.
tkinter = types.ModuleType("tkinter")
tkinter.ttk = types.ModuleType("tkinter.ttk")
tkinter.filedialog = types.ModuleType("tkinter.filedialog")
tkinter.messagebox = types.ModuleType("tkinter.messagebox")
sys.modules.setdefault("tkinter", tkinter)
sys.modules.setdefault("tkinter.ttk", tkinter.ttk)
sys.modules.setdefault("tkinter.filedialog", tkinter.filedialog)
sys.modules.setdefault("tkinter.messagebox", tkinter.messagebox)

import gerador


class TestNovasExtensoes(unittest.TestCase):
    def gerar(self, extensao, tamanho=2 * 1024 * 1024):
        pasta = Path(tempfile.mkdtemp())
        caminho = pasta / f"teste.{extensao}"
        gerador.gerar_arquivo(str(caminho), tamanho, extensao, caminho.name)
        self.assertEqual(caminho.stat().st_size, tamanho)
        return caminho.read_bytes()

    def test_imagens_pillow(self):
        assinaturas = {
            "webp": b"RIFF",
            "gif": b"GIF8",
            "tiff": (b"II*\x00", b"MM\x00*"),
        }
        for extensao, assinatura in assinaturas.items():
            dados = self.gerar(extensao)
            if isinstance(assinatura, tuple):
                self.assertIn(dados[:4], assinatura)
            else:
                self.assertEqual(dados[:4], assinatura)

    def test_svg_valido(self):
        dados = self.gerar("svg").decode("utf-8")
        self.assertIn("<svg ", dados)
        self.assertIn("</svg>", dados)
        self.assertIn("teste.svg", dados)

    def test_assinaturas_heif(self):
        for extensao in ("heic", "heif"):
            dados = self.gerar(extensao)
            self.assertEqual(dados[4:8], b"ftyp")
            self.assertEqual(dados[8:12], extensao.encode())


if __name__ == "__main__":
    unittest.main()
