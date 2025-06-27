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
        
        # 加载配置
        self.config_file = os.path.expanduser('~/network_switcher_config.json')
        self.load_config()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # IP地址输入
        ttk.Label(self.main_frame, text="IP地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(self.main_frame)
        self.ip_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.ip_entry.insert(0, self.config.get('ip', ''))
        
        # 子网掩码输入
        ttk.Label(self.main_frame, text="子网掩码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subnet_entry = ttk.Entry(self.main_frame)
        self.subnet_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.subnet_entry.insert(0, self.config.get('subnet', ''))
        
        # 路由器输入
        ttk.Label(self.main_frame, text="路由器:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.router_entry = ttk.Entry(self.main_frame)
        self.router_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.router_entry.insert(0, self.config.get('router', ''))
        
        # 切换按钮
        self.switch_var = tk.BooleanVar(value=False)
        self.switch_button = ttk.Checkbutton(
            self.main_frame,
            text="使用手动IP",
            variable=self.switch_var,
            command=self.toggle_network
        )
        self.switch_button.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(self.main_frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # 更新当前网络状态
        self.update_network_status()
        
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
            
            # 根据当前网络设置更新复选框状态
            if 'DHCP Configuration' in result.stdout:
                self.switch_var.set(False)
            else:
                self.switch_var.set(True)
            
        except Exception as e:
            self.status_label.config(text=f"错误：{str(e)}")
        
        # 每5秒更新一次
        self.root.after(5000, self.update_network_status)
    
    def toggle_network(self):
        try:
            # 获取网络服务名称
            result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                                 capture_output=True, text=True)
            wifi_service = None
            for line in result.stdout.split('\n'):
                if 'Wi-Fi' in line:
                    wifi_service = line.strip()
                    break
            
            if not wifi_service:
                self.status_label.config(text="错误：未找到WiFi服务")
                return
            
            if self.switch_var.get():  # 切换到手动IP
                ip = self.ip_entry.get()
                subnet = self.subnet_entry.get()
                router = self.router_entry.get()
                
                if not all([ip, subnet, router]):
                    self.status_label.config(text="请填写所有网络设置")
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
                    self.status_label.config(text="已切换到手动IP设置")
                else:
                    self.status_label.config(text=f"错误：{result.stderr}")
                
            else:  # 切换到DHCP
                result = subprocess.run(['networksetup', '-setdhcp', wifi_service], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    self.status_label.config(text="已切换到DHCP")
                else:
                    self.status_label.config(text=f"错误：{result.stderr}")
                
        except Exception as e:
            self.status_label.config(text=f"错误：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSwitcher(root)
    root.mainloop() 