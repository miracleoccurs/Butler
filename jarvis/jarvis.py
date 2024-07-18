import os
import sys
import time
import importlib
import importlib.util
import speech_recognition as sr
import pygame
import time
import json
import pyttsx3
import datetime
import subprocess
from pydub import AudioSegment
from playsound import playsound
from my_snowboy.snowboydecoder import HotwordDetector
#临时文件
import shutil
import tempfile
import concurrent.futures
from functools import lru_cache
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from thread import process_tasks
from binary_extensions import binary_extensions
from my_package.TextEditor import TextEditor
from my_package.virtual_keyboard import VirtualKeyboard
from my_package.Logging import *
from my_package.music import music_player
from my_package.crawler import crawler
from my_package.schedule_management import schedule_management
from my_package.Limits_of_authority import Limits_of_authority
import transformers
from transformers import BertTokenizer, BertForSequenceClassification
import torch

bert_model = "./model"
# 加载BERT模型和tokenizer
tokenizer = BertTokenizer.from_pretrained(bert_model)
model = BertForSequenceClassification.from_pretrained(bert_model)

def preprocess(text):
    inputs = tokenizer.encode_plus(
        text,
        None,
        add_special_tokens=True,
        max_length=512,
        pad_to_max_length=True,
        return_token_type_ids=True,
        truncation=True
    )
    input_ids = torch.tensor(inputs['input_ids']).unsqueeze(0)
    attention_mask = torch.tensor(inputs['attention_mask']).unsqueeze(0)
    return input_ids, attention_mask
    outputs = model(input_ids, attention_mask=attention_mask)
    logits = outputs[0]
    predicted_class = torch.argmax(logits, dim=1).item()

    # 根据分类结果，调用相应的功能程序
    if predicted_class in function_mapping:
        function_mapping[predicted_class]()

    # 使用 BERT 模型来生成回应语句
    response = generate_response(user_input)
    print("Chatbot:", response)
    
# 对话提示
prompt = "我是你的聊天助手。"

# 创建一个简单的对话循环
while True:
    user_input = input(">>> ")
    if user_input.lower() in ["退出", "结束"]:
        break
    response_class = get_response(user_input)
    response = f"分类结果: {response_class}"
    print(response)
    
def get_response(user_input):
    input_ids, attention_mask = preprocess(user_input)
    outputs = model(input_ids, attention_mask=attention_mask)
    logits = outputs[0]
    predicted_class = torch.argmax(logits, dim=1).item()
    return predicted_class
    
# 定义音频文件路径
JARVIS_AUDIO_FILE = "./my_snowboy/resources/jarvis.wav"
OUTPUT_FILE = "./temp.wav"
FINAL_OUTPUT_FILE = "./final_output.wav"

# 创建语音合成引擎
engine = pyttsx3.init()

def speak(audio):
    # 合成语音
    engine.say(audio)
    engine.runAndWait()  # 播放合成语音

    # 加载音效文件
    jarvis_sound = AudioSegment.from_wav(JARVIS_AUDIO_FILE)

    # 加载合成语音文件
    synthetic_speech = AudioSegment.from_wav(OUTPUT_FILE)

    # 调整音量
    synthetic_speech = synthetic_speech.apply_gain(10)  # 提高合成语音的音量
    jarvis_sound = jarvis_sound.apply_gain(-10)  # 降低音效的音量
    
    # 合并音频片段
    combined_sound = jarvis_sound.overlay(synthetic_speech)

    # 添加混响效果
    combined_sound = combined_sound.apply_reverb(reverb=AudioSegment.reverb(duration=1000))

    # 保存混合后的音频
    combined_sound.export(FINAL_OUTPUT_FILE, format="wav")

    # 播放混合后的音频
    playsound(FINAL_OUTPUT_FILE)

    # 删除临时文件
    os.remove(OUTPUT_FILE)

# 初始化日志
#   log_file = "program_log.txt"
#   logging.basicConfig(filename=log_file, level=logging.DEBUG)

logging = Logging.getLogger(__name__)

# 定义唤醒词和其他全局变量
WAKE_WORD = "jarvis"
Input_command = ">>> "
program_folder = ["./program", "./tools"]
model = "my_Snowboy/jarvis.umdl"  # Snowboy 模型文件路径

