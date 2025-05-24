#! /usr/bin/env bash

# 任何命令返回非零退出状态则终止脚本执行
set -e
# 运行命令前先打印完整命令
set -x

python extract_dependencies.py