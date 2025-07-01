import tkinter as tk
from tkinter import ttk
import subprocess
import re
import json
import os

class NetworkSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("网络设置切换器")
        self.root.geometry("500x600")

        # 加载配置
        self.config_file = os.path.expanduser('~/network_switcher_config.json')
        self.load_config()

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.create_widgets()

        # 初始化按钮状态（在网络状态检查之前）
        self.switch_var.set(False)  # 默认DHCP模式

        # 确保按钮显示正确颜色
        self.force_button_colors()

        # 更新当前网络状态
        self.update_network_status()

    def create_widgets(self):
        row = 0

        # 标题
        title_label = ttk.Label(self.main_frame, text="网络设置切换器", font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1

        # 当前网络信息区域
        info_frame = ttk.LabelFrame(self.main_frame, text="当前网络信息", padding="10")
        info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        info_frame.columnconfigure(1, weight=1)
        row += 1

        # 获取网络信息按钮
        self.refresh_button = ttk.Button(info_frame, text="🔄 获取当前网络配置", command=self.get_current_network_info)
        self.refresh_button.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))

        # 当前网络信息显示
        ttk.Label(info_frame, text="当前IP:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.current_ip_label = ttk.Label(info_frame, text="未获取", foreground="green")
        self.current_ip_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(info_frame, text="子网掩码:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.current_subnet_label = ttk.Label(info_frame, text="未获取", foreground="green")
        self.current_subnet_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(info_frame, text="路由器:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.current_router_label = ttk.Label(info_frame, text="未获取", foreground="green")
        self.current_router_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(info_frame, text="配置方式:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.current_method_label = ttk.Label(info_frame, text="未获取", foreground="green")
        self.current_method_label.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # 手动IP配置区域
        config_frame = ttk.LabelFrame(self.main_frame, text="手动IP配置", padding="10")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        row += 1

        # IP地址输入
        ttk.Label(config_frame, text="IP地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(config_frame, width=20)
        self.ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.ip_entry.insert(0, self.config.get('ip', ''))

        # 子网掩码输入
        ttk.Label(config_frame, text="子网掩码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subnet_entry = ttk.Entry(config_frame, width=20)
        self.subnet_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.subnet_entry.insert(0, self.config.get('subnet', ''))

        # 路由器输入
        ttk.Label(config_frame, text="路由器:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.router_entry = ttk.Entry(config_frame, width=20)
        self.router_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.router_entry.insert(0, self.config.get('router', ''))

        # 控制区域
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=row, column=0, columnspan=3, pady=(0, 15))
        row += 1

        # 开关样式的切换按钮
        self.switch_var = tk.BooleanVar(value=False)
        self.create_switch_button(control_frame)

        # 状态标签
        self.status_label = ttk.Label(self.main_frame, text="", font=("Arial", 10))
        self.status_label.grid(row=row, column=0, columnspan=3, pady=5)

    def create_switch_button(self, parent):
        """创建开关按钮"""
        switch_frame = ttk.Frame(parent)
        switch_frame.pack(pady=25)

        # 标题
        title_label = ttk.Label(switch_frame, text="网络配置模式", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # 按钮容器
        button_container = tk.Frame(switch_frame, bg=self.root.cget('bg'))
        button_container.pack()

        # 按钮统一尺寸
        button_width = 140
        button_height = 50

        # DHCP按钮 - 使用Canvas创建自定义按钮
        dhcp_frame = tk.Frame(button_container, bg=self.root.cget('bg'))
        dhcp_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.dhcp_canvas = tk.Canvas(dhcp_frame, width=button_width, height=button_height, highlightthickness=0)
        self.dhcp_canvas.pack()

        # 绘制DHCP按钮（圆角矩形）
        self.dhcp_rect = self.create_rounded_rect(self.dhcp_canvas, 2, 2, button_width-2, button_height-2, 10, "#007AFF")
        self.dhcp_text = self.dhcp_canvas.create_text(button_width//2, button_height//2, text="DHCP", fill="white", font=("Arial", 16, "bold"))

        # 绑定点击事件
        self.dhcp_canvas.bind("<Button-1>", lambda e: self.dhcp_button_click())
        self.dhcp_canvas.bind("<ButtonRelease-1>", lambda e: self.dhcp_button_release())
        self.dhcp_canvas.bind("<Enter>", lambda e: self.dhcp_canvas.config(cursor="hand2"))
        self.dhcp_canvas.bind("<Leave>", lambda e: self.dhcp_canvas.config(cursor=""))

        # 手动按钮 - 使用Canvas创建自定义按钮
        manual_frame = tk.Frame(button_container, bg=self.root.cget('bg'))
        manual_frame.pack(side=tk.LEFT, padx=(20, 0))

        self.manual_canvas = tk.Canvas(manual_frame, width=button_width, height=button_height, highlightthickness=0)
        self.manual_canvas.pack()

        # 绘制手动按钮（圆角矩形）
        self.manual_rect = self.create_rounded_rect(self.manual_canvas, 2, 2, button_width-2, button_height-2, 10, "#34C759")
        self.manual_text = self.manual_canvas.create_text(button_width//2, button_height//2, text="手动模式", fill="white", font=("Arial", 16, "bold"))

        # 绑定点击事件
        self.manual_canvas.bind("<Button-1>", lambda e: self.manual_button_click())
        self.manual_canvas.bind("<ButtonRelease-1>", lambda e: self.manual_button_release())
        self.manual_canvas.bind("<Enter>", lambda e: self.manual_canvas.config(cursor="hand2"))
        self.manual_canvas.bind("<Leave>", lambda e: self.manual_canvas.config(cursor=""))

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill_color):
        """创建圆角矩形"""
        points = []
        # 左上角
        points.extend([x1 + radius, y1])
        # 右上角
        points.extend([x2 - radius, y1])
        points.extend([x2, y1])
        points.extend([x2, y1 + radius])
        # 右下角
        points.extend([x2, y2 - radius])
        points.extend([x2, y2])
        points.extend([x2 - radius, y2])
        # 左下角
        points.extend([x1 + radius, y2])
        points.extend([x1, y2])
        points.extend([x1, y2 - radius])
        # 回到左上角
        points.extend([x1, y1 + radius])
        points.extend([x1, y1])
        points.extend([x1 + radius, y1])

        return canvas.create_polygon(points, fill=fill_color, outline="", smooth=True)

    def dhcp_button_click(self):
        """DHCP按钮点击效果"""
        # 变暗效果
        self.dhcp_canvas.itemconfig(self.dhcp_rect, fill="#0056CC")
        self.root.after(100, lambda: self.set_switch_state(False))

    def dhcp_button_release(self):
        """DHCP按钮释放效果"""
        # 恢复原色
        self.dhcp_canvas.itemconfig(self.dhcp_rect, fill="#007AFF")

    def manual_button_click(self):
        """手动按钮点击效果"""
        # 变暗效果
        self.manual_canvas.itemconfig(self.manual_rect, fill="#28A745")
        self.root.after(100, lambda: self.set_switch_state(True))

    def manual_button_release(self):
        """手动按钮释放效果"""
        # 恢复原色
        self.manual_canvas.itemconfig(self.manual_rect, fill="#34C759")

    def force_button_colors(self):
        """强制设置按钮颜色"""
        try:
            # 更新Canvas按钮颜色（圆角矩形）
            self.dhcp_canvas.itemconfig(self.dhcp_rect, fill="#007AFF")
            self.dhcp_canvas.itemconfig(self.dhcp_text, fill="white")

            self.manual_canvas.itemconfig(self.manual_rect, fill="#34C759")
            self.manual_canvas.itemconfig(self.manual_text, fill="white")

            # 强制刷新显示
            self.dhcp_canvas.update()
            self.manual_canvas.update()
        except Exception as e:
            print(f"Error setting button colors: {e}")

    def update_switch_visual(self, is_manual):
        """更新开关的视觉状态"""
        # 强制设置按钮颜色
        self.force_button_colors()

    def set_switch_state(self, is_manual):
        """设置开关状态"""
        self.update_switch_visual(is_manual)
        self.switch_var.set(is_manual)

        # 执行网络切换
        self.toggle_network()

    def get_current_network_info(self):
        """获取当前网络配置信息"""
        try:
            self.refresh_button.config(text="🔄 获取中...", state="disabled")
            self.root.update()

            # 获取当前网络设置状态
            result = subprocess.run(['networksetup', '-getinfo', 'Wi-Fi'],
                                 capture_output=True, text=True)

            if result.returncode != 0:
                self.status_label.config(text="❌ 错误：无法获取网络信息")
                return

            output = result.stdout

            # 解析网络信息
            ip_address = "未获取"
            subnet_mask = "未获取"
            router = "未获取"
            config_method = "未知"

            # 解析输出
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('IP address:'):
                    ip_address = line.split(':', 1)[1].strip()
                elif line.startswith('Subnet mask:'):
                    subnet_mask = line.split(':', 1)[1].strip()
                elif line.startswith('Router:'):
                    router = line.split(':', 1)[1].strip()

            # 判断配置方式
            if 'DHCP Configuration' in output:
                config_method = "DHCP (自动获取)"
            elif 'Manual Configuration' in output:
                config_method = "手动配置"

            # 更新显示
            self.current_ip_label.config(text=ip_address if ip_address else "未获取")
            self.current_subnet_label.config(text=subnet_mask if subnet_mask else "未获取")
            self.current_router_label.config(text=router if router else "未获取")
            self.current_method_label.config(text=config_method)

            # 根据当前配置更新开关状态（不触发网络切换）
            if 'Manual Configuration' in output:
                self.update_switch_visual(True)
                self.switch_var.set(True)
            else:
                self.update_switch_visual(False)
                self.switch_var.set(False)

            self.status_label.config(text="✅ 网络信息获取成功")

        except Exception as e:
            self.status_label.config(text=f"❌ 错误：{str(e)}")
            print(f"Error: {e}")  # 调试信息
        finally:
            self.refresh_button.config(text="🔄 获取当前网络配置", state="normal")

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'ip': '',
                'subnet': '',
                'router': ''
            }
    
    def save_config(self):
        self.config = {
            'ip': self.ip_entry.get(),
            'subnet': self.subnet_entry.get(),
            'router': self.router_entry.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def update_network_status(self):
        try:
            # 获取当前网络设置状态
            result = subprocess.run(['networksetup', '-getinfo', 'Wi-Fi'],
                                 capture_output=True, text=True)

            # 根据当前网络设置更新开关状态（不触发网络切换）
            if 'DHCP Configuration' in result.stdout:
                self.update_switch_visual(False)
                self.switch_var.set(False)
            else:
                self.update_switch_visual(True)
                self.switch_var.set(True)

        except Exception as e:
            self.status_label.config(text=f"❌ 错误：{str(e)}")

        # 每10秒更新一次（减少频率）
        self.root.after(10000, self.update_network_status)
    
    def toggle_network(self):
        try:
            # 显示正在切换状态
            if self.switch_var.get():
                self.status_label.config(text="🔄 正在切换到手动IP...")
            else:
                self.status_label.config(text="🔄 正在切换到DHCP...")
            self.root.update()

            # 获取网络服务名称
            result = subprocess.run(['networksetup', '-listallnetworkservices'],
                                 capture_output=True, text=True)
            wifi_service = None
            for line in result.stdout.split('\n'):
                if 'Wi-Fi' in line:
                    wifi_service = line.strip()
                    break

            if not wifi_service:
                self.status_label.config(text="❌ 错误：未找到WiFi服务")
                return

            if self.switch_var.get():  # 切换到手动IP
                ip = self.ip_entry.get().strip()
                subnet = self.subnet_entry.get().strip()
                router = self.router_entry.get().strip()

                if not all([ip, subnet, router]):
                    self.status_label.config(text="⚠️ 请填写所有网络设置")
                    return

                cmd = [
                    'networksetup',
                    '-setmanual',
                    wifi_service,
                    ip,
                    subnet,
                    router
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    self.save_config()
                    self.status_label.config(text=f"✅ 已切换到手动IP: {ip}")
                    # 延迟更新网络信息显示
                    self.root.after(2000, self.get_current_network_info)
                else:
                    self.status_label.config(text=f"❌ 错误：{result.stderr}")

            else:  # 切换到DHCP
                result = subprocess.run(['networksetup', '-setdhcp', wifi_service],
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    self.status_label.config(text="✅ 已切换到DHCP (自动获取IP)")
                    # 延迟更新网络信息显示
                    self.root.after(2000, self.get_current_network_info)
                else:
                    self.status_label.config(text=f"❌ 错误：{result.stderr}")

        except Exception as e:
            self.status_label.config(text=f"❌ 错误：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSwitcher(root)
    root.mainloop() 