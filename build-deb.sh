#!/bin/bash
# 构建 deb 包脚本
VERSION="1.0.0"
PKG="linux-t48_${VERSION}_amd64"

rm -rf "debian/${PKG}"
mkdir -p "debian/${PKG}/DEBIAN"
mkdir -p "debian/${PKG}/usr/local/bin"
mkdir -p "debian/${PKG}/usr/share/applications"

cp debian/linux-t48_1.0.0_amd64/DEBIAN/control "debian/${PKG}/DEBIAN/"
cp debian/linux-t48_1.0.0_amd64/DEBIAN/postinst "debian/${PKG}/DEBIAN/"
chmod 755 "debian/${PKG}/DEBIAN/postinst"

cp linux-t48.py "debian/${PKG}/usr/local/bin/linux-t48"
chmod 755 "debian/${PKG}/usr/local/bin/linux-t48"
cp linux-t48.desktop "debian/${PKG}/usr/share/applications/"

dpkg-deb --build "debian/${PKG}" "${PKG}.deb"
echo "构建完成: ${PKG}.deb"
