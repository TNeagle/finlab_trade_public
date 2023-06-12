import schedule
import finlab
import os
import keyring
import time
from fugle_trade.util import setup_keyring
from finlab.online.order_executor import Position
from finlab.online.fugle_account import FugleAccount
from finlab.online.order_executor import OrderExecutor
from finlab.backtest import sim
from finlab import data
import pandas as pd
import numpy as np
from finlab.optimize.combinations import sim_conditions
from itertools import chain, combinations
from finlab.dataframe import FinlabDataFrame
import pickle
from datetime import datetime
from time import sleep
from creat_config import read_config
import configparser
import requests

def get_position_from_GCP(vol_limitation,fund):
    data  = {
      'vol_limitation':vol_limitation,
      'fund':fund
    }
    #將參數丟到cloud function取得股票配置的名單及數量
    response = requests.post('',data=data)
    a = response.json()
    position = Position.from_list(a['data'])
    return position

def get_stock_position(vol_limitation,fund):
    position_1 = strategy_1(vol_limitation,4)
    position_5 = strategy_5(vol_limitation,7)
    position = position_1 + position_5
    report = sim(position, resample=None, upload=True, position_limit=1, fee_ratio=1.425/1000/3, stop_loss=None,  trade_at_price='open',name='執行中的交易策略')
    stock_position = Position.from_report(report, fund, odd_lot=True)
    return stock_position

def job():
    print('開始執行程式')
    if finlab_api_token == '':
        try:
            from strategy import get_position_from_GCP
            position = get_position_from_GCP(vol_limitation,fund)
        except:
            print('請輸入Finlab的vip token')
            
    else:
        finlab.login(finlab_api_token)
        position = get_stock_position(vol_limitation,fund)
    
    #執行交易
    os.environ['FUGLE_CONFIG_PATH'] = FUGLE_CONFIG_PATH 
    os.environ['FUGLE_MARKET_API_KEY'] = FUGLE_MARKET_API_KEY # 獲取市價行情以進行下單

    setup_keyring(FUGLE_ACCOUNT)
    keyring.set_password("fugle_trade_sdk:account", FUGLE_ACCOUNT, FUGLE_ACCOUNT_PASSWORD)
    keyring.set_password("fugle_trade_sdk:cert", FUGLE_ACCOUNT, FUGLE_CERT_PASSWORD)
    acc = FugleAccount()
    inventory = acc.get_position() #FUGLE第一次查詢
    
    new_position = []
    for i in position.position:
        #把position的股票代號和inventory的股票代號進行對比，有相同的走else，沒有相同的輸出{}
        j = next(( k for k in inventory.position if k['stock_id'] == i['stock_id']),{})
        if j == {}:
            if i['quantity']%1>(odd_limitation/1000):
                i['quantity']=i['quantity']//1+1
                new_position.append(i)
            else:
                new_position.append(i)
        else:
            if abs((i['quantity']-j['quantity'])/j['quantity']) > trade_buffer:
                if i['quantity']%1>(odd_limitation/1000):
                    i['quantity']=i['quantity']//1+1
                    new_position.append(i)
                else:
                    new_position.append(i)
            else:
                new_position.append(j)
    
    position = Position.from_dict(new_position)
    time.sleep(10) #Fugle限制兩次之間要間隔十秒
    order_executer = OrderExecutor(position , account=acc) #FUGLE第二次
    # 用模擬模式產生下單的明細並回傳，之後會輸出在網頁上 (optional)
    record = order_executer.create_orders(view_only=True)
    
    # LINE Notify 權杖
    token = Line_notify_token
    
    # HTTP 標頭參數與資料
    headers = { "Authorization": "Bearer " + token }
    
    if record == []:
        message = time.strftime("%Y-%m-%d",time.localtime())+'沒有任何持股變動'
        data = { 'message': message }
        requests.post("https://notify-api.line.me/api/notify", headers = headers, data = data)
    
    for i in record:
    
        if float(i['quantity'])>0:
            message = time.strftime("%Y-%m-%d",time.localtime())+' 買進 股票代號： '+i['stock_id']+' ，共 '+str(int(float(i['quantity'])*1000))+' 股'
            data = { 'message': message }
            requests.post("https://notify-api.line.me/api/notify", headers = headers, data = data)
            
        else:
            message = time.strftime("%Y-%m-%d",time.localtime())+' 賣出 股票代號： '+i['stock_id']+' ，共 '+str(int(abs(float(i['quantity'])*1000)))+' 股'
            data = { 'message': message }
            requests.post("https://notify-api.line.me/api/notify", headers = headers, data = data)
    
    key_list = [f'order{i}:' for i in range(1,len(record)+1)]
    value_list = [{i['stock_id']:i['quantity']} for i in record]
    time.sleep(10) #Fugle限制兩次之間要間隔十秒
    # 實際下單（會真的下單，初次使用建議收市時測試）
    order_executer.create_orders(market_order=False) #用市價單(要注意滑價，可自行修改) #FUGLE第三次
    
    message = '以上委託，下單完成'
    data = { 'message': message }
    requests.post("https://notify-api.line.me/api/notify", headers = headers, data = data)

   

def setting_schedule(job,setting_time='10:30'):
    # 設定每周一到五，每天的幾點執行本程式
    schedule.every().monday.at(setting_time).do(job)
    schedule.every().tuesday.at(setting_time).do(job)
    schedule.every().wednesday.at(setting_time).do(job)
    schedule.every().thursday.at(setting_time).do(job)
    schedule.every().friday.at(setting_time).do(job)

if __name__=='__main__':
    acc_config, order_config = read_config()

    for i in acc_config:
        globals()[i]=acc_config[i]


    for i in order_config:
        globals()[i]=order_config[i]


    if finlab_api_token == '':
        try:
            from strategy import get_position_from_GCP
        except:
            print('請輸入Finlab的vip token,並重新啟動程式')

    vol_limitation = float(vol_limitation)
    fund = float(fund)
    odd_limitation = float(odd_limitation)
    trade_buffer = float(trade_buffer)


    #將讀取設定檔後將憑證的路徑寫入
    config = configparser.ConfigParser()
    config.read(FUGLE_CONFIG_PATH)
    config.set('Cert','Path',FUGLE_CERT_PATH)
    with open(FUGLE_CONFIG_PATH, 'w') as f:
        config.write(f)

    #當執行程式的時候，根據當下的時間
        
    #根據設定檔中的交易時間設定每天的交易時間
    setting_schedule(job,trade_time)
    #執行檔案的時候會根據當下的時間判斷是否要執行程式，如果時間在9:30~13:30之間，則會執行程式
    now = datetime.now()
    now_time = now.strftime("%H:%M")
    if now_time >= '09:30' and now_time <= '13:30':
        job()

    # 進入主迴圈
    while True:
        schedule.run_pending()
        time.sleep(1)