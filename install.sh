#!/bin/bash
# Linux_T48编程器 一键部署脚本
# by：车机研究所_草软
# 用法: curl -sSL https://raw.githubusercontent.com/qyjqio/Linux_T48/main/install.sh | bash

set -e

echo "======================================"
echo " Linux_T48编程器 一键部署"
echo " by：车机研究所_草软"
echo "======================================"

# 安装依赖
echo "[1/6] 安装编译依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential pkg-config libusb-1.0-0-dev zlib1g-dev \
    libarchive-tools python3-tk git wget curl >/dev/null 2>&1
echo "  -> 依赖安装完成"

# 编译安装 minipro
echo "[2/6] 编译安装 minipro..."
TMPDIR=$(mktemp -d)
cd "$TMPDIR"
git clone --depth=1 https://gitlab.com/DavidGriffith/minipro.git >/dev/null 2>&1
cd minipro
make -j$(nproc) >/dev/null 2>&1
sudo make install >/dev/null 2>&1
sudo make udev >/dev/null 2>&1
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "  -> minipro 安装完成"

# 下载安装算法文件
echo "[3/6] 下载 T48/T56/T76 算法文件（可能需要几分钟）..."
SHARE_DIR=$(minipro --version 2>&1 | grep "Share dir" | awk '{print $NF}' || echo "/usr/local/share/minipro")
[ -z "$SHARE_DIR" ] && SHARE_DIR="/usr/local/share/minipro"

XGPRO_URL="https://ghfast.top/https://github.com/Kreeblah/XGecu_Software/raw/refs/heads/master/Xgpro/13"
sudo curl -L --connect-timeout 10 --retry 3 -o xgproV1304_T48_T56_T866II_Setup.rar \
    "$XGPRO_URL/xgproV1304_T48_T56_T866II_Setup.rar" 2>/dev/null
sudo curl -L --connect-timeout 10 --retry 3 -o xgpro_T76_V1303A.rar \
    "$XGPRO_URL/xgpro_T76_V1303A.rar" 2>/dev/null
sudo bash dump-alg-minipro.bash "$SHARE_DIR" 2>/dev/null && echo "  -> 算法安装完成" || echo "  -> 算法安装跳过（不影响基本使用）"

# 安装 GUI
echo "[4/6] 安装 Linux_T48编程器 GUI..."
cd /tmp
git clone --depth=1 https://github.com/qyjqio/Linux_T48.git >/dev/null 2>&1
sudo cp Linux_T48/linux-t48.py /usr/local/bin/linux-t48
sudo chmod +x /usr/local/bin/linux-t48
echo "  -> GUI 安装完成"

# 创建桌面快捷方式
echo "[5/6] 创建桌面快捷方式..."
mkdir -p ~/.local/share/applications
cp Linux_T48/linux-t48.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/ 2>/dev/null
echo "  -> 快捷方式创建完成"

# 清理
echo "[6/6] 清理临时文件..."
rm -rf "$TMPDIR" /tmp/Linux_T48
echo "  -> 清理完成"

echo ""
echo "======================================"
echo " 安装完成！"
echo " 启动方式："
echo "   命令行: linux-t48"
echo "   菜单: 搜索 'Linux_T48编程器'"
echo "======================================"
echo ""

# 检测编程器
minipro --version 2>&1 | head -3 || true
CHIP_COUNT=$(minipro -l 2>&1 | grep -v "Found\|Warning\|Device\|Serial\|Manufactured\|USB\|Supply" | wc -l)
echo "支持芯片: ${CHIP_COUNT} 种"