# 语音识别
def takecommand():
    recognizer = sr.Recognizer()   # 初始化语音识别器和文本到语音引擎
    global recognizer
    with sr.Microphone() as source:
        print("请说话...")
        recognizer.pause_threshold = 1  # 静态能量阈值
        recognizer.dynamic_energy_adjustment_damping = 0.15 # 调整阈值的平滑因子
        recognizer.dynamic_energy_ratio = 1.5  # 阈值调整比率
        recognizer.operation_timeout = 5  # 最长等待时间（秒）
        recognizer.energy_threshold = 4000      # 设置音量阈值
        recognizer.dynamic_energy_threshold = True  # 自动调整音量阈值
        recognizer.default = model
        audio = recognizer.listen(source, phrase_time_limit=5)
        # 将录制的音频保存为临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            audio_file_path = f.name
            f.write(audio.get_wav_data())
        return audio_file_path 
            
            # 使用 Snowboy 进行唤醒词检测
            try:
                from my_snowboy.snowboydecoder import HotwordDetector
                detector = HotwordDetector(model)
                result = detector.detect(audio_file_path)
                if result:
                    logging.info("唤醒词检测成功")
                    
                    # 识别语音
                    try:
                        print("Recognizing...")  # 识别中...
                        query = recognizer.recognize_sphinx(audio, language='zh-CN')
                        print('User: ' + query + '\n')
                        # 检查是否为 "运行文件" 命令
                        if "运行文件" in query:
                            file_name = query.replace("运行 ", "").strip()
                            # 使用 subprocess.run 执行文件
                            subprocess.run([file_name])
                            return None
                        else:
                            return query
                    except sr.UnknownValueError:
                        print("对不起，我没有听清楚，请再说一遍。")
                        speak("对不起，我没有听清楚，请再说一遍。")
                        return None
                    except sr.RequestError as error:
                        print(f"语音识别请求出错：{error}")
                        logging.error(f"语音识别请求出错：{error}")
                        return ""
                    except Exception as e:
                        print(f"语音识别出错: {e}")
                        logging.error(f"语音识别出错: {e}")
                        return None
                else:
                    print("没有检测到唤醒词")
                    logging.info("没有检测到唤醒词")
                    return None
            except Exception as e:
                print(f"Snowboy 检测出错: {e}")
                logging.error(f"Snowboy 检测出错: {e}")
                return None 

# 创建 Snowboy 监听器
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5, audio_gain=1)
detector.start(takecommand)

class ProgramHandler(FileSystemEventHandler):
    def __init__(self, program_folder):
        self.program_folder = program_folder
        self.programs_cache = {}
        self.programs = self.open_programs()

    def on_modified(self, event):
        if event.src_path.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    def on_created(self, event):
        if event.src_path.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
            self.programs = self.open_programs.clear_cache()()

    @lru_cache(maxsize=128)
    def open_programs(self):
        programs_cache = {}
        global programs_cache
        
        # 检查程序文件夹是否存在
        if not os.path.exists(program_folder):
            print(f"程序文件夹中 '{program_folder}' 未找到。")
            logging.info(f"程序文件夹中 '{program_folder}' 未找到。")
            return {}   
                  
        programs = {}
        for root, dirs, files in os.walk(self.program_folder):
            for file in files:
                if file.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
                    program_name = os.path.basename(root) + '.' + file[:-3]
                    program_path = os.path.join(root, file)

                    if program_name in self.programs_cache:
                        program_module = self.programs_cache[program_name]
                    else:
                        try:
                            spec = importlib.util.spec_from_file_location(program_name, program_path)
                            program_module = importlib.util.module_from_spec(spec)
                            sys.modules[program_name] = program_module
                            spec.loader.exec_module(program_module)
                            self.programs_cache[program_name] = program_module
                        except ImportError as e:
                            print(f"加载程序模块 '{program_name}' 时出错：{e}")
                            logging.info(f"加载程序模块 '{program_name}' 时出错：{e}")
                            continue

                    if not hasattr(program_module, 'run'):
                        print(f"程序模块 '{program_name}' 无效。")
                        logging.info(f"程序模块 '{program_name}' 无效。")
                        continue
                    programs[program_name] = program_module
                    
        # 按字母顺序排序程序模块
        programs = dict(sorted(programs.items()))
        return programs
        
def execute_program(program_name, handler):
    """执行程序"""
    program_module = handler.programs.get(program_name, None)
    if program_module:
        try:
            program_module.run()
        except Exception as e:
            logging.error(f"执行 '{program_name}' 程序时出错：{e}")
            speak(f"执行 '{program_name}' 程序时出错：{e}")
    else:
        logging.info(f"未找到程序: {program_name}")
        speak(f"未找到程序: {program_name}")
        
def main_program_logic(program_folder):
    handler = ProgramHandler(program_folder)
    observer = Observer()
    observer.schedule(handler, program_folder, recursive=True)
    observer.start()

    program_mapping = {
        "打开邮箱": "e-mail",
        "播放音乐": "music",
        "打开记事本": "notepad",
        "虚拟键盘": "virtual_keyboard",
        "组织": "OrganizeIT",
        "爬虫": "crawler",
        "终端": "terminal",
        # 在这里继续添加其他命令和程序的映射关系
    }
    
    # 对话历史记录
    conversation_history = []
    
    running = True
    while running:
        try:
            wake_command = takecommand().lower()
            if wake_command.startswith("打开"):
                # 如果命令以 "打开" 开头，则尝试动态解析并执行程序
                program_name = wake_command[3:].strip()
                # 添加权限控制代码
                required_permission = OPERATIONS.get(program_name.lower())
                execute_program(program_name, handler)  # 执行程序
                #if required_permission:
                #    if verify_permission(required_permission):
                #        print(f"权限验证成功，正在打开程序: {program_name}")
                #        execute_program(program_name, handler)  # 执行程序
                #    else:
                #        print(f"权限不足，无法打开程序: {program_name}")
                else:
                    print(f"未找到程序 '{program_name}") 
            elif wake_command in program_mapping:
                # 如果命令在映射关系中，则执行预定义程序
                program_name = program_mapping[wake_command]
                execute_program(program_name, handler)
            elif "退出" in wake_command or "结束" in wake_command:
                logging.info(f"{program_folder}程序已退出")
                speak(f"{program_folder}程序已退出")
                running = False
            else:
                logging.info(f"未知命令: {wake_command}")
                speak("未知命令")
        except Exception as error:
            logging.error(f"程序出现异常: {error}")
            print(f"程序出现异常: {error}")
            speak(f"程序出现异常: {error}")

    observer.stop()
    observer.join()

 # 主函数
