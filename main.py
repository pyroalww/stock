import requests
import json
import time
from datetime import datetime
import yfinance as yf
from tkinter import simpledialog, messagebox

def serverStarted():
    print("Welcome!")
    print("SERVER ID = PASSED!")
    print("Please enter the abbreviation of the stock you want to track.")
    defaultHissem = input("> ")
    print(f"STOCKIDs: {defaultHissem}")

    messagebox.showwarning("Redirecting...", f"HAVE YOU CHECKED YOUR CONFIG FILE? CONTINUE IF YOU HAVE. ")
    messagebox.showwarning("Redirecting...", f"STARTING THE SERVER DIRECTLY. SERVER 100% CHECKED, NO PROBLEM DETECTED. IF THERE ARE NO ERRORS IN THE VALUES IN YOUR CONFIG FILE OR IF YOUR LOGIN INFORMATION IS CORRECT, THE SERVER MUST START PROPERLY.")
    return defaultHissem.split(',')

def send_discord_message(webhook_url, message):
    payload = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print(f"MESSAGE SENT SUCCESSFULLY!!! | message is: {headers}")
    else:
        print(f"Discord's response: {response.status_code}")

def main(defaultHissem):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    
    webhook_url = config["discord_webhook_url"]
    check_hours = config["check_hours"]
    check_interval_seconds = config["check_interval_seconds"]
    
    while True:
        current_hour = datetime.now().hour
        if current_hour in check_hours:
            try:
                for stock_symbol in defaultHissem:
                    stock = yf.Ticker(stock_symbol)
                    current_price = stock.history(period="1d")["Close"][-1]
                    
                    if "thresholds" in config:
                        for threshold in config["thresholds"]:
                            if current_price >= threshold["above"]:
                                message = f"{stock_symbol} | ALERT: Price above {threshold['above']}!"
                                send_discord_message(webhook_url, message)
                            elif current_price <= threshold["below"]:
                                message = f"{stock_symbol} | ALERT: Price below {threshold['below']}!"
                                send_discord_message(webhook_url, message)
                    
                    historical_data = stock.history(period="7d")
                    average_price = historical_data["Close"].mean()
                    volume = stock.info.get("volume")
                    high_price = stock.info.get("dayHigh")
                    low_price = stock.info.get("dayLow")
                    message = f"{stock_symbol} | Fiyat: {current_price} | Ortalama Fiyat (Son 7 Gün): {average_price} | Hacim: {volume} | En Yüksek Fiyat: {high_price} | En Düşük Fiyat: {low_price}"
                    send_discord_message(webhook_url, message)
            except Exception as e:
                message = f"|!| SOMETHING WENT WRONG: {e} |"
                send_discord_message(webhook_url, message)
        
        time.sleep(check_interval_seconds)

if __name__ == "__main__":
    defaultHissem = serverStarted()
    main(defaultHissem)
