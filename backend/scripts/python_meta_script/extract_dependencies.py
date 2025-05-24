#!/usr/bin/env python3
"""
提取 pyproject.toml 中的依赖并生成 requirements.txt
用法: python extract_dependencies.py [--include-optional group_name]
"""

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        print("请安装 tomli: pip install tomli")
        sys.exit(1)


def extract_dependencies(
    pyproject_path: str | Path = "pyproject.toml", include_optional: str | None = None
) -> list[str]:
    """从 pyproject.toml 提取依赖

    Args:
        pyproject_path: pyproject.toml 的路径，默认为当前目录下的 pyproject.toml
        include_optional: 可选依赖组名称

    Returns:
        List[str]: 依赖列表
    """
    pyproject_path = Path(pyproject_path).resolve()

    if not pyproject_path.exists():
        print(f"错误: {pyproject_path} 文件不存在")
        return []

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"错误: 无法解析 {pyproject_path}: {e}")
        return []

    dependencies: list[str] = []

    # 获取主要依赖
    project: dict[str, Any] = data.get("project", {})
    main_deps: list[str] = project.get("dependencies", [])
    dependencies.extend(main_deps)

    # 获取可选依赖
    if include_optional:
        optional_deps: dict[str, list[str]] = project.get("optional-dependencies", {})
        if include_optional in optional_deps:
            dependencies.extend(optional_deps[include_optional])
        else:
            print(f"警告: 找不到可选依赖组 '{include_optional}'")
            print(f"可用的组: {list(optional_deps.keys())}")

    return dependencies


def main() -> None:
    parser = argparse.ArgumentParser(description="从 pyproject.toml 提取依赖")
    parser.add_argument(
        "--include-optional", help="包含指定的可选依赖组 (如: dev, test)"
    )
    parser.add_argument("--output", "-o", default="requirements.txt", help="输出文件名")

    parser.add_argument(
        "--pyproject", "-p", default="pyproject.toml", help="pyproject.toml 的路径"
    )

    args = parser.parse_args()

    dependencies = extract_dependencies(
        pyproject_path=args.pyproject, include_optional=args.include_optional
    )

    if not dependencies:
        print("没有找到依赖")
        return

    # 写入 requirements.txt
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        for dep in dependencies:
            f.write(f"{dep}\n")

    print(f"已生成 {output_path}，包含 {len(dependencies)} 个依赖:")
    for dep in dependencies:
        print(f"  - {dep}")


if __name__ == "__main__":
    main()
