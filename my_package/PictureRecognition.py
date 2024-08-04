import tkinter as tk
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import base64

# 使用 Bing 图片搜索 API
def search_image():
    """
    使用 Bing 图片搜索 API 搜索图片相关信息。
    """

    image_path = entry.get()  # 获取输入框中的图片路径

    if image_path:
        # 将图片转换为 Base64 编码
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Bing 图片搜索 API 请求 URL
        api_url = "https://www.bing.com/images/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
        }
        data = {
            "q": "imgurl:" + encoded_image,
            "form": "HDRSC2",
        }

        # 发送请求
        response = requests.post(api_url, headers=headers, data=data)

        # 解析搜索结果页面
        soup = BeautifulSoup(response.content, "html.parser")

        # 提取搜索结果信息
        results = {
            "url": response.url,
            "title": soup.find("title").text,
            "description": soup.find("meta", attrs={"name": "description"}).get("content"),
            "images": [],
        }

        # 提取所有搜索结果图片 URL
        for img in soup.find_all("img", attrs={"src": True}):
            results["images"].append(img.get("src"))

        # 打印搜索结果
        print("搜索结果页面 URL：", results["url"])
        print("搜索结果页面标题：", results["title"])
        print("搜索结果页面描述：", results["description"])
        print("搜索结果图片 URL：", results["images"])

# 处理拖放事件
def drop(event):
    """
    处理拖放事件，获取拖放的图片路径。
    """
    file_path = event.data
    entry.delete(0, tk.END)  # 清空输入框
    entry.insert(0, file_path)  # 在输入框中插入图片路径

# 创建 Tkinter 窗口
window = tk.Tk()
window.title("图片搜索")

# 创建输入框
entry = tk.Entry(window)
entry.pack()

# 创建搜索按钮
search_button = tk.Button(window, text="搜索", command=search_image)
search_button.pack()

# 设置拖放功能
window.drop_target_register(DND_FILES)
window.dnd_bind("<<Drop>>", drop)

# 运行窗口
window.mainloop()
