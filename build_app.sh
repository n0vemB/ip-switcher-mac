#!/bin/bash

# 网络设置切换器 Mac应用构建脚本

echo "正在构建网络设置切换器 Mac应用..."

# 清理之前的构建
echo "清理之前的构建文件..."
rm -rf build dist

# 构建应用（使用别名模式，更快更小）
echo "构建应用（别名模式）..."
python3 setup.py py2app -A

if [ $? -eq 0 ]; then
    echo "✅ 应用构建成功！"
    echo "📍 应用位置: dist/网络设置切换器.app"
    echo ""
    echo "使用方法："
    echo "1. 双击 dist/网络设置切换器.app 启动应用"
    echo "2. 或者运行: open 'dist/网络设置切换器.app'"
    echo ""
    echo "注意：此应用需要管理员权限来修改网络设置"
    echo "首次运行时系统可能会要求输入密码"
    echo ""
    
    # 询问是否立即打开应用
    read -p "是否现在打开应用？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "dist/网络设置切换器.app"
    fi
else
    echo "❌ 应用构建失败"
    echo "请检查错误信息并重试"
fi
