import os
import time
import requests
from bs4 import BeautifulSoup
import random
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

class ImageDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器")
        self.root.geometry("600x650")
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('TLabel', font=('微软雅黑', 10))
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('TRadiobutton', font=('微软雅黑', 10))
        style.configure('TCheckbutton', font=('微软雅黑', 10))
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 搜索关键词区域
        search_frame = ttk.LabelFrame(main_frame, text="搜索设置", padding="10")
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="搜索关键词:").pack(anchor='w')
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(fill=tk.X, pady=(5, 10))
        self.search_entry.insert(0, "Restaurant")
        
        ttk.Label(search_frame, text="下载数量:").pack(anchor='w')
        self.count_entry = ttk.Entry(search_frame, width=40)
        self.count_entry.pack(fill=tk.X, pady=5)
        self.count_entry.insert(0, "10")
        
        # 下载模式区域
        mode_frame = ttk.LabelFrame(main_frame, text="下载模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.download_mode = tk.StringVar(value="顺序")
        ttk.Radiobutton(mode_frame, text="顺序下载", variable=self.download_mode, value="顺序").pack(anchor='w', pady=2)
        ttk.Radiobutton(mode_frame, text="随机下载", variable=self.download_mode, value="随机").pack(anchor='w', pady=2)
        ttk.Radiobutton(mode_frame, text="跳跃下载", variable=self.download_mode, value="跳跃").pack(anchor='w', pady=2)
        
        # 跳跃设置区域
        jump_frame = ttk.Frame(mode_frame)
        jump_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(jump_frame, text="跳跃距离:").pack(side='left')
        self.jump_entry = ttk.Entry(jump_frame, width=10)
        self.jump_entry.pack(side='left', padx=5)
        self.jump_entry.insert(0, "2")
        
        # 命名选项区域
        name_frame = ttk.LabelFrame(main_frame, text="命名选项", padding="10")
        name_frame.pack(fill=tk.X, pady=10)
        
        self.rename_var = tk.BooleanVar(value=False)
        self.rename_check = ttk.Checkbutton(
            name_frame,
            text="统一命名（例：关键词1.jpg, 关键词2.jpg）",
            variable=self.rename_var
        )
        self.rename_check.pack(anchor='w')
        
        # 保存路径区域
        path_frame = ttk.LabelFrame(main_frame, text="保存位置", padding="10")
        path_frame.pack(fill=tk.X, pady=10)
        
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X)
        
        self.path_entry = ttk.Entry(path_input_frame)
        self.path_entry.pack(side='left', fill=tk.X, expand=True, padx=(0, 5))
        self.path_entry.insert(0, r'C:\Users\86147\图片\pypicture')
        
        self.browse_btn = ttk.Button(path_input_frame, text="浏览", command=self.browse_path)
        self.browse_btn.pack(side='right')
        
        # 下载按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        download_btn = ttk.Button(btn_frame, text="开始下载", command=self.start_download, style='Accent.TButton')
        download_btn.pack(pady=5)
        
        # 进度显示
        self.progress_label = ttk.Label(main_frame, text="", font=('微软雅黑', 9))
        self.progress_label.pack(pady=10)
        
        # 添加状态栏
        self.status_label = ttk.Label(root, text="就绪", relief=tk.SUNKEN, anchor='w')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 设置日志
        self.setup_logging()

    def setup_logging(self):
        # 配置日志
        self.logger = logging.getLogger('ImageDownloader')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        fh = logging.FileHandler('error.txt', encoding='utf-8')
        fh.setLevel(logging.ERROR)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)

    def browse_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def start_download(self):
        self.status_label.config(text="正在下载...")
        keyword = self.search_entry.get().strip()
        save_path = self.path_entry.get().strip()
        
        try:
            count = int(self.count_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的下载数量！")
            return
            
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词！")
            return
            
        if not save_path:
            messagebox.showerror("错误", "请选择保存路径！")
            return
            
        # 创建以关键词命名的子文件夹
        keyword_folder = os.path.join(save_path, keyword)
        if not os.path.exists(keyword_folder):
            os.makedirs(keyword_folder)
            
        self.progress_label.config(text="开始下载...")
        self.root.update()
        
        try:
            self.download_images(keyword, count, keyword_folder)
            messagebox.showinfo("完成", f"成功下载了 {count} 张图片到文件夹 {keyword_folder}！")
            self.status_label.config(text="下载完成")
        except Exception as e:
            messagebox.showerror("错误", f"下载过程中出现错误：{str(e)}")
            self.status_label.config(text="下载出错")
        finally:
            self.progress_label.config(text="")

    def download_images(self, keyword, count, save_folder):
        try:
            base_url = f'https://www.vcg.com/creative-image/{keyword}'
            
            # 更新状态
            self.progress_label.config(text="正在获取图片列表...")
            self.root.update()
            
            soup = make_soup(base_url)
            all_img_urls = get_image_urls(soup)
            
            if not all_img_urls:
                raise Exception("未找到任何图片")
            
            # 根据下载模式选择图片
            if self.download_mode.get() == "顺序":
                img_urls = all_img_urls[:count]
            elif self.download_mode.get() == "随机":
                img_urls = random.sample(all_img_urls, min(count, len(all_img_urls)))
            elif self.download_mode.get() == "跳跃":
                try:
                    jump_distance = int(self.jump_entry.get().strip())
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的跳跃距离！")
                    return
                img_urls = all_img_urls[::jump_distance][:count]
            
            # 确定起始编号
            start_index = self.get_start_index(keyword, save_folder)
            
            # 创建进度条
            progress_window = tk.Toplevel(self.root)
            progress_window.title("下载进度")
            progress_window.geometry("300x150")
            progress_window.transient(self.root)  # 设置为主窗口的子窗口
            
            ttk.Label(progress_window, text="正在下载...").pack(pady=10)
            progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
            progress_bar.pack(pady=10)
            progress_text = ttk.Label(progress_window, text="")
            progress_text.pack(pady=10)
            
            # 设置进度条最大值
            progress_bar['maximum'] = len(img_urls)
            
            for i, img_url in enumerate(img_urls, start=1):
                # 更新进度显示
                progress_text.config(text=f"正在下载第 {i}/{len(img_urls)} 张图片")
                progress_bar['value'] = i
                self.status_label.config(text=f"正在下载: {i}/{len(img_urls)}")
                
                # 更新界面
                progress_window.update()
                self.root.update_idletasks()
                
                if self.rename_var.get():
                    filename = f"{keyword}{start_index + i - 1}.jpg"
                else:
                    filename = img_url.split('/')[-1].split('?')[0]
                    
                save_path = os.path.join(save_folder, filename)
                
                try:
                    download_image(img_url, save_path)
                except Exception as e:
                    self.logger.error(f"下载失败 {img_url}: {str(e)}")
                    continue
                
                # 控制更新频率，避免界面卡顿
                if i % 2 == 0:  # 每下载两张图片更新一次界面
                    time.sleep(0.1)  # 短暂延时，让界面有机会响应
            
            # 关闭进度窗口
            progress_window.destroy()
            
        except Exception as e:
            self.logger.error(f"下载过程出错: {str(e)}")
            raise

    def get_start_index(self, keyword, save_folder):
        # 获取文件夹中已有的最大编号
        existing_files = [f for f in os.listdir(save_folder) if f.startswith(keyword) and f.endswith('.jpg')]
        max_index = 0
        for file in existing_files:
            try:
                index = int(file[len(keyword):-4])  # 提取编号
                if index > max_index:
                    max_index = index
            except ValueError:
                continue
        return max_index + 1

def make_soup(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logging.error(f'Error making soup for {url}: {str(e)}')
        raise

def get_image_urls(soup):
    img_urls = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('data-src') or img_tag.get('src')
        if img_url:
            if not img_url.lower().endswith('.jpg') and not img_url.lower().endswith('.jpeg'):
                continue
                
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://www.vcg.com' + img_url
            
            logging.debug(f'Found image URL: {img_url}')
            img_urls.append(img_url)
    return img_urls

def download_image(url, save_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        return True
    except Exception as e:
        logging.error(f'Error downloading {url}: {str(e)}')
        return False

def main():
    root = tk.Tk()
    app = ImageDownloaderGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
