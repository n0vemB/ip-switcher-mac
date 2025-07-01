#!/bin/bash

# 网络设置切换器 DMG 创建脚本
# 版本: 1.1.0

echo "🚀 开始创建 DMG 安装包..."

# 设置变量
APP_NAME="网络设置切换器"
VERSION="1.1.0"
DMG_NAME="${APP_NAME}_v${VERSION}"
SOURCE_APP="dist/${APP_NAME}.app"
DMG_DIR="dmg_temp"
FINAL_DMG="dist/${DMG_NAME}.dmg"

# 检查应用是否存在
if [ ! -d "$SOURCE_APP" ]; then
    echo "❌ 错误：找不到应用文件 $SOURCE_APP"
    echo "请先运行 ./build_app.sh 构建应用"
    exit 1
fi

# 清理之前的临时文件
echo "🧹 清理临时文件..."
rm -rf "$DMG_DIR"
rm -f "$FINAL_DMG"

# 创建临时目录
echo "📁 创建临时目录..."
mkdir -p "$DMG_DIR"

# 复制应用到临时目录
echo "📋 复制应用文件..."
cp -R "$SOURCE_APP" "$DMG_DIR/"

# 创建应用程序文件夹的符号链接
echo "🔗 创建应用程序文件夹链接..."
ln -s /Applications "$DMG_DIR/Applications"

# 创建README文件
echo "📝 创建安装说明..."
cat > "$DMG_DIR/安装说明.txt" << EOF
网络设置切换器 v${VERSION} 安装说明
=====================================

📦 安装方法：
1. 将 "${APP_NAME}.app" 拖拽到 "Applications" 文件夹
2. 在启动台或应用程序文件夹中找到并启动应用
3. 首次运行时，系统可能要求输入管理员密码

⚠️  重要提示：
- 此应用需要管理员权限来修改网络设置
- 请确保输入正确的网络配置信息
- 主要针对Wi-Fi网络接口

🎯 使用方法：
- 蓝色按钮：切换到DHCP自动获取IP
- 绿色按钮：切换到手动IP设置
- 配置信息会自动保存

📞 技术支持：
- GitHub: https://github.com/n0vemB/ip-switcher-mac
- 版本: v${VERSION}

© 2024 Network Switcher. All Rights Reserved.
EOF

# 创建DMG
echo "💿 创建 DMG 文件..."
hdiutil create -volname "${APP_NAME} v${VERSION}" \
    -srcfolder "$DMG_DIR" \
    -ov -format UDZO \
    -imagekey zlib-level=9 \
    "$FINAL_DMG"

# 检查DMG创建是否成功
if [ $? -eq 0 ]; then
    echo "✅ DMG 创建成功！"
    echo "📍 文件位置: $FINAL_DMG"
    
    # 显示文件大小
    DMG_SIZE=$(du -h "$FINAL_DMG" | cut -f1)
    echo "📏 文件大小: $DMG_SIZE"
    
    # 清理临时文件
    echo "🧹 清理临时文件..."
    rm -rf "$DMG_DIR"
    
    echo ""
    echo "🎉 DMG 安装包创建完成！"
    echo "📦 可以上传 $FINAL_DMG 到 GitHub Release"
    echo ""
    echo "使用方法："
    echo "1. 上传到 GitHub Release"
    echo "2. 用户下载后双击打开DMG"
    echo "3. 拖拽应用到Applications文件夹"
    
else
    echo "❌ DMG 创建失败"
    exit 1
fi
