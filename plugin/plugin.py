import tkinter as tk
from tkinter import messagebox
from package import Logging
from plugin_manager import PluginManager
from jarvis.jarvis import takecommand, speak
from jarvis import InputProcessor

# 插件导入
from plugin.Notepad_plugin import NotepadPlugin
from plugin.read_file import ReadFilePlugin
from plugin.CountdownPlugin import CountdownPlugin
from plugin.downloaded_url import DownloadURLPlugin
from plugin.JokePlugin import JokePlugin
from plugin.FileSearchPlugin import FileSearchPlugin
from plugin.GithubPlugin import GithubPlugin
from plugin.write_file import WriteFilePlugin
from plugin.TodoPlugin import TodoPlugin
from plugin.TimePlugin import TimePlugin
from plugin.SearchPlugin import SearchPlugin
from plugin.BluetoothPlugin import BluetoothPlugin

# 配置日志
logger = Logging.getLogger(__name__)

# 初始化 PluginManager 并传入插件包的路径
plugin_manager = PluginManager(plugin_package="plugins")

# 插件名称列表
plugins_to_manage = {
    "TimePlugin": {"takecommand": "查询时间", "args": {}},
    "CountdownPlugin": {"takecommand": "倒计时", "args": {}},
    "FileSearchPlugin": {"takecommand": ["搜索", "搜索一下"], "args": {}},
    "JokePlugin": {"takecommand": ["我无聊了", "休息一下", "讲个笑话", "好无聊"], "args": {}},
    "NotepadPlugin": {"takecommand": ["记笔记", "添加笔记", "查看笔记", "删除笔记", "编辑笔记", "搜索笔记"], "args": {}},
    "TodoPlugin": {"takecommand": {"添加待办事项", "列出待办事项", "删除待办事项"}, "args": {}},
    "clear_recent_memory": {"takecommand": {"清理长期记忆"}, "args": {}},
    "downloaded_url": {"takecommand": {"下载网页"}, "args": {}},
    "read_file": {"takecommand": {"读取", "读取文件"}, "args": {}},
    "write_file": {"takecommand": {"写入", "写入文件"}, "args": {}},
    "SearchPlugin": {"takecommand": ["在百度搜索", "在Bing搜索", "bilibili搜索", "快手搜索", "抖音搜索"], "args": {}},
    "BluetoothPlugin": {"takecommand": ["搜索蓝牙设备", "连接蓝牙设备", "断开蓝牙设备"], "args": {}},
}

# 加载所有插件
all_plugins = plugin_manager.get_all_plugins()
logger.info(f"已加载插件: {[plugin.get_name() for plugin in all_plugins]}")

def match_command_to_plugin(command: str):
    """根据语音命令匹配对应的插件."""
    for plugin_name, details in plugins_to_manage.items():
        takecommands = details['takecommand']
        
        if isinstance(takecommands, str):
            takecommands = [takecommands]
        
        if isinstance(takecommands, (set, list)) and not takecommands:
            continue

        if any(cmd in command for cmd in takecommands):
            for plugin in all_plugins:
                if plugin.get_name() == plugin_name:
                    return plugin_name, details['args'], plugin
    return None, None, None

def process_command(command: str):
    """处理指令并执行相应的插件."""
    plugin_name, args, plugin = match_command_to_plugin(command)

    if plugin_name:
        logger.info(f"匹配到插件: {plugin_name}，执行中...")
        result = plugin_manager.run_plugin(name=plugin_name, takecommand=command, args=args)
        logger.info(f"{plugin_name} 运行结果: {result}")
        speak(f"{plugin_name} 运行结果: {result}")
        
        status = plugin_manager.get_plugin_status(name=plugin_name)
        logger.info(f"{plugin_name} 状态: {status}")
        speak(f"{plugin_name} 状态: {status}")

        stop_result = plugin_manager.stop_plugin(name=plugin_name)
        logger.info(f"{plugin_name} 停止结果: {stop_result}")
        speak(f"{plugin_name} 停止结果: {stop_result}")
    else:
        speak("未找到匹配的插件。请尝试其他命令。")

def plugin():
    """主函数，处理语音和文字输入，默认语音输入。"""
    use_text_input = False
    input_processor = InputProcessor.InputProcessor()
    while True:
        if not use_text_input:
            command = input_processor.process_voice_input()
            if not command:
                speak("请再说一遍，我没有听清楚。")
                continue
        else:
            command = input_processor.process_text_input()

        process_command(command)

        if not use_text_input:
            switch_input = input("输入 1 切换到文字输入，输入 2 返回语音输入，其他键退出：")
            if switch_input == "1":
                use_text_input = True
                speak("已切换到文字输入模式。")
            elif switch_input == "2":
                use_text_input = False
                speak("已切换到语音输入模式。")
            else:
                speak("退出程序。")
                break
        else:
            switch_input = input("输入 2 返回语音输入，其他键退出：")
            if switch_input == "2":
                use_text_input = False
                speak("已切换到语音输入模式。")
            else:
                speak("退出程序。")
                break
