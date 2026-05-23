import argparse
import shutil
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="将 DOCX 解包为 OOXML 目录。")
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--force", action="store_true", help="覆盖已存在的输出目录")
    args = parser.parse_args()

    if not args.docx.exists():
        parser.error(f"文件不存在：{args.docx}")
    if args.output_dir.exists():
        if not args.force:
            parser.error(f"输出目录已存在：{args.output_dir}；需要覆盖时加 --force")
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.docx, "r") as zf:
        zf.extractall(args.output_dir)
    print(f"已解包：{args.docx} -> {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
