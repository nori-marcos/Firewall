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
    "--pdf-engine", "tectonic",
    "--listings",
    "--citeproc",
    "--bibliography", str(DEFAULT_BIB),
    "--csl", str(DEFAULT_CSL),
    "-H", str(CODE_STYLE),
    "--template", "custom-template.tex",
    "-V", "documentclass=IEEEtran",
    "-V", "classoption=conference",
    "-V", "lang=pt-BR",
    "-V", "babel-lang=brazilian",
]

def ensure_pandoc():
	try:
		pypandoc.get_pandoc_path()
	except OSError:
		print("Pandoc não encontrado — baixando localmente...")
		pypandoc.download_pandoc()


def convert_one(md_path: Path):
    md_path = md_path.resolve()
    pdf_path = md_path.with_suffix(".pdf")
    last_err = None

    resource_path = f"{md_path.parent}{os.pathsep}{ROOT}"

    try:

        pypandoc.convert_file(
            str(md_path),
            "pdf",
            format="md",
            outputfile=str(pdf_path),
            extra_args=BASE_ARGS + [f"--resource-path={resource_path}"],
        )

        print(f"✔ Gerado: {pdf_path}  (engine: tectonic, classe: IEEEtran[conference])")
        return
    except Exception as e:
        last_err = e

    raise RuntimeError(
			f"Falha ao gerar PDF para '{md_path.name}'.\n"
			f"Dica: verifique o 'tectonic' e se o LaTeX encontra a classe IEEEtran instalada.\n"
			f"Erro: {last_err}"
	)


def main():
	ensure_pandoc()
	for md in ROOT.rglob("*.md"):
		try:
			convert_one(md)
		except Exception as e:
			print(f"✖ Erro em {md}: {e}", file=sys.stderr)


if __name__ == "__main__":
	main()
