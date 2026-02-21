import pyautogui
import time
import ctypes
import keyboard
import os

# 配置参数
# 目标列表：(文件名, (横向偏移量, 纵向偏移量), 描述)
# 偏移量：0.5=中心，0.0=最左/上，1.0=最右/下
# 【重要】如果目标图片包含变动文字（如文件名），识别会失败。请务必只截图固定的按钮部分！
TARGETS = [
    ('target.png', (0.95, 0.5), '默认继续'),
    # 针对删除确认弹窗，建议仅截图红色的【删除】按钮本身，此时偏移量设为 (0.5, 0.5) 点击中心即可
    ('delete.png', (0.5, 0.5), '删除按钮(请仅截图红色按钮)'),
]

# 后续操作：当点击了某个目标后，需要接着检查的图片
# 格式：{ '触发图片文件名': [ ('后续图片文件名', (偏移量), '描述') ] }
FOLLOW_UP_TARGETS = {
    'delete.png': [
        ('yes.png', (0.5, 0.5), '确认按钮')
    ]
}

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

def click_target(filename, offset, desc):
    """查找并点击单个目标，成功返回True"""
    try:
        # 兼容旧配置格式 (filename, offset_x, desc)
        if isinstance(offset, (int, float)):
            offset = (offset, 0.5)
            
        box = pyautogui.locateOnScreen(filename, confidence=CONFIDENCE)
        if box:
            offset_x, offset_y = offset
            click_x = box.left + box.width * offset_x
            click_y = box.top + box.height * offset_y
            
            print(f"\n发现目标[{desc}]！区域: {box}, 点击位置: ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            return True
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"\n发生错误 ({desc}): {e}")
    return False

def check_follow_up(trigger_filename):
    """检查是否有后续操作"""
    if trigger_filename in FOLLOW_UP_TARGETS:
        follow_ups = FOLLOW_UP_TARGETS[trigger_filename]
        print(f"检测到[{trigger_filename}]的后续操作，开始监控后续目标...")
        
        # 尝试检测后续目标，最多尝试10次（约10秒）
        for i in range(10):
            print(f"正在等待后续目标出现 ({i+1}/10)...", end='\r')
            time.sleep(1)
            
            for f_filename, f_offset, f_desc in follow_ups:
                if click_target(f_filename, f_offset, f_desc):
                    print(f"\n成功执行后续操作：{f_desc}")
                    print("等待5秒避免重复点击...")
                    time.sleep(5)
                    return

        print("\n未检测到后续目标，停止等待。")

def main():
    print("脚本已启动！")
    print("按 'q' 键退出脚本。")

    valid_targets = []
    for item in TARGETS:
        filename = item[0]
        offset = item[1]
        desc = item[2]
        
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
                if click_target(filename, offset, desc):
                    # 如果点击成功，检查是否有后续操作
                    check_follow_up(filename)
                    
                    if filename not in FOLLOW_UP_TARGETS:
                        print("已点击。等待5秒避免重复点击...")
                        time.sleep(5)
                        
                    found_any = True
                    break # 找到一个后跳出循环，重新开始监控

            if not found_any:
                # print("未找到目标，继续监控...", end='\r')
                pass

            time.sleep(CHECK_INTERVAL)
            
    finally:
        restore_sleep()
        print("脚本已结束。")

if __name__ == "__main__":
    main()
