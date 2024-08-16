#!/bin/bash

# 初始化 config 資料夾
if [ ! -d /workspace/config ]; then
  mkdir -p /workspace/config
fi

# 如果 config 資料夾為空，則複製 config_init 資料夾內的檔案到 config 資料夾
if [ -z "$(ls -A /workspace/config)" ]; then
  cp /workspace/config_init/* /workspace/config/
fi

# 等待其他服務啟動
echo "等待其他服務啟動......" &
sleep 5

# 啟動主程式
echo "啟動主程式" &
python3 /workspace/main.py

# 防止腳本退出
wait -n
