#!/usr/bin/env python
# coding=utf-8

import random
import threading
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename

from PIL import ImageTk, Image


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('月时计')
        self.config(bg='blue')
        self.width, self.height = self.maxsize()
        self.geometry("{}x{}".format(self.width, self.height))
        self.resizable(False, False)
        self.index = tk.Label(self, bg='gray')
        self.index.pack(expand=True, fill=tk.BOTH)

        self.init_menu()

        self.title_name = '未命名'
        self.begin_num = 0
        self.end_num = 0
        self.counts = 0
        self.bg_path = None

    def init_menu(self):
        menubar = tk.Menu(self)
        setting_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='设置', menu=setting_menu)
        setting_menu.add_command(label='抽取设置', command=self.update_settings)
        setting_menu.add_separator()
        setting_menu.add_command(label='退出', command=self.quit)
        self.config(menu=menubar)

    def init_lottery_UI(self):
        self.index.destroy()
        bg = None
        if self.bg_path:
            image = Image.open(self.bg_path)
            image = image.resize((self.width, self.height), Image.ANTIALIAS)
            self.bg = ImageTk.PhotoImage(image)
            self.index = tk.Label(self, image=self.bg)
        else:
            self.index = tk.Label(self, bg='blue')
        self.index.pack(expand=True, fill=tk.BOTH)
        tk.Label(self.index, text=self.title_name, bg='white', font=('微软雅黑', 32)).pack(pady=50)
        btns = tk.Frame(self.index)
        btns.pack()
        tk.Button(btns, text='开始', command=self.start_lottery).pack(side=tk.LEFT)
        tk.Button(btns, text='停止', command=self.end_lottery).pack(side=tk.LEFT)

        results_pannels = []
        for i in range(self.counts // 10 + 1):
            results_pannel = tk.Frame(self.index, bg='red')
            if i == 0:
                results_pannel.pack(pady=50)
            results_pannel.pack(pady=4)
            results_pannels.append(results_pannel)

        self.results = []
        for i in range(self.counts):
            num = tk.IntVar()
            tk.Label(results_pannels[i // 10], textvariable=num, bg='white', font=('Arial', 22), width=5, height=1). \
                pack(padx=2, side=tk.LEFT)
            self.results.append(num)

    def update_settings(self):
        self.running_flag = False
        res = self.request_settings()
        self.title_name = res.get('title_name') if res.get('title_name', '') != '' else '未命名'
        self.begin_num = res.get('begin_num', 0)
        self.end_num = res.get('end_num', 0)
        self.counts = res.get('counts', 0)
        self.bg_path = res.get('bg_path') if res.get('bg_path', '') != '' else None
        self.init_lottery_UI()

    def request_settings(self):
        input_dialog = MyDialog()
        self.wait_window(input_dialog)
        try:
            res = input_dialog.settings
        except Exception as e:
            res = dict(title_name=self.title_name,
                       begin_num=self.begin_num,
                       end_num=self.end_num,
                       counts=self.counts,
                       bg_path=self.bg_path)
        finally:
            return res

    def start_lottery(self):
        self.running_flag = True
        p = threading.Thread(target=self.async_lottery)
        p.start()

    def async_lottery(self):
        while self.running_flag:
            select_list = range(self.begin_num, self.end_num + 1)
            selected_list = random.sample(select_list, self.counts)
            for i in range(self.counts):
                self.results[i].set(selected_list[i])
            time.sleep(0.1)

    def end_lottery(self):
        self.running_flag = False


class MyDialog(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('抽取设置')
        self.wm_attributes("-topmost", 1)
        self.setup_UI()

    def setup_UI(self):
        row1 = tk.Frame(self)
        row1.pack(fill="x")
        tk.Label(row1, text='标题：', width=8).pack(side=tk.LEFT)
        self.title_name = tk.StringVar()
        tk.Entry(row1, textvariable=self.title_name, width=20).pack(side=tk.LEFT)

        row2 = tk.Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text='起始值：', width=8).pack(side=tk.LEFT)
        self.begin_num = tk.IntVar()
        tk.Entry(row2, textvariable=self.begin_num, width=20).pack(side=tk.LEFT)

        row3 = tk.Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row3, text='结束值：', width=8).pack(side=tk.LEFT)
        self.end_num = tk.IntVar()
        tk.Entry(row3, textvariable=self.end_num, width=20).pack(side=tk.LEFT)

        row4 = tk.Frame(self)
        row4.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row4, text='抽取数：', width=8).pack(side=tk.LEFT)
        self.counts = tk.IntVar()
        tk.Entry(row4, textvariable=self.counts, width=20).pack(side=tk.LEFT)

        row5 = tk.Frame(self)
        row5.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row5, text='活动背景图片路径：', width=20).pack(side=tk.LEFT)
        self.bg_path = tk.StringVar()
        tk.Entry(row5, textvariable=self.bg_path, width=40).pack(side=tk.LEFT)
        tk.Button(row5, text="路径选择", command=self._select_path).pack(side=tk.LEFT)

        row6 = tk.Frame(self)
        row6.pack(fill="x")
        tk.Button(row6, text="确定", command=self.save).pack(side=tk.LEFT)
        tk.Button(row6, text="取消", command=self.cancel).pack(side=tk.LEFT)

    def _select_path(self):
        self.bg_path.set(askopenfilename())

    def save(self):
        self.settings = dict(title_name=self.title_name.get(),
                             begin_num=self.begin_num.get(),
                             end_num=self.end_num.get(),
                             counts=self.counts.get(),
                             bg_path=self.bg_path.get())
        self.destroy()

    def cancel(self):
        self.settings = dict()
        self.destroy()


if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
