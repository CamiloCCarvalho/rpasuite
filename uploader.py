"""Build, verify, and optionally upload rpa_suite to (Test)PyPI."""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import zipfile

BUILD_DIRS = ("dist", "build", "rpa_suite.egg-info")

FORBIDDEN_CORE_REQUIRES = ("typing", "opencv-python", "colorlog")
LEGACY_WHEEL_PATHS = ("rpa_suite/core/database.py",)
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
    for unpacked in glob.glob("rpa_suite-[0-9]*"):
        if os.path.isdir(unpacked) and os.path.isfile(os.path.join(unpacked, "PKG-INFO")):
            shutil.rmtree(unpacked)


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

    leftover_legacy = [path for path in LEGACY_WHEEL_PATHS if path in names]
    if leftover_legacy:
        print("O wheel ainda inclui o database.py legado:")
        for path in leftover_legacy:
            print(f"  - {path}")
        sys.exit(1)

    forbidden_core = []
    for line in metadata.splitlines():
        if not line.lower().startswith("requires-dist:"):
            continue
        rest = line.split(":", 1)[1].strip()
        name = rest.split()[0].split("[")[0].strip().lower()
        extra_marker = "extra ==" in rest.lower() or "extra==" in rest.lower()
        if name in FORBIDDEN_CORE_REQUIRES and not extra_marker:
            forbidden_core.append(line.strip())
    if forbidden_core:
        print("O wheel declara dependencias pesadas/obsoletas no nucleo (deveriam ser extra ou removidas):")
        for line in forbidden_core:
            print(f"  - {line}")
        sys.exit(1)

    print(f"Wheel OK: {os.path.basename(wheel_path)}")
    print("  - templates/static do dashboard presentes")
    print("  - database.py legado ausente")
    print("  - typing/opencv-python/colorlog ausentes do nucleo")


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
