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
check_command "curl"

# 获取当前版本号
current_version=$(grep 'version=' setup.py | cut -d'"' -f2)
info "当前版本: $current_version"
echo "调试信息: 从setup.py中获取的版本号是: $current_version"

# 检查PyPI上是否已存在此版本
check_version_exists() {
    local version=$1
    response=$(curl -s "https://pypi.org/pypi/didatodolist/json")
    if echo "$response" | grep -q "\"$version\""; then
        return 0 # 版本存在
    else
        return 1 # 版本不存在
    fi
}

# 检查当前版本是否已发布
if check_version_exists "$current_version"; then
    warning "版本 $current_version 已经发布到PyPI，无需重复发布"
    warning "如果需要发布新版本，请先更新setup.py中的版本号"
    exit 0
fi

info "版本 $current_version 尚未发布，开始发布流程..."

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
git commit -m "Release version $current_version"
git tag "v$current_version"

# 推送到远程仓库
info "推送到远程仓库..."
git push origin main
git push origin "v$current_version"

# 上传到PyPI
info "上传到PyPI..."
if ! twine upload dist/*; then
    error "上传到PyPI失败！"
    exit 1
fi

# 安装新版本
info "安装新版本..."
pip install --upgrade didatodolist

info "发布完成！新版本 $current_version 已发布并安装"

# 显示当前安装的版本
installed_version=$(pip show didatodolist | grep Version | cut -d' ' -f2)
info "当前安装的版本: $installed_version" 