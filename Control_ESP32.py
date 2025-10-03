# esp32_client.py
import requests
import json
import time
from typing import Dict, Any, Optional

class ESP32Controller:
    """
    ESP32 Web服务器客户端控制类
    """
    
    def __init__(self, base_url: str, timeout: int = 5):
        """
        初始化ESP32控制器
        
        Args:
            base_url: ESP32的IP地址，例如 "http://192.168.0.104"
            timeout: 请求超时时间（秒）
        """
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'http://' + base_url
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _send_request(self, endpoint: str) -> Dict[str, Any]:
        """发送HTTP请求到ESP32"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": True, "message": f"请求失败: {e}"}
        except json.JSONDecodeError as e:
            return {"error": True, "message": f"JSON解析失败: {e}"}
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        return self._send_request("/api/device/info")
    
    def led_control(self, action: str) -> Dict[str, Any]:
        """
        控制LED
        
        Args:
            action: 'on', 'off', 'toggle'
        """
        valid_actions = ['on', 'off', 'toggle']
        if action not in valid_actions:
            return {"error": True, "message": f"无效的操作，请使用: {valid_actions}"}
        return self._send_request(f"/api/led/{action}")
    
    def relay_control(self, action: str) -> Dict[str, Any]:
        """
        控制继电器
        
        Args:
            action: 'on', 'off'
        """
        valid_actions = ['on', 'off']
        if action not in valid_actions:
            return {"error": True, "message": f"无效的操作，请使用: {valid_actions}"}
        return self._send_request(f"/api/relay/{action}")
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """获取传感器数据"""
        return self._send_request("/api/sensor/data")
    
    def get_status(self) -> Dict[str, Any]:
        """获取完整状态（设备信息 + 传感器数据）"""
        device_info = self.get_device_info()
        sensor_data = self.get_sensor_data()
        
        if "error" in device_info or "error" in sensor_data:
            return {"error": True, "message": "获取状态失败"}
        
        return {
            "device_info": device_info,
            "sensor_data": sensor_data
        }

def print_response(response: Dict[str, Any], title: str = ""):
    """美化打印响应结果"""
    if title:
        print(f"\n{'='*50}")
        print(f"📋 {title}")
        print(f"{'='*50}")
    
    if "error" in response and response["error"]:
        print(f"❌ 错误: {response.get('message', '未知错误')}")
    else:
        print(json.dumps(response, indent=2, ensure_ascii=False))

def demo_automated_test(controller: ESP32Controller):
    """自动化演示测试"""
    print("🚀 开始自动化演示测试")
    
    # 1. 获取设备信息
    print_response(controller.get_device_info(), "设备信息")
    time.sleep(1)
    
    # 2. LED控制演示
    print_response(controller.led_control("on"), "打开LED")
    time.sleep(1)
    
    print_response(controller.led_control("off"), "关闭LED")
    time.sleep(1)
    
    print_response(controller.led_control("toggle"), "切换LED")
    time.sleep(1)
    
    # 3. 继电器控制演示
    print_response(controller.relay_control("on"), "打开继电器")
    time.sleep(1)
    
    print_response(controller.relay_control("off"), "关闭继电器")
    time.sleep(1)
    
    # 4. 传感器数据读取
    print_response(controller.get_sensor_data(), "传感器数据")
    time.sleep(1)
    
    # 5. 最终状态
    print_response(controller.get_status(), "完整状态")
    
    print("\n✅ 自动化测试完成!")

def interactive_control(controller: ESP32Controller):
    """交互式控制界面"""
    commands = {
        "1": {"name": "📊 获取设备信息", "func": controller.get_device_info},
        "2": {"name": "💡 LED控制", "submenu": {
            "1": {"name": "打开LED", "func": lambda: controller.led_control("on")},
            "2": {"name": "关闭LED", "func": lambda: controller.led_control("off")},
            "3": {"name": "切换LED", "func": lambda: controller.led_control("toggle")}
        }},
        "3": {"name": "🔌 继电器控制", "submenu": {
            "1": {"name": "打开继电器", "func": lambda: controller.relay_control("on")},
            "2": {"name": "关闭继电器", "func": lambda: controller.relay_control("off")}
        }},
        "4": {"name": "📈 读取传感器数据", "func": controller.get_sensor_data},
        "5": {"name": "🔄 获取完整状态", "func": controller.get_status},
        "6": {"name": "🎬 自动化演示测试", "func": lambda: demo_automated_test(controller)},
        "0": {"name": "❌ 退出程序", "func": None}
    }
    
    while True:
        print("\n" + "="*60)
        print("🎛️  ESP32 智能控制器")
        print("="*60)
        
        # 显示主菜单
        for key, value in commands.items():
            print(f"{key}. {value['name']}")
        
        try:
            choice = input("\n请输入选项编号: ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice in commands:
                if "submenu" in commands[choice]:
                    # 显示子菜单
                    submenu = commands[choice]["submenu"]
                    print(f"\n--- {commands[choice]['name']} ---")
                    for sub_key, sub_value in submenu.items():
                        print(f"  {sub_key}. {sub_value['name']}")
                    
                    sub_choice = input("请选择操作: ").strip()
                    if sub_choice in submenu:
                        result = submenu[sub_choice]["func"]()
                        print_response(result, submenu[sub_choice]["name"])
                    else:
                        print("❌ 无效的选择")
                else:
                    # 执行直接功能
                    result = commands[choice]["func"]()
                    if choice != "6":  # 自动化测试自己会打印结果
                        print_response(result, commands[choice]["name"])
            else:
                print("❌ 无效的选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

def monitor_sensor_data(controller: ESP32Controller, interval: int = 2):
    """实时监控传感器数据"""
    print(f"\n📊 开始实时监控传感器数据 (每{interval}秒更新)")
    print("按 Ctrl+C 停止监控")
    
    try:
        while True:
            sensor_data = controller.get_sensor_data()
            if "error" not in sensor_data:
                print(f"\r🕒 {time.strftime('%H:%M:%S')} - " +
                      f"模拟值: {sensor_data.get('analog_value', 'N/A'):4d} | " +
                      f"电压: {sensor_data.get('voltage', 0):.2f}V | " +
                      f"按钮: {'按下' if sensor_data.get('button_pressed') else '释放':3s} | " +
                      f"LED: {'开启' if sensor_data.get('led_state') else '关闭':3s} | " +
                      f"继电器: {'开启' if sensor_data.get('relay_state') else '关闭':3s}", 
                      end="", flush=True)
            else:
                print(f"\r❌ 读取失败: {sensor_data.get('message', '未知错误')}", end="")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")

def main():
    """主函数"""
    print("🌐 ESP32 Web客户端控制器")
    print("="*50)
    
    # 配置ESP32的IP地址
    esp32_ip = input("请输入ESP32的IP地址 (例如: 192.168.1.100): ").strip()
    
    if not esp32_ip:
        print("❌ IP地址不能为空")
        return
    
    # 创建控制器实例
    controller = ESP32Controller(esp32_ip)
    
    # 测试连接
    print("\n🔗 测试连接中...")
    try:
        info = controller.get_device_info()
        if "error" not in info:
            print("✅ 连接成功!")
            print(f"📱 设备: {info.get('device', 'Unknown')}")
            print(f"🌐 IP: {info.get('ip', 'Unknown')}")
            print(f"📶 信号强度: {info.get('rssi', 'N/A')} dBm")
            
            # 进入交互式控制
            interactive_control(controller)
        else:
            print("❌ 连接失败，请检查:")
            print("   - IP地址是否正确")
            print("   - ESP32和电脑是否在同一网络")
            print("   - ESP32服务器是否正在运行")
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")

if __name__ == "__main__":
    # 安装依赖: pip install requests
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序退出")
    except Exception as e:
        print(f"💥 程序异常: {e}")