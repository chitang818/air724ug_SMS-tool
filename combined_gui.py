import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import serial
import serial.tools.list_ports
import threading
import time
import re
import datetime

class CombinedAir724UGTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Air724UG&780 综合工具")
        self.root.geometry("1100x800")  # 增大窗口宽度以优化界面
        self.root.resizable(True, True)

        # 设置字体支持中文
        self.font = ("SimHei", 10)
        self.bold_font = font.Font(family="SimHei", size=10, weight="bold")

        # 高DPI屏幕适配
        try:
            self.root.tk.call('tk', 'scaling', 1.5)
        except:
            pass

        # 设置主题颜色 - 高级现代专业配色方案
        # 主色系统
        self.primary_color = "#2c7be5"    # 专业蓝色主色
        self.primary_light = "#408ef7"   # 主色浅色变体
        self.primary_dark = "#1d62cc"    # 主色深色变体
        
        # 辅助色系统
        self.success_color = "#28a745"   # 成功状态绿色
        self.warning_color = "#ffc107"   # 警告状态黄色
        self.error_color = "#dc3545"     # 错误状态红色
        self.info_color = "#17a2b8"      # 信息状态蓝色
        
        # 中性色系统
        self.bg_color = "#f8f9fa"         # 极浅灰色背景，更柔和舒适
        self.bg_light = "#ffffff"        # 白色背景用于框架
        self.bg_dark = "#e9ecef"         # 深灰色背景用于区分区域
        self.text_color = "#000000"      # 纯黑色文本，提高可见度
        self.text_secondary = "#6c757d"  # 次要文本颜色
        self.border_color = "#dee2e6"    # 边框颜色
        self.log_bg_color = "#fefefe"    # 日志框背景色
        
        # 强调色（用于重要按钮和高亮）
        self.accent_color = self.primary_color

        # 设置窗口背景和提升视觉层次感
        self.root.configure(bg=self.bg_color)
        
        # 添加自定义的背景样式 - 创建轻微的渐变效果
        # 创建一个主背景框架，用于实现更好的视觉效果
        self.background_frame = ttk.Frame(root, style="Main.TFrame")
        self.background_frame.pack(fill="both", expand=True)
        
        # 为主要区域添加轻微的阴影效果（通过嵌套框架实现视觉层次）
        self.shadow_frame = ttk.Frame(self.background_frame, style="Main.TFrame")
        self.shadow_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 串口相关变量 - 短信助手端口
        self.sms_ser = None
        self.sms_port_var = tk.StringVar()
        self.sms_baudrate_var = tk.StringVar(value="115200")
        self.sms_connected = False

        # 串口相关变量 - 系统日志端口
        self.monitor_ser = None
        self.monitor_port_var = tk.StringVar()
        self.monitor_baudrate_var = tk.StringVar(value="115200")
        self.monitor_databits_var = tk.StringVar(value="8")
        self.monitor_stopbits_var = tk.StringVar(value="1")
        self.monitor_parity_var = tk.StringVar(value="N")
        self.monitor_connected = False
        self.monitor_running = False
        self.monitor_thread = None

        # 设备信息变量
        self.phone_number_var = tk.StringVar(value="未连接")
        self.carrier_var = tk.StringVar()

        # 短信发送变量
        self.sms_phone_var = tk.StringVar()
        self.sms_count_var = tk.StringVar(value="发送统计: 共发送 0 条，成功 0 条")
        self.sms_sent_count = 0
        self.sms_success_count = 0
        
        # 最新短信信息，用于存储最近收到的短信的完整信息
        self.latest_sms_info = {}
        
        # 自动复制验证码复选框变量
        self.auto_copy_verification_var = tk.BooleanVar(value=False)
        
        # 设备断开连接日志标志
        self._device_disconnected_logged = False

        # 日志类型选择变量
        self.log_type = tk.StringVar(value="all")
        # 日志缓存，按类型分类
        self.all_logs = []
        self.sms_logs = []
        self.monitor_logs = []

        # ========== UI位置配置 ==========
        # 统一管理所有UI元素的位置参数，便于集中修改
        # 紧凑化设计参数，减少留白，增强信息密度
        self.ui_layout = {
            # 主框架边距 - 适度减少以增加内容区域
            'main_padx': 6,
            'main_pady': 4,
            
            # 左侧面板 - 优化比例以平衡内容展示
            'left_frame_width': 420,
            'left_padx': 4,
            'left_pady': 4,
            
            # 右侧面板 - 调整边距以优化整体布局
            'right_padx': 4,
            'right_pady': 4,
            
            # 通用控件边距 - 微调以增强内容紧凑性
            'control_padx': 4,
            'control_pady': 3,
            'button_padx': 4,
            'button_pady': 2,
            
            # 设备连接控制区域
            'connect_frame_padx': 5,
            'connect_frame_pady': 3,
            
            # 设备信息区域
            'info_frame_padx': 5,
            'info_frame_pady': 3,
            'device_info_frame_padx': 5,
            'info_grid_padx': 2,
            'info_grid_pady': 1,
            
            # 短信发送区域
            'sms_frame_padx': 4,
            'sms_frame_pady': 3,
            'sms_entry_width': 22,
            'sms_text_width': 32,
            'sms_text_height': 5,
            'button_frame_pady': 2,
            
            # 日志区域
            'log_frame_padx': 4,
            'log_frame_pady': 2,
            'filter_frame_padx': 4,
            'filter_frame_pady': 2,
            'filter_radio_padx': 4,
            'clear_btn_padx': 4,
            
            # 按钮坐标和尺寸（x, y表示中心点坐标，w, h表示宽度和高度）
            'copy_phone_btn': {'x': 600, 'y': 195, 'w': 120, 'h': 30},
            'send_btn': {'x': 100, 'y': 300, 'w': 120, 'h': 30},
            'clear_btn': {'x': 500, 'y': 30, 'w': 100, 'h': 25}
        }
        
        # 创建主框架 - 使用shadow_frame作为父容器以实现视觉效果
        self.main_frame = ttk.Frame(self.shadow_frame, style="Main.TFrame")
        self.main_frame.pack(expand=1, fill="both", padx=self.ui_layout['main_padx'], pady=self.ui_layout['main_pady'])
        
        # ========== 配置ttk样式 - 高级现代UI风格 ==========
        self.style = ttk.Style()
        
        # 提升高DPI支持和字体渲染质量
        self.style.configure(".", font=self.font)
        
        # 基础框架样式 - 增加立体感和层次感
        self.style.configure("Main.TFrame", background=self.bg_light, borderwidth=0)
        self.style.configure("Left.TFrame", background=self.bg_light, borderwidth=1, relief="solid", bordercolor=self.border_color)
        self.style.configure("Right.TFrame", background=self.bg_light, borderwidth=1, relief="solid", bordercolor=self.border_color)
        
        # 高级分组框样式 - 增加精细视觉层次
        self.style.configure("TLabelFrame", 
                            background=self.bg_light, 
                            foreground=self.primary_color, 
                            font=(self.font[0], self.font[1], "bold"),  # 标题加粗以提升层次感
                            bordercolor=self.border_color, 
                            borderwidth=1, 
                            padding=8, 
                            relief="flat")
        
        # 标签样式 - 区分主次文本
        self.style.configure("TLabel", 
                            background=self.bg_light, 
                            foreground=self.text_color, 
                            font=self.font, 
                            padding=2)
        self.style.configure("Secondary.TLabel", 
                            background=self.bg_light, 
                            foreground=self.text_secondary, 
                            font=self.font, 
                            padding=2)
        
        # 主标题样式 - 用于左侧面板和右侧面板的区域标题
        self.style.configure("Title.TLabel",
                            background=self.bg_light,
                            foreground=self.primary_color,
                            font=(self.font[0], self.font[1] + 1, "bold"),  # 标题加粗并稍大
                            padding=3)

        # 次要标题样式 - 用于子区域或功能模块标题
        self.style.configure("Subtitle.TLabel",
                            background=self.bg_light,
                            foreground=self.text_secondary,
                            font=(self.font[0], self.font[1], "normal"),
                            padding=3)
        
        # 按钮样式 - 扁平化设计带平滑动画过渡
        self.style.configure("TButton", 
                            background=self.bg_dark, 
                            foreground=self.text_color, 
                            font=self.font, 
                            padding=6, 
                            borderwidth=0, 
                            relief="flat", 
                            borderradius=3)
        # 添加悬停和点击动画效果
        self.style.map("TButton", 
                      background=[("active", "#dee2e6"), ("disabled", "#f8f9fa")],
                      foreground=[("", "#000000"), ("active", "#000000"), ("disabled", "#adb5bd")],
                      relief=[("pressed", "flat")],
                      padding=[("active", 7)])  # 轻微增大内边距作为悬停反馈
        
        # 强调按钮样式 - 现代化设计带微动画
        self.style.configure("Accent.TButton", 
                            background=self.accent_color, 
                            foreground="#000000",  # 黑色文本以提高可见度
                            font=self.font, 
                            padding=6, 
                            borderwidth=0, 
                            relief="flat", 
                            borderradius=3)
        # 添加更丰富的交互动画效果
        self.style.map("Accent.TButton", 
                      background=[("active", self.primary_dark), ("disabled", "#b8c2cc")],
                      foreground=[("", "#000000"), ("active", "#000000"), ("disabled", "#000000")],
                      relief=[("pressed", "flat")],
                      padding=[("active", 7)])  # 轻微增大内边距作为悬停反馈
        
        # 下拉框样式 - 增加焦点和悬停状态动画
        self.style.configure("TCombobox", 
                            background=self.bg_light, 
                            foreground=self.text_color,
                            fieldbackground=self.bg_light, 
                            bordercolor=self.border_color, 
                            borderwidth=1, 
                            padding=5, 
                            relief="flat")
        self.style.map("TCombobox", 
                      fieldbackground=[("readonly", self.bg_dark), ("active", "#f8f9fa")],
                      foreground=[("readonly", self.text_color)],
                      bordercolor=[("focus", self.primary_color), ("active", self.primary_light)],
                      padding=[("active", 6)])
        
        # 输入框样式 - 增加焦点动画效果
        self.style.configure("Main.TEntry", 
                            fieldbackground=self.bg_light, 
                            foreground=self.text_color, 
                            borderwidth=1, 
                            bordercolor=self.border_color, 
                            padding=5, 
                            relief="flat")
        self.style.map("Main.TEntry", 
                      bordercolor=[("focus", self.primary_color), ("active", self.primary_light)],
                      fieldbackground=[("disabled", self.bg_dark), ("focus", "#f8f9fa")],
                      padding=[("focus", 6)])  # 轻微增加焦点时的内边距
        
        # 单选按钮样式
        self.style.configure("TRadiobutton", 
                            background=self.bg_light, 
                            foreground=self.text_color, 
                            selectcolor=self.primary_color, 
                            padding=4)
        
        # 复选框样式
        self.style.configure("TCheckbutton", 
                            background=self.bg_light, 
                            foreground=self.text_color, 
                            selectcolor=self.primary_color, 
                            padding=4)
        
        # 分隔线样式
        self.style.configure("TSeparator", 
                            background=self.border_color, 
                            padding=2)

        # 创建左侧面板(包含串口设置、SIM卡信息和短信发送)
        self.left_frame = ttk.Frame(self.main_frame, width=self.ui_layout['left_frame_width'], style="Left.TFrame")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=self.ui_layout['left_padx'], pady=self.ui_layout['left_pady'])
        self.left_frame.pack_propagate(False)

        # 添加左侧面板标题 - 使用主标题样式增强视觉效果
        left_title = ttk.Label(self.left_frame, text="设备控制中心", style="Title.TLabel")
        left_title.pack(pady=(10, 5))
        
        # 添加标题下划线
        title_separator = ttk.Separator(self.left_frame)
        title_separator.pack(fill=tk.X, padx=10, pady=2)

        # 移除独立的状态指示灯区域，将在设备连接控制区域内显示

        # 创建状态栏 - 提前初始化status_var
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 初始化界面组件
        self.init_ui_components()

        # 运营商识别前缀
        self.carrier_prefixes = {
            '中国移动': ['134', '135', '136', '137', '138', '139', '147', '150', '151', '152', '157', '158', '159', '172', '178', '182', '183', '184', '187', '188', '198'],
            '中国联通': ['130', '131', '132', '145', '155', '156', '166', '171', '175', '176', '185', '186'],
            '中国电信': ['133', '149', '153', '173', '177', '180', '181', '189', '199']
        }

        # 初始刷新端口并检查是否有可用端口
        if self.refresh_ports():
            # 有可用端口时，设置自动连接
            self.root.after(1000, self.auto_connect_all_ports)
        
        # 启动定期检查端口存在性的定时器
        self.start_port_monitoring()

    def init_ui_components(self):
        # 设备连接控制
        connect_frame = ttk.LabelFrame(self.left_frame, text="设备连接控制")
        connect_frame.pack(fill=tk.X, padx=self.ui_layout['connect_frame_padx'], pady=self.ui_layout['connect_frame_pady'])

        # 配置列权重，使三列均分宽度
        connect_frame.columnconfigure(0, weight=1)
        connect_frame.columnconfigure(1, weight=1)
        connect_frame.columnconfigure(2, weight=1)
        
        # 端口状态指示区域 - 优化布局
        status_frame = ttk.Frame(connect_frame, style="Main.TFrame")
        status_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="ew")
        
        # 创建居中容器框架
        center_frame = ttk.Frame(status_frame, style="Main.TFrame")
        center_frame.pack(fill=tk.X, expand=True)
        
        # 创建更美观的状态指示器
        # 短信端口状态
        sms_port_frame = ttk.Frame(center_frame, style="Main.TFrame")
        sms_port_frame.pack(side=tk.LEFT, padx=(75, 30))  # 调整左侧边距使其向右移动一些
        ttk.Label(sms_port_frame, text="短信端口", font=self.font).pack(side=tk.LEFT, padx=(0, 8))
        self.sms_status_led = ttk.Label(sms_port_frame, text="●", font=font.Font(size=16), foreground=self.error_color)
        self.sms_status_led.pack(side=tk.LEFT)
        
        # 系统端口状态
        monitor_port_frame = ttk.Frame(center_frame, style="Main.TFrame")
        monitor_port_frame.pack(side=tk.LEFT)
        ttk.Label(monitor_port_frame, text="系统端口", font=self.font).pack(side=tk.LEFT, padx=(0, 8))
        self.monitor_status_led = ttk.Label(monitor_port_frame, text="●", font=font.Font(size=16), foreground=self.error_color)
        self.monitor_status_led.pack(side=tk.LEFT)

        # 连接设备按钮
        self.connect_all_btn = ttk.Button(connect_frame, text="连接设备", command=self.auto_connect_all_ports, width=12, style="Accent.TButton")
        self.connect_all_btn.grid(row=1, column=0, padx=8, pady=(5, 10), sticky="ew")

        # 断开设备按钮
        self.disconnect_all_btn = ttk.Button(connect_frame, text="断开设备", command=self.disconnect_all_ports, width=12, style="Accent.TButton")
        self.disconnect_all_btn.grid(row=1, column=1, padx=8, pady=(5, 10), sticky="ew")

        # 读取SIM卡按钮
        self.read_sim_btn = ttk.Button(connect_frame, text="读取SIM卡", command=self.read_sim_info, width=12, style="Accent.TButton")
        self.read_sim_btn.grid(row=1, column=2, padx=8, pady=(5, 10), sticky="ew")

        # 串口设置区域 - 短信助手 (隐藏)
        sms_port_frame = ttk.LabelFrame(self.left_frame, text="短信助手端口设置")
        sms_port_frame.pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])
        sms_port_frame.pack_forget()  # 隐藏端口设置

        # 创建一个框架来放置短信端口控件，使用网格布局
        sms_port_controls = ttk.Frame(sms_port_frame, style="Main.TFrame")
        sms_port_controls.pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 端口选择
        ttk.Label(sms_port_controls, text="端口:", font=self.font).grid(row=0, column=0, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.sms_port_combo = ttk.Combobox(sms_port_controls, textvariable=self.sms_port_var, width=15)
        self.sms_port_combo.grid(row=0, column=1, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 波特率选择
        ttk.Label(sms_port_controls, text="波特率:", font=self.font).grid(row=1, column=0, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.sms_baudrate_combo = ttk.Combobox(sms_port_controls, textvariable=self.sms_baudrate_var, values=["9600", "19200", "38400", "57600", "115200"], width=15)
        self.sms_baudrate_combo.grid(row=1, column=1, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 创建按钮框架
        sms_btn_frame = ttk.Frame(sms_port_controls, style="Main.TFrame")
        sms_btn_frame.grid(row=0, column=2, rowspan=2, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.NS)



        # 串口设置区域 - 监控工具 (隐藏)
        monitor_port_frame = ttk.LabelFrame(self.left_frame, text="监控工具端口设置")
        monitor_port_frame.pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])
        monitor_port_frame.pack_forget()  # 隐藏端口设置

        # 创建一个框架来放置系统日志端口控件
        monitor_port_controls = ttk.Frame(monitor_port_frame, style="Main.TFrame")
        monitor_port_controls.pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 端口选择
        ttk.Label(monitor_port_controls, text="端口:", font=self.font).grid(row=0, column=0, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.monitor_port_combo = ttk.Combobox(monitor_port_controls, textvariable=self.monitor_port_var, width=15)
        self.monitor_port_combo.grid(row=0, column=1, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 波特率选择
        ttk.Label(monitor_port_controls, text="波特率:", font=self.font).grid(row=0, column=2, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.monitor_baudrate_combo = ttk.Combobox(monitor_port_controls, textvariable=self.monitor_baudrate_var, values=['9600', '19200', '38400', '57600', '115200', '230400', '460800'], width=10)
        self.monitor_baudrate_combo.grid(row=0, column=3, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 数据位选择
        ttk.Label(monitor_port_controls, text="数据位:", font=self.font).grid(row=1, column=0, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.monitor_databits_combo = ttk.Combobox(monitor_port_controls, textvariable=self.monitor_databits_var, values=['5', '6', '7', '8'], width=10)
        self.monitor_databits_combo.grid(row=1, column=1, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 停止位选择
        ttk.Label(monitor_port_controls, text="停止位:", font=self.font).grid(row=1, column=2, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.monitor_stopbits_combo = ttk.Combobox(monitor_port_controls, textvariable=self.monitor_stopbits_var, values=['1', '1.5', '2'], width=10)
        self.monitor_stopbits_combo.grid(row=1, column=3, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 校验位选择
        ttk.Label(monitor_port_controls, text="校验位:", font=self.font).grid(row=2, column=0, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.W)
        self.monitor_parity_combo = ttk.Combobox(monitor_port_controls, textvariable=self.monitor_parity_var, values=['N', 'E', 'O', 'M', 'S'], width=10)
        self.monitor_parity_combo.grid(row=2, column=1, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'])

        # 创建按钮框架
        monitor_btn_frame = ttk.Frame(monitor_port_controls, style="Main.TFrame")
        monitor_btn_frame.grid(row=0, column=4, rowspan=3, padx=self.ui_layout['control_padx'], pady=self.ui_layout['control_pady'], sticky=tk.NS)

        # 刷新端口按钮已移除



        # 添加分隔线
        ttk.Separator(self.left_frame).pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=5)

        # SIM卡信息区域 (已隐藏)
        sim_frame = ttk.LabelFrame(self.left_frame, text="SIM卡信息")
        # 使用pack_forget()隐藏SIM卡信息区域
        sim_frame.pack_forget()

        # 移除端口状态文字显示
        pass

        # 添加分隔线
        ttk.Separator(self.left_frame).pack(fill=tk.X, padx=self.ui_layout['control_padx'], pady=2)
        
        # 设备信息区域 - 极致紧凑化布局
        device_info_frame = ttk.LabelFrame(self.left_frame, text="设备信息")
        device_info_frame.pack(fill=tk.X, padx=self.ui_layout['device_info_frame_padx'], pady=(0, 1))  # 进一步减少下方内边距至1
        
        # 创建一个新的变量用于设备名称显示
        self.device_display_var = tk.StringVar(value="设备未连接")
        
        # 设备信息紧凑布局
        info_grid_frame = ttk.Frame(device_info_frame)
        info_grid_frame.pack(fill=tk.X, padx=4, pady=0)  # 减少左右内边距至4
        
        # 使用grid布局 - 极致紧凑配置
        info_grid_frame.columnconfigure(0, weight=0, minsize=75)  # 进一步缩小标签列宽度至75
        info_grid_frame.columnconfigure(1, weight=1, minsize=180)  # 缩小号码显示列至180
        info_grid_frame.columnconfigure(2, weight=0, minsize=22)  # 进一步缩小复制按钮列宽度至22
        info_grid_frame.rowconfigure(0, weight=0)
        info_grid_frame.rowconfigure(1, weight=0)
        
        # 设备名称显示 - 极致紧凑布局
        ttk.Label(info_grid_frame, text="设备名称:", font=self.font, anchor="w").grid(row=0, column=0, padx=(0, 2), pady=(0, 0), sticky="w")
        device_name_display = ttk.Label(info_grid_frame, textvariable=self.device_display_var, font=self.bold_font, foreground=self.accent_color)
        device_name_display.grid(row=0, column=1, padx=(0, 4), pady=(0, 0), sticky="w")
        
        # 当前号码显示 - 极致紧凑布局
        ttk.Label(info_grid_frame, text="当前号码:", font=self.font, anchor="w").grid(row=1, column=0, padx=(0, 2), pady=(0, 0), sticky="w")
        phone_number_display = ttk.Label(info_grid_frame, textvariable=self.phone_number_var, font=self.bold_font, foreground=self.error_color)
        phone_number_display.grid(row=1, column=1, padx=(0, 2), pady=(0, 0), sticky="w")
        
        # 竖排复制手机号按钮，上下居中显示
        vertical_text = "复\n制\n号\n码"
        self.copy_phone_btn = ttk.Button(info_grid_frame, text=vertical_text, command=self.copy_phone_number, style="Accent.TButton", width=2)
        self.copy_phone_btn.grid(row=0, column=2, rowspan=2, padx=(2, 4), pady=(2, 2), sticky=tk.NS)  # 设置pady=(2,2)使其上下居中显示
        
        # 添加分隔线 - 极致紧凑样式
        ttk.Separator(self.left_frame).pack(fill=tk.X, padx=15, pady=0)  # 分隔线内边距设为0

        # 短信发件箱区域 - 紧凑化布局，整体上移
        sms_frame = ttk.LabelFrame(self.left_frame, text="短信发件箱")
        sms_frame.pack(fill=tk.BOTH, expand=True, padx=self.ui_layout['sms_frame_padx'], pady=(0, 5))  # 保持上方内边距为0，确保整体上移效果

        # 设置grid列权重，使布局更加紧凑
        sms_frame.columnconfigure(1, weight=1)
        sms_frame.columnconfigure(2, weight=0)
        
        # 手机号码输入 - 紧凑布局
        ttk.Label(sms_frame, text="目标号码:", font=self.font).grid(row=0, column=0, padx=(8, 3), pady=(3, 5), sticky=tk.W)
        self.sms_phone_entry = ttk.Entry(sms_frame, textvariable=self.sms_phone_var, font=self.font, width=self.ui_layout['sms_entry_width'], style="Entry.TEntry")
        self.sms_phone_entry.grid(row=0, column=1, padx=(3, 8), pady=(3, 5), sticky="ew")

        # 短信内容 - 紧凑布局
        ttk.Label(sms_frame, text="短信内容:", font=self.font).grid(row=1, column=0, padx=(8, 3), pady=(0, 3), sticky=tk.NW)
        self.sms_text = scrolledtext.ScrolledText(sms_frame, font=self.font, width=self.ui_layout['sms_text_width'], height=self.ui_layout['sms_text_height'], wrap=tk.WORD, background=self.log_bg_color, foreground=self.text_color)
        self.sms_text.grid(row=1, column=1, padx=(3, 8), pady=(0, 3), sticky=tk.NSEW)
        self.sms_text.configure(borderwidth=1, relief=tk.SUNKEN)
        
        # 发送统计信息标签 - 紧凑位置
        self.count_label = ttk.Label(sms_frame, textvariable=self.sms_count_var, font=self.font, foreground=self.success_color)
        self.count_label.grid(row=2, column=0, columnspan=2, padx=(8, 0), pady=(0, 5), sticky="w")

        # 发送按钮（竖排显示）- 紧凑样式和位置
        vertical_text = "发\n送\n短\n信"
        send_btn = ttk.Button(sms_frame, text=vertical_text, command=self.send_sms, style="Accent.TButton", width=2)
        send_btn.grid(row=1, column=2, padx=(0, 8), pady=3, sticky=tk.NS)

        # 添加分隔线 - 短信发件箱和收件箱之间
        ttk.Separator(self.left_frame).pack(fill=tk.X, padx=15, pady=5)

        # 短信收件箱区域
        inbox_frame = ttk.LabelFrame(self.left_frame, text="短信收件箱")
        inbox_frame.pack(fill=tk.BOTH, expand=True, padx=self.ui_layout['sms_frame_padx'], pady=self.ui_layout['sms_frame_pady'])

        # 收件箱控制区域
        inbox_control_frame = ttk.Frame(inbox_frame)
        inbox_control_frame.pack(fill=tk.X, padx=10, pady=(5, 8))
        
        # 提取短信按钮
        refresh_inbox_btn = ttk.Button(inbox_control_frame, text="提取短信", command=self.refresh_inbox_placeholder, style="Accent.TButton")
        refresh_inbox_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空收件箱按钮
        clear_inbox_btn = ttk.Button(inbox_control_frame, text="清空收件箱", command=self.clear_inbox_content, style="Accent.TButton")
        clear_inbox_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 复制验证码按钮
        copy_code_btn = ttk.Button(inbox_control_frame, text="复制验证码", command=self.copy_verification_code, style="Accent.TButton")
        copy_code_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 收件箱消息文本框 - 缩小大小
        self.inbox_text = scrolledtext.ScrolledText(inbox_frame, font=self.font, wrap=tk.WORD, 
                                                    background=self.log_bg_color, foreground=self.text_color, 
                                                    borderwidth=1, relief=tk.SUNKEN, height=8)
        self.inbox_text.pack(fill=tk.X, padx=10, pady=(0, 5))
        # 设置文本框为只读
        self.inbox_text.config(state=tk.DISABLED)
        
        # 自动复制验证码复选框 - 放到文本框下方
        self.auto_copy_checkbox = ttk.Checkbutton(
            inbox_frame, 
            text="自动复制验证码", 
            variable=self.auto_copy_verification_var,
            command=self.on_auto_copy_toggle,
            style="TCheckbutton"
        )
        self.auto_copy_checkbox.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # 创建右侧面板(只包含日志)
        self.right_frame = ttk.Frame(self.main_frame, style="Right.TFrame")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=self.ui_layout['right_padx'], pady=self.ui_layout['right_pady'])

        # 添加右侧面板标题 - 使用主标题样式增强视觉效果
        right_title = ttk.Label(self.right_frame, text="系统监控日志", style="Title.TLabel")
        right_title.pack(pady=(10, 5))
        
        # 添加标题下划线
        right_title_separator = ttk.Separator(self.right_frame)
        right_title_separator.pack(fill=tk.X, padx=10, pady=2)

        # 合并日志区域 - 优化布局
        log_frame = ttk.LabelFrame(self.right_frame, text="系统日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        log_frame.pack_propagate(False)

        # 优化日志控制区 - 清理重复代码并优化布局
        
        # 重新创建日志过滤选项，放置在右侧面板的标题下方
        filter_container = ttk.Frame(self.right_frame, style="Main.TFrame")
        filter_container.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # 左侧过滤选项区域
        filter_options_frame = ttk.Frame(filter_container)
        filter_options_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # 日志过滤标签
        ttk.Label(filter_options_frame, text="显示日志:", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        # 优化单选按钮组的布局
        radio_frame = ttk.Frame(filter_options_frame)
        radio_frame.pack(side=tk.LEFT)
        
        # 全部日志选项
        ttk.Radiobutton(radio_frame, text="全部日志", variable=self.log_type, value="all", command=self.filter_logs, style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 12))
        
        # 短信助手日志选项
        ttk.Radiobutton(radio_frame, text="短信助手日志", variable=self.log_type, value="sms", command=self.filter_logs, style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 12))
        
        # 系统端口日志选项
        ttk.Radiobutton(radio_frame, text="系统端口日志", variable=self.log_type, value="monitor", command=self.filter_logs, style="TRadiobutton").pack(side=tk.LEFT)
        
        # 清除日志按钮（放置在筛选选项右侧）
        clear_btn = ttk.Button(filter_container, text="清除日志", command=self.clear_logs, style="Accent.TButton")
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        # 统一日志显示区域 - 优化样式
        self.log_text = scrolledtext.ScrolledText(log_frame, font=self.font, wrap=tk.WORD, background=self.log_bg_color, foreground="#000000")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 添加更好的边框和视觉效果
        self.log_text.configure(borderwidth=1, relief=tk.SUNKEN)

    def copy_phone_number(self):
        """复制当前手机号到剪贴板（只复制纯数字部分）"""
        phone_number = self.phone_number_var.get()
        if phone_number and phone_number != "未连接":
            # 提取纯数字部分（手机号码）
            pure_number_match = re.search(r'\d+', phone_number)
            if pure_number_match:
                pure_number = pure_number_match.group()
                self.root.clipboard_clear()
                self.root.clipboard_append(pure_number)
                # 输出日志信息
                self.sms_log(f"手机号码 {pure_number} 已复制到剪贴板")
    
    def copy_verification_code(self):
        """从短信内容中提取完整的连续数字或字母验证码并复制到剪贴板"""
        try:
            # 获取收件箱中的所有内容
            self.inbox_text.config(state=tk.NORMAL)
            inbox_content = self.inbox_text.get(1.0, tk.END)
            self.inbox_text.config(state=tk.DISABLED)
            
            if not inbox_content.strip():
                self.sms_log("收件箱为空，无法提取验证码")
                return
            
            # 分析短信内容，查找完整的连续数字或字母验证码
            
            # 优先查找常见的验证码格式：
            # 1. 连续的4-8位数字（最常见的验证码格式）
            code_match = re.search(r'([0-9]{4,8})', inbox_content)
            
            # 2. 如果没有找到纯数字验证码，查找包含字母和数字的验证码
            if not code_match:
                code_match = re.search(r'([A-Za-z0-9]{4,8})', inbox_content)
            
            # 3. 特定格式的验证码（例如：XX-XX-XX）
            if not code_match:
                code_match = re.search(r'([A-Za-z0-9]{2}-[A-Za-z0-9]{2}-[A-Za-z0-9]{2})', inbox_content)
            
            if code_match:
                verification_code = code_match.group(1)
                # 复制到剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(verification_code)
                self.sms_log(f"验证码 {verification_code} 已复制到剪贴板")
            else:
                self.sms_log("未在短信内容中找到验证码")
        except Exception as e:
            self.sms_log(f"提取验证码时发生错误: {str(e)}")
    
    def refresh_inbox_placeholder(self):
        """重新从系统日志中读取所有短信并更新收件箱"""
        try:
            # 首先清空当前收件箱
            self.clear_inbox_content()
            
            # 记录刷新操作
            self.sms_log("正在刷新收件箱...")
            
            # 检查是否有历史日志
            if not self.monitor_logs:
                self.sms_log("没有找到历史系统日志")
                self.sms_log("日志中无短信可提取")
                return
            
            # 遍历历史系统日志，提取所有短信信息
            sms_count = 0
            # 拼接所有系统日志
            all_monitor_logs = "\n".join(self.monitor_logs)
            
            # 查找所有包含handler_sms.smsCallback的日志片段
            callback_matches = re.finditer(r'handler_sms\.smsCallback[^\[]+', all_monitor_logs)
            
            # 处理每个匹配的短信回调
            processed_sms = []  # 用于存储已处理的短信，避免重复
            for match in callback_matches:
                callback_content = match.group()
                
                # 提取发件人号码
                phone_match = re.search(r'sender_number:\s*(\d+)', callback_content)
                phone_number = phone_match.group(1) if phone_match else "未知号码"
                
                # 提取发件时间
                time_match = re.search(r'datetime:\s*([\d/,:+\s]+)', callback_content)
                send_time = time_match.group(1).strip() if time_match else "未知时间"
                
                # 提取短信内容
                content_match = re.search(r'sms_content:\s*(.+?)(?=\[|$)', callback_content, re.DOTALL)
                if content_match:
                    raw_sms_content = content_match.group(1).strip()
                    
                    # 分割内容为行
                    lines = raw_sms_content.split('\n')
                    clean_lines = []
                    
                    # 逐行处理，移除系统日志行，但保留短信内容中的换行
                    for line in lines:
                        # 如果行以[开头且包含]，可能是系统日志行，跳过
                        if line.startswith('[') and ']' in line and ('-' in line or ':' in line):
                            continue
                        # 否则保留该行，去除首尾空格
                        clean_line = line.strip()
                        if clean_line:
                            clean_lines.append(clean_line)
                    
                    # 组合成多行文本，保留短信内容的合理换行
                    sms_content = '\n'.join(clean_lines)
                    
                    # 特别处理常见的验证码短信格式
                    if '哔哩哔哩' in sms_content and '短信登录验证码' in sms_content:
                        # 提取所有数字，组合成完整的验证码
                        numbers = ''.join(re.findall(r'\d+', sms_content))
                        if numbers:
                            # 重新格式化哔哩哔哩验证码短信
                            sms_content = f"【哔哩哔哩】{numbers}短信登录验证码，5分钟内有效，请勿泄露。"
                    
                    # 修复可能的乱码问题
                    # 方法1: 尝试替换常见的乱码组合
                    sms_content = sms_content.replace('�  ', '的')
                    # 方法2: 如果还有其他乱码，使用更智能的替换策略
                    # 使用正则表达式替换单个乱码字符为空格
                    sms_content = re.sub(r'�+', ' ', sms_content)
                else:
                    # 尝试从其他模式中提取短信内容
                    alt_content_match = re.search(r'\[(.*?)\]', callback_content)
                    if alt_content_match:
                        sms_content = alt_content_match.group(1)
                    else:
                        sms_content = "无法提取内容"
                
                # 创建唯一标识符以避免重复
                sms_identifier = f"{phone_number}_{send_time}_{sms_content[:20]}"
                if sms_identifier not in processed_sms:
                    processed_sms.append(sms_identifier)
                    # 格式化短信信息
                    formatted_sms = f"{sms_content}\n发件号码: {phone_number}\n发件时间: {send_time}\n\n"
                    # 更新收件箱UI
                    self.root.after(0, lambda sms=formatted_sms: self.update_inbox_text(sms))
                    sms_count += 1
            
            # 记录刷新结果
            if sms_count > 0:
                self.sms_log(f"成功提取 {sms_count} 条短信")
            else:
                self.sms_log("日志中无短信可提取")
                
        except Exception as e:
            self.sms_log(f"刷新收件箱时发生错误: {str(e)}")
            
    def clear_inbox_content(self):
        """清空收件箱内容"""
        try:
            self.inbox_text.config(state=tk.NORMAL)
            self.inbox_text.delete(1.0, tk.END)
            self.inbox_text.config(state=tk.DISABLED)
            self.sms_log("收件箱已清空")
        except Exception as e:
            error_msg = f"清空收件箱时发生错误: {str(e)}"
            self.log(error_msg)
            self.sms_log(error_msg)
    
    def refresh_ports(self):
        """刷新可用串口列表"""
        ports = list(serial.tools.list_ports.comports())
        port_names = [port.device for port in ports]
        
        # 同时更新两个端口下拉列表
        self.sms_port_combo['values'] = port_names
        self.monitor_port_combo['values'] = port_names
        
        # 检查是否有可用端口
        if not port_names:
            self.sms_port_var.set("")
            self.monitor_port_var.set("")
            self.log("未找到可用串口，请连接设备后重试", log_type="sms")
            # 显示提示对话框
            self.root.after(500, lambda: self.show_no_ports_error())
            return False
        
        # 尝试自动为短信助手选择AT端口
        at_ports = [port for port in ports if 'AT' in port.description]
        specific_at_ports = [port for port in at_ports if 'LUAT USB Device 1 AT' in port.description]
        
        # 尝试自动为监控工具选择Modem端口
        modem_ports = [port for port in ports if 'Modem' in port.description or 'MODEM' in port.description]
        specific_modem_ports = [port for port in modem_ports if 'LUAT USB Device 0 Modem' in port.description]
        
        # 设置短信端口
        if specific_at_ports:
            self.sms_port_var.set(specific_at_ports[0].device)
            self.log(f"已自动选择短信端口: {specific_at_ports[0].device} - {specific_at_ports[0].description}")
        elif at_ports:
            self.sms_port_var.set(at_ports[0].device)
            self.log(f"已自动选择AT端口: {at_ports[0].device} - {at_ports[0].description}")
        elif port_names:
            self.sms_port_var.set(port_names[0])
            self.log("已刷新串口列表，但未找到AT端口")
        
        # 设置系统日志端口
        if specific_modem_ports:
            self.monitor_port_var.set(specific_modem_ports[0].device)
            self.log(f"已自动选择系统日志端口: {specific_modem_ports[0].device} - {specific_modem_ports[0].description}")
        elif modem_ports:
            self.monitor_port_var.set(modem_ports[0].device)
            self.log(f"已自动选择Modem端口: {modem_ports[0].device} - {modem_ports[0].description}")
        elif port_names and len(port_names) > 1:
            # 如果有多个端口，选择第二个作为系统日志端口
            self.monitor_port_var.set(port_names[1])
            self.log(f"已自动选择系统日志端口: {port_names[1]}")
        elif port_names:
            # 如果只有一个端口，也选择它作为系统日志端口
            self.monitor_port_var.set(port_names[0])
            self.log("只有一个可用端口，将同时用于短信助手和监控工具")
        
        return True



    def sms_connect(self):
        """连接到短信助手串口"""
        try:
            port = self.sms_port_var.get()
            baudrate = int(self.sms_baudrate_var.get())

            if not port:
                messagebox.showerror("错误", "请选择短信端口")
                self.sms_status_led.config(text="●", foreground=self.error_color)
                return

            self.sms_ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=2,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )

            if self.sms_ser.is_open:
                self.sms_connected = True
                self.status_var.set(f"设备已连接成功 ({port})")
                self.log(f"短信端口已连接到串口: {port}", log_type="sms")
                # 更新状态指示灯为绿色
                self.sms_status_led.config(text="●", foreground=self.success_color)
                # 启动连接成功动画
                self.animate_connection(self.sms_status_led)
                # 测试模块响应
                response = self.sms_send_at_command('AT')
                if response and 'OK' in response:
                    self.log("短信模块响应正常", log_type="sms")
                    # 端口连接成功后自动获取手机号
                    self.log("开始自动获取SIM卡信息...", log_type="sms")
                    self.root.after(200, self.read_sim_info)  # 减少延迟，加速信息获取
                else:
                    self.log("警告: 短信模块无响应或响应异常", log_type="sms")
            else:
                messagebox.showerror("错误", "无法打开短信端口")
                self.sms_status_led.config(text="●", foreground=self.error_color)
        except Exception as e:
            messagebox.showerror("错误", f"连接短信端口时发生错误: {str(e)}")
            self.log(f"连接短信端口时发生错误: {str(e)}", log_type="sms")
            # 确保指示灯为红色
            self.sms_status_led.config(text="●", foreground=self.error_color)
        finally:
            # 检查设备连接状态
            self.check_device_connection()

    def sms_disconnect(self):
        """断开短信助手串口连接"""
        # 调用disconnect_all_ports方法断开所有端口
        self.disconnect_all_ports()



    def monitor_open_serial(self):
        try:
            # 获取串口参数
            port = self.monitor_port_var.get()
            baudrate = int(self.monitor_baudrate_var.get())
            databits = int(self.monitor_databits_var.get())
            
            # 转换停止位
            stopbits_value = self.monitor_stopbits_var.get()
            if stopbits_value == '1':
                stopbits = serial.STOPBITS_ONE
            elif stopbits_value == '1.5':
                stopbits = serial.STOPBITS_ONE_POINT_FIVE
            else:
                stopbits = serial.STOPBITS_TWO
            
            # 转换校验位
            parity_value = self.monitor_parity_var.get()
            if parity_value == 'N':
                parity = serial.PARITY_NONE
            elif parity_value == 'E':
                parity = serial.PARITY_EVEN
            elif parity_value == 'O':
                parity = serial.PARITY_ODD
            elif parity_value == 'M':
                parity = serial.PARITY_MARK
            else:
                parity = serial.PARITY_SPACE
            
            # 打开串口
            self.monitor_ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=databits,
                parity=parity,
                stopbits=stopbits,
                timeout=0.1
            )
            
            if self.monitor_ser.is_open:
                self.status_var.set(f"系统日志端口已连接到 {port}")
                self.log(f"系统日志端口已连接到 {port} ({baudrate},{databits},{parity_value},{stopbits_value})")
                
                # 更新状态指示灯为绿色
                self.monitor_status_led.config(text="●", foreground=self.success_color)
                # 启动连接成功动画
                self.animate_connection(self.monitor_status_led)
                
                # 禁用串口设置
                self.monitor_port_combo.config(state="disabled")
                self.monitor_baudrate_combo.config(state="disabled")
                self.monitor_databits_combo.config(state="disabled")
                self.monitor_stopbits_combo.config(state="disabled")
                self.monitor_parity_combo.config(state="disabled")
                
                # 启动接收线程
                self.monitor_running = True
                self.monitor_connected = True  # 设置连接状态标志
                self.monitor_thread = threading.Thread(target=self.monitor_receive_data)
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
        except Exception as e:
            self.status_var.set(f"打开系统日志端口失败: {str(e)}")
            self.log(f"打开系统日志端口失败: {str(e)}")
            messagebox.showerror("错误", f"打开系统日志端口失败:\n{str(e)}")
        finally:
            # 检查设备连接状态
            self.check_device_connection()

    def monitor_close_serial(self):
        try:
            # 停止接收线程
            self.monitor_running = False
            time.sleep(0.2)  # 等待线程结束
            
            if self.monitor_ser is not None and self.monitor_ser.is_open:
                self.monitor_ser.close()
                self.monitor_ser = None
            
            # 更新连接状态标志
            self.monitor_connected = False
            
            # 更新UI
            self.status_var.set("系统日志端口已关闭")
            self.log("系统日志端口已关闭")
            
            # 更新状态指示灯为红色
            self.monitor_status_led.config(text="●", foreground=self.error_color)
            
            # 启用串口设置
            self.monitor_port_combo.config(state="readonly")
            self.monitor_baudrate_combo.config(state="readonly")
            self.monitor_databits_combo.config(state="readonly")
            self.monitor_stopbits_combo.config(state="readonly")
            self.monitor_parity_combo.config(state="readonly")
        except Exception as e:
            self.status_var.set(f"关闭系统日志端口失败: {str(e)}")
            self.log(f"关闭系统日志端口失败: {str(e)}")
        finally:
            # 检查设备连接状态
            self.check_device_connection()

    # 监控工具数据接收线程
    def monitor_receive_data(self):
        while self.monitor_running:
            try:
                if self.monitor_ser is not None and self.monitor_ser.is_open:
                    # 读取串口数据
                    data = self.monitor_ser.read(1024)
                    if data:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        # 只记录接收数据的字节数信息，不添加额外换行符
                        self.log(f"接收到数据: {len(data)} 字节", log_type="monitor")

                        # 尝试解码数据
                        try:
                            text = data.decode('utf-8', errors='replace')
                            self.log(f"使用UTF-8解码成功", log_type="monitor")
                        except:
                            # 如果utf-8解码失败，尝试其他编码
                            try:
                                text = data.decode('gbk', errors='replace')
                                self.log(f"使用GBK解码成功", log_type="monitor")
                            except:
                                # 如果都失败，显示十六进制
                                text = ''.join([f"{b:02X} " for b in data])
                                self.log(f"解码失败，显示十六进制", log_type="monitor")

                        # 清理文本，去除多余空行和特殊字符
                        cleaned_text = self._clean_log_text(text)
                        
                        # 在日志中显示清理后的数据，不添加额外换行符
                        if cleaned_text:
                            self.log(cleaned_text, log_type="monitor")
                          
                        # 检查是否包含handler_sms.smsCallback，并提取短信信息
                        if 'handler_sms.smsCallback' in text:
                            self.process_sms_callback(text, timestamp)
            except Exception as e:
                if self.monitor_running:  # 只有在线程运行时才显示错误
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    error_msg = f"[{timestamp}] 接收数据错误: {str(e)}"
                    self.log(f"\n{error_msg}\n", log_type="monitor")
                    self.status_var.set(error_msg)
                    # 发生错误时关闭串口
                    self.root.after(10, self.monitor_close_serial)
                break

            time.sleep(0.01)  # 短暂休眠，降低CPU使用率
            
    def _clean_log_text(self, text):
        """清理日志文本，去除多余空行和特殊字符"""
        # 替换Windows换行符为Unix换行符
        text = text.replace('\r\n', '\n')
        # 去除连续的多个换行符
        text = re.sub(r'\n{2,}', '\n', text)
        # 去除行首行尾的空白字符
        lines = [line.strip() for line in text.split('\n')]
        # 移除空行
        lines = [line for line in lines if line]
        # 重新组合文本，每行前不加时间戳（由log方法统一处理）
        return '\n'.join(lines)

    def process_sms_callback(self, text, timestamp):
        """处理handler_sms.smsCallback消息，提取短信信息并添加到收件箱"""
        try:
            
            # 从系统日志中提取短信信息
            # 寻找handler_sms.smsCallback后的发件人号码、时间和内容
            callback_pos = text.find('handler_sms.smsCallback')
            if callback_pos != -1:
                # 截取callback后的内容进行分析
                callback_content = text[callback_pos:]
                
                # 提取发件人号码（格式：sender_number: 106814308000003154）
                phone_match = re.search(r'sender_number:\s*(\d+)', callback_content)
                phone_number = phone_match.group(1) if phone_match else "未知号码"
                
                # 提取发件时间（格式：datetime: 25/09/30,17:31:01+32）
                time_match = re.search(r'datetime:\s*([\d/,:+\s]+)', callback_content)
                send_time = time_match.group(1).strip() if time_match else timestamp
                
                # 提取短信内容，优化提取逻辑以处理验证码被分割的情况
                content_match = re.search(r'sms_content:\s*(.+?)(?=\[|$)', callback_content, re.DOTALL)
                if content_match:
                    raw_sms_content = content_match.group(1).strip()
                    
                    # 移除所有可能的换行符、制表符等空白字符，但保留空格
                    processed_content = re.sub(r'[\n\r\t]+', '', raw_sms_content)
                    
                    # 处理哔哩哔哩验证码短信的特殊情况
                    if '哔哩哔哩' in processed_content and '短信登录验证码' in processed_content:
                        # 使用更精确的正则表达式提取6位数字验证码
                        # 优先查找短信中明显的6位数字序列
                        code_match = re.search(r'([0-9]{6})', processed_content)
                        if code_match:
                            verification_code = code_match.group(1)
                            sms_content = "【哔哩哔哩】" + verification_code + "短信登录验证码，5分钟内有效，请勿泄露。"
                        else:
                            # 如果没有找到明显的6位数字，回退到原始内容
                            sms_content = processed_content
                    else:
                        # 对于其他短信，直接使用处理后的内容
                        sms_content = processed_content
                    
                    # 修复可能的乱码问题
                    # 方法1: 尝试替换常见的乱码组合
                    sms_content = sms_content.replace('�  ', '的')
                    # 方法2: 使用正则表达式替换单个乱码字符为空格
                    sms_content = re.sub(r'�+', ' ', sms_content)
                    # 方法3: 对内容进行进一步清理，保留中文和常用字符
                    sms_content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：,.!?;:\-\s]', '', sms_content)
                else:
                    sms_content = "无法提取内容"
                
                # 只显示短信内容，不显示发件人和发件时间
                # 但保留这些信息在内部变量中以便其他功能使用
                self.latest_sms_info = {
                    'content': sms_content,
                    'phone_number': phone_number,
                    'send_time': send_time
                }
                
                # 更新收件箱UI（在主线程中执行）
                self.root.after(0, lambda: self.update_inbox_text(f"{sms_content}\n\n"))
        except Exception as e:
            self.log(f"处理短信回调时发生错误: {str(e)}", log_type="monitor")
            
    def update_inbox_text(self, sms_content):
        """更新收件箱文本框内容"""
        try:
            self.inbox_text.config(state=tk.NORMAL)
            self.inbox_text.insert(tk.END, sms_content)
            self.inbox_text.see(tk.END)  # 滚动到最新内容
            self.inbox_text.config(state=tk.DISABLED)
            
            # 检查是否启用了自动复制验证码功能
            if self.auto_copy_verification_var.get():
                # 调用自动复制验证码方法
                self._auto_copy_verification_code(sms_content)
        except Exception as e:
            self.log(f"更新收件箱时发生错误: {str(e)}")
            
    def on_auto_copy_toggle(self):
        """处理自动复制验证码复选框的状态变化"""
        if self.auto_copy_verification_var.get():
            self.sms_log("已启用自动复制验证码功能")
        else:
            self.sms_log("已禁用自动复制验证码功能")
    
    def _auto_copy_verification_code(self, sms_content):
        """自动从短信内容中提取验证码并复制到剪贴板"""
        try:
            
            # 优先查找常见的验证码格式：
            # 1. 连续的4-8位数字（最常见的验证码格式）
            code_match = re.search(r'([0-9]{4,8})', sms_content)
            
            # 2. 如果没有找到纯数字验证码，查找包含字母和数字的验证码
            if not code_match:
                code_match = re.search(r'([A-Za-z0-9]{4,8})', sms_content)
            
            # 3. 特定格式的验证码（例如：XX-XX-XX）
            if not code_match:
                code_match = re.search(r'([A-Za-z0-9]{2}-[A-Za-z0-9]{2}-[A-Za-z0-9]{2})', sms_content)
            
            if code_match:
                verification_code = code_match.group(1)
                # 复制到剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(verification_code)
                self.sms_log(f"已自动复制验证码 {verification_code} 到剪贴板")
        except Exception as e:
            self.sms_log(f"自动复制验证码时发生错误: {str(e)}")
    
    # 通用函数
    def check_device_connection(self):
        """检查设备是否完全连接成功"""
        # 检查是否存在LUAT USB Device端口
        is_air724ug = self.is_air724ug_device()
        
        # 更新设备名称显示
        if is_air724ug:
            self.device_display_var.set("Air724ug")
        else:
            self.device_display_var.set("未知设备")
            
        # 更新状态文本
        if self.sms_connected and self.monitor_connected:
            self.status_var.set("所有端口已连接")
        elif self.sms_connected:
            self.status_var.set("短信端口已连接")
        elif self.monitor_connected:
            self.status_var.set("系统日志端口已连接")
        else:
            self.status_var.set("就绪")
            # 当两个端口都未连接时，输出提示日志
            if hasattr(self, '_device_disconnected_logged') and not self._device_disconnected_logged:
                self.log("设备已断开，请插入设备后点击连接设备")
                self._device_disconnected_logged = True
            # 如果设备重新连接后又断开，重置标志以再次显示提示
            elif self.sms_connected or self.monitor_connected:
                self._device_disconnected_logged = False
    
    def is_air724ug_device(self):
        """检查是否为Air724ug设备，通过检测是否存在LUAT USB Device端口"""
        try:
            ports = list(serial.tools.list_ports.comports())
            # 检查是否有端口描述中包含"LUAT USB Device"字样
            for port in ports:
                if port.description and "LUAT USB Device" in port.description:
                    return True
            return False
        except Exception as e:
            self.log(f"检测设备类型时发生错误: {str(e)}")
            return False
    
    def start_port_monitoring(self):
        """启动定期检查端口存在性的监控"""
        # 定期执行端口检查（每2秒检查一次）
        self.port_monitoring_interval = 2000  # 毫秒
        self.check_ports_existence()
        
    def check_ports_existence(self):
        """检查当前连接的端口是否仍然存在于系统中"""
        try:
            # 获取当前系统中的所有端口
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            
            # 需要断开连接的标志
            need_disconnect = False
            
            # 检查短信端口是否仍然存在
            if self.sms_connected and hasattr(self, 'sms_port_var'):
                current_sms_port = self.sms_port_var.get()
                if current_sms_port and current_sms_port not in available_ports:
                    need_disconnect = True
                    self.log(f"检测到短信端口 {current_sms_port} 已不存在")
            
            # 检查监控端口是否仍然存在
            if self.monitor_connected and hasattr(self, 'monitor_port_var'):
                current_monitor_port = self.monitor_port_var.get()
                if current_monitor_port and current_monitor_port not in available_ports:
                    need_disconnect = True
                    self.log(f"检测到系统日志端口 {current_monitor_port} 已不存在")
            
            # 如果任一已连接端口不存在，断开所有连接
            if need_disconnect:
                self.log("设备已断开连接，正在更新状态...")
                self.disconnect_all_ports()
                # 设置标志以确保会显示断开连接的提示
                self._device_disconnected_logged = False
            
            # 继续定期检查
            self.root.after(self.port_monitoring_interval, self.check_ports_existence)
            
        except Exception as e:
            self.log(f"检查端口存在性时发生错误: {str(e)}")
            # 即使发生错误，也要继续定期检查
            self.root.after(self.port_monitoring_interval, self.check_ports_existence)


    def auto_connect_all_ports(self):
        """自动连接所有端口"""
        self.log("正在尝试自动连接所有端口...")
        
        # 注意：初始化时已经刷新过端口列表，这里不再重复刷新
        # 避免日志中出现重复的端口选择信息

        # 先连接短信助手端口
        if not self.sms_connected:
            self.log("正在连接短信助手端口...")
            self.sms_connect()
        else:
            self.log("短信助手端口已连接")

        # 减少连接监控端口的延迟，提高连接速度
        self.root.after(100, self.auto_connect_monitor_port)

    def animate_connection(self, led):
        """连接成功后的动画效果 - 简化版"""
        # 简化动画，直接设置为成功颜色，提高响应速度
        led.config(foreground=self.success_color)
        self.root.update()

    def auto_connect_monitor_port(self):
        """自动连接系统日志端口"""
        if not self.monitor_connected:
            self.log("正在连接系统日志端口...")
            self.monitor_open_serial()
        else:
            self.log("系统日志端口已连接")

    def disconnect_all_ports(self):
        """断开所有端口连接"""
        self.log("正在断开所有端口连接...")
        
        # 断开短信端口（直接实现，避免递归调用sms_disconnect）
        if self.sms_connected:
            self.log("正在断开短信端口...")
            if self.sms_ser and self.sms_ser.is_open:
                self.sms_ser.close()
                self.sms_connected = False
                self.log("短信端口已断开串口连接", log_type="sms")
                # 更新状态指示灯为红色
                self.sms_status_led.config(text="●", foreground=self.error_color)
                # 清空手机号码显示
                self.root.after(0, lambda: self.phone_number_var.set("未连接"))
        else:
            self.log("短信端口未连接")

        # 断开系统日志端口 - 改进版：增加线程终止可靠性和缓冲区清理
        if self.monitor_connected:
            self.log("正在断开系统日志端口...")
            try:
                # 先停止接收线程
                self.monitor_running = False
                
                # 记录开始等待的时间
                start_time = time.time()
                # 设置最长等待时间为0.5秒
                max_wait_time = 0.5
                
                # 等待线程结束，但不超过最长等待时间
                # 使用括号处理多行条件
                while (hasattr(self, 'monitor_thread') and 
                       self.monitor_thread.is_alive() and 
                       (time.time() - start_time < max_wait_time)):
                    time.sleep(0.05)  # 短暂休眠，减少CPU使用率
                
                # 强制关闭串口，确保断开连接
                if self.monitor_ser is not None:
                    # 清除输入缓冲区，防止关闭前读取到残留数据
                    if self.monitor_ser.is_open:
                        try:
                            self.monitor_ser.flushInput()  # 清空输入缓冲区
                            self.monitor_ser.flushOutput()  # 清空输出缓冲区
                        except:
                            pass  # 忽略缓冲区清理错误
                        
                        # 关闭串口
                        self.monitor_ser.close()
                    
                    self.monitor_ser = None  # 完全释放串口对象引用
                
                # 更新连接状态标志
                self.monitor_connected = False
                self.log("系统日志端口已关闭")
                
                # 更新状态指示灯为红色
                self.monitor_status_led.config(text="●", foreground=self.error_color)
                
                # 启用串口设置
                self.monitor_port_combo.config(state="readonly")
                self.monitor_baudrate_combo.config(state="readonly")
                self.monitor_databits_combo.config(state="readonly")
                self.monitor_stopbits_combo.config(state="readonly")
                self.monitor_parity_combo.config(state="readonly")
            except Exception as e:
                self.log(f"关闭系统日志端口失败: {str(e)}")
        else:
            self.log("系统日志端口未连接")
        
        # 在所有端口断开后，统一更新状态文本
        if not self.sms_connected and not self.monitor_connected:
            self.status_var.set("短信端口及系统日志端口已断开连接")
        elif not self.sms_connected:
            self.status_var.set("短信端口已断开连接")
        elif not self.monitor_connected:
            self.status_var.set("系统日志端口已断开连接")
        
        self.log("所有端口已断开连接")

    def sms_send_at_command(self, command, wait_time=0.3):
        """发送AT指令并返回响应"""
        if not self.sms_ser or not self.sms_ser.is_open:
            self.log("错误: 短信端口未连接。", log_type="sms")
            return None

        try:
            # 确保命令以\r\n结尾
            if not command.endswith('\r\n'):
                if command.endswith('\r'):
                    command += '\n'
                else:
                    command += '\r\n'

            # 发送命令
            self.sms_ser.write(command.encode('utf-8'))
            
            # 优化等待机制
            max_wait = wait_time * 2  # 最大等待时间为设置值的2倍
            start_time = time.time()
            response = b''
            
            while time.time() - start_time < max_wait:
                if self.sms_ser.in_waiting:
                    response += self.sms_ser.read(self.sms_ser.in_waiting)
                    # 如果已经收到OK或ERROR，可能是命令执行完成
                    if b'OK' in response or b'ERROR' in response or b'>' in response:
                        break
                time.sleep(0.05)  # 缩短检查间隔

            return response.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            self.log(f"发送AT指令时发生错误: {str(e)}", log_type="sms")
            return None

    def log(self, message, log_type="all"):
        """添加日志信息"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # 根据日志类型添加标签
        if log_type == "sms":
            formatted_message = f"[{timestamp}] [短信助手] {message}\n"
            self.sms_logs.append(formatted_message)
        elif log_type == "monitor":
            formatted_message = f"[{timestamp}] [系统端口] {message}\n"
            self.monitor_logs.append(formatted_message)
        
        # 添加到全部日志
        self.all_logs.append(formatted_message)
        
        # 只有当当前选择的日志类型匹配时才显示
        if self.log_type.get() == "all" or self.log_type.get() == log_type:
            self.log_text.insert(tk.END, formatted_message)
            self.log_text.see(tk.END)

    def sms_log(self, message):
        """添加短信日志信息"""
        self.log(message, log_type="sms")
        # 高亮显示短信日志
        last_line = self.log_text.index("end-2l")
        self.log_text.tag_add("sms_log", last_line, "end-1l")
        self.log_text.tag_config("sms_log", foreground=self.error_color)

    def filter_logs(self):
        """根据选择的日志类型过滤显示日志"""
        # 清空当前显示
        self.log_text.delete(1.0, tk.END)
        
        # 根据选择的日志类型显示对应的日志
        selected_type = self.log_type.get()
        if selected_type == "all":
            for log in self.all_logs:
                self.log_text.insert(tk.END, log)
        elif selected_type == "sms":
            for log in self.sms_logs:
                self.log_text.insert(tk.END, log)
        elif selected_type == "monitor":
            for log in self.monitor_logs:
                self.log_text.insert(tk.END, log)
        
        # 滚动到底部
        self.log_text.see(tk.END)

    def clear_logs(self):
        """清除所有日志"""
        self.log_text.delete(1.0, tk.END)
        self.all_logs = []
        self.sms_logs = []
        self.monitor_logs = []
        self.log("日志已清除")

    def read_sim_info(self):
        """读取SIM卡信息"""
        if not self.sms_connected:
            messagebox.showerror("错误", "请先连接短信端口")
            return

        # 在新线程中执行，避免界面卡死
        threading.Thread(target=self._read_sim_info_thread).start()

    def _read_sim_info_thread(self):
        """读取SIM卡信息的线程函数"""
        self.log("开始读取SIM卡信息...", log_type="sms")

        # 检查SIM卡是否就绪
        response = self.sms_send_at_command('AT+CPIN?')
        if response and '+CPIN: READY' not in response:
            self.log("SIM卡未就绪或未插入", log_type="sms")
            self.root.after(0, lambda: messagebox.showerror("错误", "SIM卡未就绪或未插入"))
            return

        # 关闭回显
        self.sms_send_at_command('ATE0')

        # 获取手机号码
        self.log("正在获取手机号码...", log_type="sms")
        phone_number = self.get_sim_phone_number()

        # 获取运营商信息
        self.log("正在获取运营商信息...", log_type="sms")
        carrier = self.get_carrier(phone_number)

        # 更新UI，在手机号码后显示运营商信息
        display_text = phone_number if phone_number else "无法获取"
        if display_text != "无法获取" and display_text != "未连接" and carrier and carrier != "未知运营商":
            display_text = f"{display_text} ({carrier})"
        self.root.after(0, lambda: self.phone_number_var.set(display_text))
        self.root.after(0, lambda: self.carrier_var.set(carrier))

        # 检查设备连接状态
        self.root.after(0, self.check_device_connection)

        self.log("SIM卡信息读取完成", log_type="sms")

    def get_sim_phone_number(self):
        """获取SIM卡手机号码"""
        # 常用的获取手机号码的AT指令
        commands = [
            'AT+CNUM',      # 多数模块支持
            'AT+CCID',      # 获取ICCID，可以用来查询号码
            'AT+CSQ',       # 查询信号强度，先确认网络状态
            'AT^HFSN',      # 某些模块的指令
            'AT+CPIN?'      # 检查SIM卡是否就绪
        ]

        # 查询手机号码
        phone_number = None
        for cmd in commands:
            response = self.sms_send_at_command(cmd)
            if response:
                self.log(f"{cmd} 响应: {response}", log_type="sms")
                # 尝试从响应中提取手机号码
                if cmd == 'AT+CNUM':
                    # 匹配实际响应格式: +CNUM: "","+8613355265083",145
                    match = re.search(r'\+CNUM: ".*?",\s*"(\+?\d+)"', response)
                    if match:
                        phone_number = match.group(1).lstrip('+86')
                        break
                elif cmd == 'AT+CCID':
                    # 保存ICCID，后面可以用来查询运营商
                    pass

        if not phone_number:
            # 如果直接获取失败，尝试其他方法
            self.log("无法直接获取手机号码，可能需要通过其他方式查询", log_type="sms")
            # 有些模块需要通过AT+CSCA命令获取短信中心号码来推断
            response = self.sms_send_at_command('AT+CSCA?')
            if response:
                self.log(f"短信中心号码: {response}", log_type="sms")

        return phone_number

    def get_carrier(self, phone_number=None):
        """根据手机号码前缀判断运营商"""
        if not phone_number:
            # 如果没有手机号码，尝试通过网络信息判断
            response = self.sms_send_at_command('AT+COPS?')
            if response:
                self.log(f"运营商信息: {response}", log_type="sms")
                # 尝试从COPS响应中提取运营商名称
                match = re.search(r'\+COPS: \d+,\d+,"(.*?)"', response)
                if match:
                    carrier = match.group(1)
                    if 'China Mobile' in carrier or '中国移动' in carrier:
                        return '中国移动'
                    elif 'China Unicom' in carrier or '中国联通' in carrier:
                        return '中国联通'
                    elif 'China Telecom' in carrier or '中国电信' in carrier:
                        return '中国电信'
                    else:
                        return carrier
        else:
            # 去掉可能的+86前缀
            if phone_number.startswith('+86'):
                phone_number = phone_number[3:]
            # 检查号码前缀
            for carrier, prefixes in self.carrier_prefixes.items():
                for prefix in prefixes:
                    if phone_number.startswith(prefix):
                        return carrier

        return "未知运营商"
    


    def send_sms(self):
        """发送短信"""
        if not self.sms_connected:
            messagebox.showerror("错误", "请先连接短信端口")
            return

        phone_number = self.sms_phone_var.get()
        message = self.sms_text.get(1.0, tk.END).strip()

        # 验证输入
        if not phone_number:
            messagebox.showerror("错误", "请输入目标手机号码")
            return

        if not re.match(r'^1[3-9]\d{9}$', phone_number):
            if not messagebox.askyesno("警告", "手机号码格式可能不正确，是否继续发送?"):
                return

        if not message:
            messagebox.showerror("错误", "请输入短信内容")
            return

        # 在新线程中执行，避免界面卡死
        threading.Thread(target=self._send_sms_thread, args=(phone_number, message)).start()

    def _send_sms_thread(self, phone_number, message):
        """发送短信的线程函数"""
        self.sms_log(f"开始发送短信到: {phone_number}")
        self.sms_log(f"短信内容: {message}")

        # 增加发送计数
        self.sms_sent_count += 1

        try:
            # 准备短信设置
            self.sms_log("准备短信设置...")

            # 设置短信中心号码 (根据实际情况修改)
            sms_center = "8613800200500"  # 默认短信中心号码，可能需要根据地区修改
            ucs2_sms_center = self.convert_to_ucs2(sms_center)
            response = self.sms_send_at_command(f'AT+CSCA="{ucs2_sms_center}"', wait_time=0.5)
            self.sms_log(f"设置短信中心响应: {response}")

            # 检查SIM卡就绪状态 (快速检查，降低等待时间)
            response = self.sms_send_at_command('AT+CPIN?', wait_time=0.3)
            if response and '+CPIN: READY' not in response:
                self.sms_log("SIM卡未就绪")
                self.root.after(0, lambda: messagebox.showerror("错误", "SIM卡未就绪"))
                return

            # 设置短信模式为文本模式
            response = self.sms_send_at_command('AT+CMGF=1', wait_time=0.3)
            self.sms_log(f"设置短信模式响应: {response}")

            # 设置短信参数，适用于UCS2编码
            response = self.sms_send_at_command('AT+CSMP=17,167,0,8', wait_time=0.3)
            self.sms_log(f"设置短信参数响应: {response}")

            # 设置字符编码为UCS2
            response = self.sms_send_at_command('AT+CSCS="UCS2"', wait_time=0.3)
            self.sms_log(f"设置字符编码响应: {response}")
            if response and 'OK' not in response:
                self.sms_log("设置字符编码失败")
                # 不强制返回，尝试继续发送

            # 确认当前字符编码设置
            response = self.sms_send_at_command('AT+CSCS?', wait_time=0.3)
            self.sms_log(f"当前字符编码: {response}")

            # 检查网络注册状态
            response = self.sms_send_at_command('AT+CREG?')
            self.sms_log(f"网络注册响应: {response}")  # 记录原始响应以便调试
            
            # 改进的网络注册检查逻辑，接受更多注册状态
            registration_state = None
            if response:
                match = re.search(r'\+CREG: \d+,(\d)', response)
                if match:
                    registration_state = int(match.group(1))
                    
            if registration_state in [0, 3, 4]:
                self.sms_log(f"网络未注册或注册状态异常: {registration_state}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"网络未注册或注册状态异常: {registration_state}，请检查信号"))
                return
            elif registration_state is None:
                self.sms_log("无法确定网络注册状态")
                # 不强制返回，尝试继续发送
            else:
                self.sms_log(f"网络注册状态正常: {registration_state}")

            # 转换手机号码和消息为UCS2编码
            try:
                self.sms_log(f"原始短信内容: {message}")
                ucs2_phone = self.convert_to_ucs2(phone_number)
                ucs2_message = self.convert_to_ucs2(message)
                self.sms_log(f"UCS2编码后手机号: {ucs2_phone}")
                self.sms_log(f"UCS2编码后消息: {ucs2_message}")
            except Exception as e:
                self.sms_log(f"编码转换失败: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"编码转换失败: {str(e)}"))
                return

            # 发送短信
            self.sms_log("发送短信...")
            response = self.sms_send_at_command(f'AT+CMGS="{ucs2_phone}"')
            if response and '>' in response:
                # 发送消息内容并结束
                response = self.sms_send_at_command(ucs2_message + '\x1a', wait_time=3)
                if response and 'OK' in response:
                    self.sms_log("短信发送成功")
                    self.sms_success_count += 1
                    self.root.after(0, lambda: messagebox.showinfo("成功", "短信发送成功"))
                else:
                    self.sms_log(f"短信发送失败: {response}")
                    self.root.after(0, lambda: messagebox.showerror("错误", f"短信发送失败: {response}"))
            else:
                self.sms_log(f"无法发送短信: {response}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"无法发送短信: {response}"))

        except Exception as e:
            self.sms_log(f"发送短信时发生错误: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"发送短信时发生错误: {str(e)}"))
        finally:
            # 更新发送统计
            self.root.after(0, lambda: self.sms_count_var.set(f"发送统计: 共发送 {self.sms_sent_count} 条，成功 {self.sms_success_count} 条"))

    def convert_to_ucs2(self, text):
        """将文本转换为UCS2编码"""
        # 先转换为UTF-16 Big Endian
        utf16_bytes = text.encode('utf-16be')
        # 转换为十六进制字符串
        ucs2_hex = utf16_bytes.hex().upper()
        return ucs2_hex

    def show_no_ports_error(self):
        """显示无可用端口错误提示"""
        messagebox.showwarning("设备未连接", "未检测到任何可用串口，请连接设备后点击刷新按钮重试。")
        
    def on_closing(self):
        # 关闭所有串口和窗口
        self.sms_disconnect()
        self.monitor_close_serial()
        self.root.destroy()

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedAir724UGTool(root)
    # 设置窗口关闭事件处理
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