def main():
    process_tasks()# 运行多线程程序
    schedule_management()
    # 获取系统的临时文件夹路径
    temp_dir = tempfile.gettempdir()

    # 指定要保存临时文件的文件夹路径
    target_dir = "./temp"

    # 创建一个临时文件
    temp_file_path = tempfile.mktemp(suffix=".txt", dir=temp_dir)

    # 在临时文件中写入数据
    with open(temp_file_path, 'w') as file:
        file.write("这是临时文件中的数据")

    # 将临时文件移动到目标文件夹
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.move(temp_file_path, target_dir)
    
    global matched_program
    matched_program = None
    pygame.init()  # 初始化 Pygame
    wen_jian = program_folder
    programs = open_programs(wen_jian)
    print("等待唤醒词")
    if not programs:
        print("没有找到程序模块")
        return ""

    running = True  # 控制程序是否继续运行的标志
    while running:
            
        # 开始监听
        detector.start(detected_callback=takecommand,
                       interrupt_check=lambda: False,
                       sleep_time=0.03)

        # 程序结束时停止监听
        detector.terminate()

        wake_command = takecommand().lower()#    recognize_sphinx(takecommand()).lower()
        user_input = None
        print("等待唤醒词")
        logging.info("等待唤醒词")
        if "退出" in wake_command or "结束" in wake_command:
            print("程序已退出")
            logging.info(f"用户已退出{program_folder}程序")
            running = False  # 设置标志为 False，用于退出主循环
                 
        if "手动输入" in wake_command:
            keyboard = VirtualKeyboard()
            # 打开虚拟键盘
            keyboard.open()
            # 获取虚拟键盘输入的字符
            input_text = keyboard.get_input()
            user_input = input_text.strip()
            logging.info("用户手动输入：" + user_input)
            if "退出" in user_input or "结束" in user_input:
                print("程序已退出")
                logging.info("用户已退出程序手写输入")
                running = False  # 设置标志为 False，用于退出主循环
                return None
            return user_input

        if WAKE_WORD in wake_command:
            print("已唤醒，等待命令...")
            logging.info("已唤醒，等待命令")
            time.sleep(1)

            # 通过文本交流获取用户输入
            query = input(Input_command)
            response_text = takecommand(query).lower()

            user_command = response_text[len(WAKE_WORD):].strip()  
            # 对用户输入进行处理，执行特定操作
            if "打开" in user_command:
                program_name = response_text.replace("打开", "").strip()
                if program_name in programs:
                    program_module = programs[program_name]
                    if program_module is not None:
                        program_module.run()
                    else:
                        print(f"未找到程序：{program_name}")
                        logging.info(f"未找到程序：{program_name}")
                else:
                    print(f"未找到程序：{program_name}")
                    logging.info(f"未找到程序：{program_name}")

            elif "退出" in user_command or "结束" in user_command:
                print("程序已退出")
                logging.info("用户已退出程序")
                running = False  # 设置标志为 False，用于退出主循环
            else:
                print("未知指令，请重试")
                logging.warning("未知指令")
                time.sleep(3)
                # 在这里添加后续的命令处理逻辑

                # 检查命令是否匹配程序模块
                matched_program = None
                for program_name, program_module in programs.items():
                    if program_name in wake_command:
                        matched_program = program_module
                        break  # 正常退出循环

                if matched_program is None:
                    # 检查命令是否匹配到模块文件名
                    for module_file in os.listdir(program_folder):
                        if module_file.endswith(('.py', 'invoke.py')) or event.src_path.split('.')[-1] in binary_extensions:
                            if module_file in wake_command:
                                module_path = f"{program_folder}.{module_file[:-3]}"
                                try:
                                    program_module = importlib.import_module(module_path)
                                    program_module.run()  # 此处调用了程序模块的 run 函数
                                    continue
                                except ImportError as error:
                                    print(f"导入模块失败: {error}")
                                    logging.error(f"导入模块失败: {error}")

    # 退出程序
    if not running:
        # 打开另一个程序
        os.system("python Bide_one's_time.py")

if __name__ == "__main__":  
    while True:
        try:     
            music_player()
            # 执行主程序的逻辑
            main()
            # 执行主程序的逻辑
            main_program_logic(program_folder)
        finally:
            try:
                main_program_logic(program_folder)  # 执行主程序的逻辑
            except Exception as error:
                print(f"程序发生异常：{error}")
                logging.info(f"程序发生异常：{error}")
