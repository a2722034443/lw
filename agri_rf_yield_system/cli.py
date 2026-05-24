from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .config import DEFAULT_CROP, DEFAULT_END_YEAR, DEFAULT_MAX_COUNTRIES, DEFAULT_START_YEAR
from .data_sources import download_all
from .dataset import build_dataset
from .evaluation import evaluate_outputs
from .modeling import train_model
from .thesis_assets import export_assets


def cmd_download_data(args) -> int:
    path = download_all(args.crop, args.start_year, args.end_year, args.max_countries)
    print(path)
    return 0


def cmd_build_dataset(args) -> int:
    profile = build_dataset(min_rows=args.min_rows)
    print(profile["dataset_path"])
    return 0


def cmd_train(args) -> int:
    metrics = train_model(args.n_estimators, args.test_years, args.random_state)
    print(metrics)
    return 0


def cmd_evaluate(args) -> int:
    report = evaluate_outputs()
    print(report)
    return 0


def cmd_export_thesis_assets(args) -> int:
    path = export_assets()
    print(path)
    return 0


def cmd_init_thesis(args) -> int:
    title = "基于随机森林的多源农业数据作物产量预测与可视化系统设计与实现"
    workspace = Path(args.workspace)
    command = [
        sys.executable,
        "-m",
        "local_thesis_assistant.thesis_flow",
        "init",
        "--title",
        title,
        "--type",
        "software-project",
        "--workspace",
        str(workspace),
    ]
    return subprocess.call(command)


def cmd_run_app(args) -> int:
    command = [sys.executable, "-m", "streamlit", "run", "agri_rf_yield_system/app.py"]
    if args.server_port:
        command.extend(["--server.port", str(args.server_port)])
    return subprocess.call(command)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="农业随机森林产量预测系统")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("download-data", help="下载 FAOSTAT、NASA POWER 和 World Bank 真实数据")
    p.add_argument("--crop", default=DEFAULT_CROP)
    p.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    p.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR)
    p.add_argument("--max-countries", type=int, default=DEFAULT_MAX_COUNTRIES)
    p.set_defaults(func=cmd_download_data)

    p = sub.add_parser("build-dataset", help="合并多源数据并构建建模数据集")
    p.add_argument("--min-rows", type=int, default=120)
    p.set_defaults(func=cmd_build_dataset)

    p = sub.add_parser("train", help="训练随机森林回归模型")
    p.add_argument("--n-estimators", type=int, default=300)
    p.add_argument("--test-years", type=int, default=5)
    p.add_argument("--random-state", type=int, default=42)
    p.set_defaults(func=cmd_train)

    p = sub.add_parser("evaluate", help="生成预测图表和评价报告")
    p.set_defaults(func=cmd_evaluate)

    p = sub.add_parser("export-thesis-assets", help="导出论文证据链、实验报告和截图清单")
    p.set_defaults(func=cmd_export_thesis_assets)

    p = sub.add_parser("init-thesis", help="调用本地论文助手创建论文工作区")
    p.add_argument("--workspace", default="agri_rf_yield_system/thesis_workspace")
    p.set_defaults(func=cmd_init_thesis)

    p = sub.add_parser("run-app", help="启动 Streamlit 系统")
    p.add_argument("--server-port", type=int)
    p.set_defaults(func=cmd_run_app)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
