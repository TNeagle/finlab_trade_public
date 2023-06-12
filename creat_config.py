import os
import json
from tkinter import *
import tkinter as tk
from tkinter import filedialog

def read_config():
    # 建立主視窗
    root = tk.Tk()
    root.title("提示訊息")

    # 建立標籤，顯示提示訊息
    label = tk.Label(root, text="如果不能打小數點，記得把輸入法切換到英數喔。", font=("Arial", 24))
    label.pack(padx=50, pady=50)

    # 建立按鈕，設定按下後的動作
    def close_window():
        root.destroy()
    button = tk.Button(root, text="確定", command=close_window)
    button.pack(pady=10)

    # 進入主迴圈
    root.mainloop()

    # 讀取或創建 acc_config.txt
    if os.path.exists("acc_config.txt"):
        with open("acc_config.txt", "r") as f:
            acc_config = json.load(f)
    else:
        acc_config = {}
        window = Tk()
        window.title('創建 acc_config.txt')

        # 建立視窗元素
        Label(window, text="FUGLE_CONFIG_PATH").grid(row=0, column=0)
        Label(window, text="富果交易憑證路徑").grid(row=1, column=0)
        Label(window, text="玉山證券帳號").grid(row=2, column=0)
        Label(window, text="玉山證券密碼").grid(row=3, column=0)
        Label(window, text="富果交易憑證密碼").grid(row=4, column=0)
        #Label(window, text="PYTHON_KEYRING_BACKEND").grid(row=5, column=0)
        Label(window, text="Line_Notify_權杖").grid(row=6, column=0)
        Label(window, text="finlab_api_token").grid(row=7, column=0)
        Label(window, text="富果行情API_token").grid(row=8, column=0)

        entry1 = Entry(window)
        entry2 = Entry(window)
        entry3 = Entry(window)
        entry4 = Entry(window)
        entry5 = Entry(window)
        #entry6 = Entry(window)
        entry7 = Entry(window)
        entry8 = Entry(window)
        entry9 = Entry(window)

        entry1.grid(row=0, column=1)
        entry2.grid(row=1, column=1)
        entry3.grid(row=2, column=1)
        entry4.grid(row=3, column=1)
        entry5.grid(row=4, column=1)
        #entry6.grid(row=5, column=1)
        entry7.grid(row=6, column=1)
        entry8.grid(row=7, column=1)
        entry9.grid(row=8, column=1)

        def select_file1():
            file_path = filedialog.askopenfilename()
            if file_path:
                entry1.delete(0, tk.END)
                entry1.insert(0, file_path)
        entry1_button = tk.Button(window, text="選擇檔案", command=select_file1)
        entry1_button.grid(row=0, column=2)

        def select_file2():
            file_path = filedialog.askopenfilename()
            if file_path:
                entry2.delete(0, tk.END)
                entry2.insert(0, file_path)
        entry2_button = tk.Button(window, text="選擇檔案", command=select_file2)
        entry2_button.grid(row=1, column=2)


        # 確定按鈕的功能
        def save_config():
            acc_config["FUGLE_CONFIG_PATH"] = entry1.get()
            acc_config["FUGLE_CERT_PATH"] = entry2.get()
            acc_config["FUGLE_ACCOUNT"] = entry3.get()
            acc_config["FUGLE_ACCOUNT_PASSWORD"] = entry4.get()
            acc_config["FUGLE_CERT_PASSWORD"] = entry5.get()
            acc_config["PYTHON_KEYRING_BACKEND"] = 'keyrings.cryptfile.cryptfile.CryptFileKeyring'#entry6.get()
            acc_config["Line_notify_token"] = entry7.get()
            acc_config["finlab_api_token"] = entry8.get()
            acc_config["FUGLE_MARKET_API_KEY"] = entry9.get()

            with open("acc_config.txt", "w") as f:
                json.dump(acc_config, f)

            window.destroy()

        button = Button(window, text="確定", command=save_config)
        button.grid(row=10, column=1)

        window.mainloop()

    print(json.dumps(acc_config, indent=4))

    # 讀取或創建 order_config.txt
    if os.path.exists("order_config.txt"):
        with open("order_config.txt", "r") as f:
            order_config = json.load(f)
    else:
        order_config = {}
        window = Tk()
        window.title('創建 order_config.txt')
        # 建立視窗元素
        Label(window, text="成交量濾網").grid(row=0)
        Label(window, text="操作資金").grid(row=1)
        Label(window, text="零股上限 ex.設800,超過800股的就會算做一張").grid(row=2)
        Label(window, text="交易緩衝 ex.設0.2,股價漲跌超過20%就會重新平衡").grid(row=3)
        Label(window, text="交易時間(24小時制) ex.15:30").grid(row=4)
        #Label(window, text="PYTHON_KEYRING_BACKEND").grid(row=5)

        entry1 = Entry(window)
        entry2 = Entry(window)
        entry3 = Entry(window)
        entry4 = Entry(window)
        entry5 = Entry(window)
        #entry6 = Entry(window)

        entry1.grid(row=0, column=1)
        entry2.grid(row=1, column=1)
        entry3.grid(row=2, column=1)
        entry4.grid(row=3, column=1)
        entry5.grid(row=4, column=1)
        #entry6.grid(row=5, column=1)

        # 確定按鈕的功能
        def save_config2():
            order_config["vol_limitation"] = entry1.get()
            order_config["fund"] = entry2.get()
            order_config["odd_limitation"] = entry3.get()
            order_config["trade_buffer"] = entry4.get()
            order_config["trade_time"] = entry5.get()
            #config["PYTHON_KEYRING_BACKEND"] = 'keyrings.cryptfile.cryptfile.CryptFileKeyring'#entry6.get()

            with open("order_config.txt", "w") as f:
                json.dump(order_config, f)

            window.destroy()

        button = Button(window, text="確定", command=save_config2)
        button.grid(row=6, column=1)

        window.mainloop()

    # 印出 config
    print(json.dumps(order_config, indent=4))
    return acc_config, order_config