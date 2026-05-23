import importlib.util
import json
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


PYTHON_MODULES = ["docx", "lxml", "defusedxml"]
COMMANDS = ["pandoc", "soffice", "pdftoppm", "node"]


def command_version(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        return ""
    probes = {
        "pandoc": [cmd, "--version"],
        "soffice": [cmd, "--version"],
        "pdftoppm": [cmd, "-v"],
        "node": [cmd, "--version"],
    }
    try:
        result = subprocess.run(probes[cmd], capture_output=True, text=True, timeout=8)
    except Exception as exc:
        return f"found at {path}; version check failed: {exc}"
    output = (result.stdout or result.stderr).splitlines()
    return output[0].strip() if output else f"found at {path}"


def node_docx_status() -> bool:
    if not shutil.which("node"):
        return False
    result = subprocess.run(
        ["node", "-e", "try{require.resolve('docx');process.exit(0)}catch(e){process.exit(1)}"],
        capture_output=True,
        text=True,
        timeout=8,
    )
    return result.returncode == 0


def main() -> int:
    report = {
        "python": sys.version.split()[0],
        "modules": {name: importlib.util.find_spec(name) is not None for name in PYTHON_MODULES},
        "commands": {name: {"found": bool(shutil.which(name)), "version": command_version(name)} for name in COMMANDS},
        "node_docx_package": node_docx_status(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    missing = [name for name, ok in report["modules"].items() if not ok]
    if missing:
        print("缺少 Python 模块：" + "、".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
