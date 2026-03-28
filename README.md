# Linux_T48编程器

**by：车机研究所_草软**

T48/TL866 系列万能编程器的 Linux 图形界面工具，基于开源 [minipro](https://gitlab.com/DavidGriffith/minipro) 驱动。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Debian-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-green)

## 功能特性

- 支持 **32,000+** 种芯片（SPI Flash / EEPROM / MCU / PLD 等）
- 芯片搜索、读取、写入、擦除、校验
- SPI 时钟调速（4/8/15/30 MHz）
- 空白检查、引脚检测、芯片ID自动识别
- 保护位读写、ICSP 在线编程
- VPP/VDD/VCC 电压自定义
- Intel HEX / Motorola SREC / RAW 二进制格式支持
- 编程器固件更新、逻辑IC测试

## 支持的编程器

| 编程器 | 支持状态 |
|--------|---------|
| T48 | ✅ 完整支持 |
| TL866II+ | ✅ 完整支持 |
| TL866A/CS | ✅ 完整支持 |
| T56 | ⚠️ 实验性支持 |
| T76 | ⚠️ 实验性支持 |

## 一键安装

```bash
curl -sSL https://raw.githubusercontent.com/qyjqio/Linux_T48/main/install.sh | bash
```

自动完成：安装依赖 → 编译 minipro → 下载芯片算法 → 安装 GUI → 创建桌面快捷方式。

## DEB 包安装

```bash
# 下载 deb 包
wget https://github.com/qyjqio/Linux_T48/releases/latest/download/linux-t48_1.0.0_amd64.deb

# 安装
sudo dpkg -i linux-t48_1.0.0_amd64.deb
sudo apt-get install -f
```

## 手动安装

```bash
# 1. 先安装 minipro 驱动
sudo apt install build-essential pkg-config libusb-1.0-0-dev zlib1g-dev python3-tk
git clone https://gitlab.com/DavidGriffith/minipro.git
cd minipro && make -j$(nproc) && sudo make install && sudo make udev

# 2. 安装 GUI
git clone https://github.com/qyjqio/Linux_T48.git
sudo cp Linux_T48/linux-t48.py /usr/local/bin/linux-t48
sudo chmod +x /usr/local/bin/linux-t48

# 3. 创建桌面快捷方式
cp Linux_T48/linux-t48.desktop ~/.local/share/applications/
```

## 使用方法

```bash
# 命令行启动
linux-t48

# 或在应用菜单搜索 "Linux_T48编程器"
```

### 常用操作

1. 插入 T48 编程器，打开软件，自动检测编程器
2. 搜索框输入芯片型号（如 `W25Q64`），点击选中
3. 选择 SPI 时钟速度（30MHz 最快，接线差用 4MHz）
4. 点击「读取芯片」/「写入芯片」/「擦除」等操作

### 命令行直接使用

```bash
# 读取芯片
minipro -p "W25Q64BV@SOIC8" -r backup.bin -o spi_clock=30

# 写入芯片
minipro -p "W25Q64BV@SOIC8" -w firmware.bin -o spi_clock=30

# 擦除芯片
minipro -p "W25Q64BV@SOIC8" -E

# 搜索支持的芯片
minipro -L "W25Q"
```

## 系统要求

- Ubuntu 20.04+ / Debian 11+ / Linux Mint 20+
- Python 3.8+
- USB 2.0 接口
- T48 或 TL866 系列编程器

## 致谢

- [minipro](https://gitlab.com/DavidGriffith/minipro) - 开源编程器驱动
- [XGecu](http://www.xgecu.com) - T48 编程器硬件

## 许可证

GPL-3.0
