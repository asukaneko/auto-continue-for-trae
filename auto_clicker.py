import pyautogui
import time
import ctypes
import keyboard
import os

# 配置参数
TARGET_IMAGE = 'target.png'  # 目标图片文件名
CHECK_INTERVAL = 2  # 检查间隔（秒）
CONFIDENCE = 0.8  # 匹配相似度（需要安装opencv-python）
CLICK_OFFSET_X = 0.95  # 点击位置的横向偏移量（0.5为中心，0.95为最右侧）

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
    print(f"请确保目录中存在 '{TARGET_IMAGE}' 图片文件。")
    print("按 'q' 键退出脚本。")

    if not os.path.exists(TARGET_IMAGE):
        print(f"错误：未找到 '{TARGET_IMAGE}'。请截图目标按钮并保存为该文件名。")
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

            try:
                # 查找屏幕上的目标图片
                box = pyautogui.locateOnScreen(TARGET_IMAGE, confidence=CONFIDENCE)
                
                if box:
                    # 计算点击位置
                    click_x = box.left + box.width * CLICK_OFFSET_X
                    click_y = box.top + box.height * 0.5
                    
                    print(f"发现目标！区域: {box}, 点击位置: ({click_x}, {click_y})")
                    pyautogui.click(click_x, click_y)
                    print("已点击继续。等待5秒避免重复点击...")
                    time.sleep(5)  # 点击后等待一段时间
                else:
                    # print("未找到目标，继续监控...", end='\r')
                    pass
                    
            except pyautogui.ImageNotFoundException:
                # print("未找到目标（异常），继续监控...", end='\r')
                pass
            except Exception as e:
                print(f"发生错误: {e}")

            time.sleep(CHECK_INTERVAL)
            
    finally:
        restore_sleep()
        print("脚本已结束。")

if __name__ == "__main__":
    main()
