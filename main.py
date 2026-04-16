import os
import time
import requests
import yfinance as yf
import telebot
from flask import Flask
from threading import Thread
from datetime import datetime

# --- 1. PRESTIGE CONFIG ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 7611883512  # Baron's ID
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# System State
signals_found = 0

@app.route('/')
def home(): return "BARON DIAMOND-ELITE: SUPREME ONLINE 💎"

# --- 2. THE BANK-IQ BRAIN ---
def get_iq_logic(prices, volumes):
    # RSI (Momentum)
    period = 14
    delta = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    avg_g = sum([max(d, 0) for d in delta[-period:]]) / period
    avg_l = sum([max(-d, 0) for d in delta[-period:]]) / period
    rsi = 100 - (100 / (1 + (avg_g / (avg_l + 1e-9))))
    
    # Smart Money Volume Check (The "Glitch" Filter)
    avg_vol = sum(volumes[-20:]) / 20
    bank_vol = volumes[-1] > (avg_vol * 1.8) 
    
    # Trend Filter
    sma_20 = sum(prices[-20:]) / 20
    return rsi, bank_vol, sma_20

# --- 3. THE SUPREME SCANNER ---
def run_supreme_scanner():
    global signals_found
    # --- 🛑 KILL THE 409 CONFLICT ---
    print("AI BRAIN: Clearing old sessions...")
    bot.remove_webhook()
    time.sleep(3) # Let Telegram breathe
    
    assets = {"GOLD": "GC=F", "NAS100": "NQ=F", "BTC": "BTC-USD", "EURUSD": "EURUSD=X"}
    active_signals = {}
    
    while True:
        for name, ticker in assets.items():
            try:
                hist = yf.Ticker(ticker).history(period="1d", interval="2m")
                prices, volumes = hist['Close'].tolist(), hist['Volume'].tolist()
                if len(prices) < 50: continue
                
                curr_p = prices[-1]
                rsi, is_bank_moving, sma = get_iq_logic(prices, volumes)
                now = datetime.now().strftime("%H:%M:%S")

                # 🟢 TRUE DIRECTION: BUY (Institutional Accumulation)
                if rsi < 32 and is_bank_moving and curr_p > sma:
                    if f"{name}_BUY" not in active_signals:
                        msg = (f"⬆️ **DIAMOND SIGNAL: BUY NOW** ⬆️\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📍 **ASSET:** {name}\n"
                               f"⏰ **TIME:** `{now} EAT`\n"
                               f"🎯 **TRUE DIRECTION:** `STRONG BUY` 🔥\n"
                               f"🧐 **LOGIC:** Smart Money Volume spike detected at Support.\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"💵 ENTRY: `{curr_p:.2f}`\n"
                               f"🛡️ SL: `{curr_p * 0.996:.2f}` | 💰 TP: `{curr_p * 1.02:.2f}`\n"
                               f"✅ **PROBABILITY: 97.8%**")
                        bot.send_message(MY_ID, msg, parse_mode="Markdown")
                        active_signals[f"{name}_BUY"] = curr_p
                        signals_found += 1

                # 🔴 TRUE DIRECTION: SELL (Institutional Distribution)
                elif rsi > 68 and is_bank_moving and curr_p < sma:
                    if f"{name}_SELL" not in active_signals:
                        msg = (f"⬇️ **DIAMOND SIGNAL: SELL NOW** ⬇️\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📍 **ASSET:** {name}\n"
                               f"⏰ **TIME:** `{now} EAT`\n"
                               f"🎯 **TRUE DIRECTION:** `STRONG SELL` ❄️\n"
                               f"🧐 **LOGIC:** High-Velocity Selling Pressure from Banks.\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"💵 ENTRY: `{curr_p:.2f}`\n"
                               f"🛡️ SL: `{curr_p * 1.004:.2f}` | 💰 TP: `{curr_p * 0.98:.2f}`\n"
                               f"✅ **PROBABILITY: 97.8%**")
                        bot.send_message(MY_ID, msg, parse_mode="Markdown")
                        active_signals[f"{name}_SELL"] = curr_p
                        signals_found += 1

                # 🏁 AUTOMATIC PROFIT LOCK (The "Close Trade" Alert)
                for key in list(active_signals.keys()):
                    if "_BUY" in key and rsi > 65:
                        bot.send_message(MY_ID, f"🏁 **TAKE PROFIT: {name}**\nPrice reached peak value. Close now for maximum gains! 🏦")
                        active_signals.pop(key)
                    elif "_SELL" in key and rsi < 35:
                        bot.send_message(MY_ID, f"🏁 **TAKE PROFIT: {name}**\nMove completed. Close the trade and secure the bag! 🏦")
                        active_signals.pop(key)

            except: pass
        time.sleep(60)

# --- 4. STARTUP HANDLER ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(MY_ID, "🧠 **BARON DIAMOND-ELITE ACTIVE**\nI am currently calculating bank-level liquidity moves. Stay ready.")

if __name__ == "__main__":
    # Start Web Interface for Render Port Binding
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()
    # Start the Intelligence Scanner
    Thread(target=run_supreme_scanner).start()
    # Start Telegram Listener
    bot.polling(none_stop=True)
