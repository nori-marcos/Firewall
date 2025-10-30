import os
import sys
from pathlib import Path

import pypandoc

ROOT = Path(__file__).parent.resolve()

DEFAULT_CSL = ROOT / "ieee.csl"
DEFAULT_BIB = ROOT / "references.bib"
CODE_STYLE = ROOT / "code-style.tex"

BASE_ARGS = [
		"--standalone",
		"--number-sections",
		"--wrap=preserve",
		"--pdf-engine", "xelatex",
		"--listings",
		"--citeproc",
		"--bibliography", str(DEFAULT_BIB),
		"--csl", str(DEFAULT_CSL),
		"-H", str(CODE_STYLE),
		"-V", "documentclass=IEEEtran",
		"-V", "classoption=conference",
		"-V", "lang=pt-BR",
]


def ensure_pandoc():
	"""Verifica se o Pandoc está instalado, baixa se necessário."""
	try:
		pypandoc.get_pandoc_path()
	except OSError:
		print("Pandoc não encontrado — baixando localmente...")
		pypandoc.download_pandoc()


def convert_one(md_path: Path):
	"""
	Converte um único arquivo Markdown para PDF.
	Erros são propagados para a função 'main'.
	"""
	md_path = md_path.resolve()
	pdf_path = md_path.with_suffix(".pdf")
	
	resource_path = f"{md_path.parent}{os.pathsep}{ROOT}"
	
	print(f"Convertendo {md_path.name} com xelatex...")
	
	pypandoc.convert_file(
			str(md_path),
			"pdf",
			format="md",
			outputfile=str(pdf_path),
			extra_args=BASE_ARGS + [f"--resource-path={resource_path}"],
	)
	
	print(f"✔ Gerado: {pdf_path.name} (engine: xelatex, classe: IEEEtran)")


def main():
	"""Encontra e converte todos os arquivos .md no diretório."""
	ensure_pandoc()
	
	for md_file in ROOT.rglob("*.md"):
		try:
			convert_one(md_file)
		except Exception as e:
			print(f"✖ Falha ao converter '{md_file.name}'.", file=sys.stderr)
			print(f"  Verifique se 'xelatex' e a classe 'IEEEtran.cls' estão instalados.", file=sys.stderr)
			print(f"  Erro completo: {e}", file=sys.stderr)


if __name__ == "__main__":
	main()
