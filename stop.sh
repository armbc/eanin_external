#!/usr/bin/env bash

echo -e "\033[34m--------------------wsgi process--------------------\033[0m"

# 检查是否有运行中的 uWSGI 进程
if ! pgrep -f eanintop01_uwsgi.ini > /dev/null; then
    echo "No uWSGI process found."
    exit 0
else
    # 显示当前正在运行的 uWSGI 进程
    ps -ef | grep eanintop01_uwsgi.ini | grep -v grep
fi

sleep 0.5

read -p "--------------------going to close. Are you sure? (y/n) " confirm
if [[ $confirm == [yY] ]]; then
    echo -e '\n--------------------closing processes--------------------'
    pkill -f eanintop01_uwsgi.ini

    # 检查是否由 systemd 管理
    if systemctl is-active --quiet uwsgi; then
        echo "Stopping uWSGI service managed by systemd..."
        sudo systemctl stop uwsgi
    fi

    echo -e '\n--------------------remaining processes--------------------'
    ps -ef | grep eanintop01_uwsgi.ini | grep -v grep
else
    echo -e '\n--------------------cancelled--------------------'
fi