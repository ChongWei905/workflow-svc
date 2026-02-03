#!/bin/bash
#
# 创建文件或目录
#

create_file() {
    local filepath="$1"
    local content="$2"
    local mkdir=$(dirname "$filepath")

    # 创建父目录
    if [ ! -d "$mkdir" ]; then
        mkdir -p "$mkdir"
    fi

    # 写入内容
    if [ -n "$content" ]; then
        echo "$content" > "$filepath"
    else
        touch "$filepath"
    fi

    echo "文件已创建: $filepath"
}

create_directory() {
    local dirpath="$1"
    mkdir -p "$dirpath"
    echo "目录已创建: $dirpath"
}

# 主逻辑
if [[ "$1" == "--dir" ]]; then
    create_directory "$2"
else
    create_file "$1" "$2"
fi
