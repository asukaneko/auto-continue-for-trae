import pyautogui
import time
import ctypes
import keyboard
import os

# 配置参数
# 目标列表：(文件名, 点击位置横向偏移量 0.5=中心 0.95=最右侧, 描述)
TARGETS = [
    ('target.png', 0.95, '默认继续'),
    ('delete.png', 0.5, '删除确认')
]

CHECK_INTERVAL = 2  # 检查间隔（秒）
CONFIDENCE = 0.8  # 匹配相似度（需要安装opencv-python）

# Windows API 常量
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """防止系统休眠和熄屏"""
    print("正在设置系统保持唤醒状态...")
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def restore_sleep():
    """恢复系统正常休眠策略"""
    print("正在恢复系统休眠策略...")
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

def main():
    print("脚本已启动！")
    print("按 'q' 键退出脚本。")

    valid_targets = []
    for filename, offset, desc in TARGETS:
        if os.path.exists(filename):
            print(f"已加载目标: {filename} ({desc})")
            valid_targets.append((filename, offset, desc))
        else:
            print(f"提示: 未找到 '{filename}' ({desc})，如需启用请截图保存为该文件名。")

    if not valid_targets:
        print("错误：未找到任何目标图片文件。请至少准备一个目标图片。")
        return

    prevent_sleep()
    print("系统唤醒设置成功！开始自动监控屏幕...")
    
    try:
        count = 0
        while True:
            if keyboard.is_pressed('q'):
                print("\n检测到退出按键，正在退出...")
                break

            # 每10次循环（约20秒）打印一次状态，表示程序在运行
            if count % 10 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] 正在监控中...", end='\r')
            count += 1

            found_any = False
            for filename, offset, desc in valid_targets:
                try:
                    # 查找屏幕上的目标图片
                    box = pyautogui.locateOnScreen(filename, confidence=CONFIDENCE)
                    
                    if box:
                        # 计算点击位置
                        click_x = box.left + box.width * offset
                        click_y = box.top + box.height * 0.5
                        
                        print(f"\n发现目标[{desc}]！区域: {box}, 点击位置: ({click_x}, {click_y})")
                        pyautogui.click(click_x, click_y)
                        print("已点击。等待5秒避免重复点击...")
                        time.sleep(5)  # 点击后等待一段时间
                        found_any = True
                        break # 找到一个后跳出循环，重新开始监控
                except pyautogui.ImageNotFoundException:
                    pass
                except Exception as e:
                    print(f"\n发生错误 ({desc}): {e}")

            if not found_any:
                # print("未找到目标，继续监控...", end='\r')
                pass

            time.sleep(CHECK_INTERVAL)
            
    finally:
        restore_sleep()
        print("脚本已结束。")

if __name__ == "__main__":
    main()
