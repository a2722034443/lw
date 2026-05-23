import argparse
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="将 OOXML 目录重新打包为 DOCX。")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--force", action="store_true", help="覆盖已存在的输出 DOCX")
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"目录不存在：{args.input_dir}")
    if args.output_docx.exists() and not args.force:
        parser.error(f"输出文件已存在：{args.output_docx}；需要覆盖时加 --force")
    args.output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output_docx, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in args.input_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(args.input_dir).as_posix())
    print(f"已打包：{args.input_dir} -> {args.output_docx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
