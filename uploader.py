"""Build, verify, and optionally upload rpa_suite to (Test)PyPI."""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import zipfile

BUILD_DIRS = ("dist", "build", "rpa_suite.egg-info")

REQUIRED_WHEEL_ASSETS = (
    "rpa_suite/core/dashboard/templates/overview.html",
    "rpa_suite/core/dashboard/templates/error.html",
    "rpa_suite/core/dashboard/templates/base.html",
    "rpa_suite/core/dashboard/templates/executions.html",
    "rpa_suite/core/dashboard/templates/items.html",
    "rpa_suite/core/dashboard/templates/logs.html",
    "rpa_suite/core/dashboard/templates/_pagination.html",
    "rpa_suite/core/dashboard/static/dashboard.css",
    "rpa_suite/core/dashboard/static/dashboard.js",
)


def limpar_pastas(pastas: tuple[str, ...] = BUILD_DIRS) -> None:
    for pasta in pastas:
        if os.path.exists(pasta):
            shutil.rmtree(pasta)


def _dist_artifacts() -> list[str]:
    artifacts = glob.glob(os.path.join("dist", "*.whl")) + glob.glob(os.path.join("dist", "*.tar.gz"))
    return sorted(artifacts)


def _wheel_path(artifacts: list[str]) -> str:
    wheels = [path for path in artifacts if path.endswith(".whl")]
    if not wheels:
        print("Nenhum arquivo .whl encontrado em dist/.")
        sys.exit(1)
    if len(wheels) > 1:
        print("Mais de um wheel em dist/. Limpe a pasta e gere novamente.")
        for path in wheels:
            print(f"  - {path}")
        sys.exit(1)
    return wheels[0]


def verify_wheel(wheel_path: str) -> None:
    with zipfile.ZipFile(wheel_path) as archive:
        names = set(archive.namelist())
        metadata_name = next((name for name in names if name.endswith(".dist-info/METADATA")), None)
        metadata = archive.read(metadata_name).decode("utf-8") if metadata_name else ""

    missing = [asset for asset in REQUIRED_WHEEL_ASSETS if asset not in names]
    if missing:
        print("O wheel nao inclui os assets do dashboard:")
        for asset in missing:
            print(f"  - {asset}")
        sys.exit(1)

    require_lines = [line.strip() for line in metadata.splitlines() if line.lower().startswith("requires-dist:")]
    typing_requires = []
    for line in require_lines:
        requirement = line.split(":", 1)[1].strip().split(";")[0].strip()
        name = requirement.split()[0].split("[")[0].strip()
        if name.lower() == "typing":
            typing_requires.append(line)
    if typing_requires:
        print("O wheel ainda declara a dependencia 'typing' (backport). Remova de install_requires.")
        for line in typing_requires:
            print(f"  - {line}")
        sys.exit(1)

    print(f"Wheel OK: {os.path.basename(wheel_path)}")
    print("  - templates/static do dashboard presentes")
    print("  - dependencia 'typing' ausente do METADATA")


def _run(command: list[str], error_message: str) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"{error_message}: {exc}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera, valida e envia rpa_suite para o PyPI.")
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Apenas gera e valida o wheel (nao envia).",
    )
    parser.add_argument(
        "--test-pypi",
        action="store_true",
        help="Envia para TestPyPI em vez do PyPI de producao.",
    )
    parser.add_argument(
        "--keep-dist",
        action="store_true",
        help="Mantem dist/build apos o upload para inspecao.",
    )
    args = parser.parse_args()

    limpar_pastas()

    _run([sys.executable, "-m", "build"], "Erro ao construir o pacote")

    artifacts = _dist_artifacts()
    if not artifacts:
        print("A pasta dist/ nao contem artefatos apos o build. Abortando.")
        sys.exit(1)

    verify_wheel(_wheel_path(artifacts))
    _run([sys.executable, "-m", "twine", "check", *artifacts], "Erro no twine check")

    if args.skip_upload:
        print("Validacao concluida. Upload ignorado (--skip-upload).")
        return

    upload_cmd = [sys.executable, "-m", "twine", "upload"]
    if args.test_pypi:
        upload_cmd.extend(["--repository", "testpypi"])
        print("Enviando para TestPyPI...")
    else:
        print("Enviando para PyPI de producao...")
    upload_cmd.extend(artifacts)

    _run(upload_cmd, "Erro ao fazer upload com o Twine")

    if not args.keep_dist:
        limpar_pastas()


if __name__ == "__main__":
    main()
