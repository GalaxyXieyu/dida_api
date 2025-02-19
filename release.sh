#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 检查必要的命令
check_command "python"
check_command "pip"
check_command "twine"
check_command "git"

# 获取当前版本号
current_version=$(grep 'version=' setup.py | cut -d'"' -f2)
info "当前版本: $current_version"

# 提示输入新版本号
read -p "请输入新版本号 (直接回车使用自动递增): " new_version

# 如果没有输入新版本号，自动递增最后一位
if [ -z "$new_version" ]; then
    IFS='.' read -r -a version_parts <<< "$current_version"
    last_part=$((${version_parts[2]} + 1))
    new_version="${version_parts[0]}.${version_parts[1]}.$last_part"
fi

info "准备发布版本 $new_version"

# 更新版本号
sed -i "s/version=\"$current_version\"/version=\"$new_version\"/" setup.py
info "版本号已更新到 $new_version"

# 清理旧的构建文件
info "清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info/

# 构建包
info "构建包..."
python setup.py sdist bdist_wheel

# 检查构建是否成功
if [ ! -d "dist" ]; then
    error "构建失败！"
    exit 1
fi

# 使用twine检查包
info "检查包..."
if ! twine check dist/*; then
    error "包检查失败！"
    exit 1
fi

# 提交到Git
info "提交到Git..."
git add setup.py
git commit -m "Release version $new_version"
git tag "v$new_version"

# 推送到远程仓库
info "推送到远程仓库..."
git push origin master
git push origin "v$new_version"

# 上传到PyPI
info "上传到PyPI..."
if ! twine upload dist/*; then
    error "上传到PyPI失败！"
    exit 1
fi

# 安装新版本
info "安装新版本..."
pip install --upgrade didatodolist

info "发布完成！新版本 $new_version 已发布并安装"

# 显示当前安装的版本
installed_version=$(pip show didatodolist | grep Version | cut -d' ' -f2)
info "当前安装的版本: $installed_version" 