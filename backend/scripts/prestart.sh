#! /usr/bin/env bash

# 任何命令返回非零退出状态则终止脚本执行
set -e
# 运行命令前先打印完整命令
set -x

python app/db/initial/db_start_test.py

alembic upgrade head

python app/db/initial/initial_data_in_db.py