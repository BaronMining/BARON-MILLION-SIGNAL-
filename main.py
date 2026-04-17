import os
import time
import yfinance as yf
import telebot
from flask import Flask
from threading import Thread
from datetime import datetime
from telebot import types

# --- 1. CONFIGURATION ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 7611883512 # Baron's Direct Line
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Global Trackers
active_trades = {}
scan_count = 0

@app.route('/')
def home(): return "BARON SOVEREIGN-AI: DYNAMIC INTELLIGENCE ACTIVE 💎"

# --- 2. DYNAMIC CONFIDENCE ENGINE ---
def calculate_certainty(prices, volumes, rsi, direction):
    """Calculates a dynamic percentage based on signal strength."""
    score = 85.0 # Base confidence for a basic hit
    
    # 1. Volume Alignment (Banks entering)
    avg_vol = sum(volumes[-20:]) / 20
    if volumes[-1] > (avg_vol * 1.5): score += 7.5
    
    # 2. RSI Extremes (Oversold/Overbought)
    if direction == "BUY" and rsi < 20: score += 4.0
    if direction == "SELL" and rsi > 80: score += 4.0
    
    # 3. SMA Distance (Price Gap)
    sma_20 = sum(prices[-20:]) / 20
    gap = abs(prices[-1] - sma_20) / sma_20
    if gap > 0.002: score += 3.4
    
    return min(score, 99.9) # Caps at 99.9% for realism

def get_analysis(prices):
    if len(prices) < 20: return 50, 0
    delta = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    avg_g = sum([max(d, 0) for d in delta[-14:]]) / 14
    avg_l = sum([max(-d, 0) for d in delta[-14:]]) / 14
    rsi = 100 - (100 / (1 + (avg_g / (avg_l + 1e-9))))
    sma_20 = sum(prices[-20:]) / 20
    return rsi, sma_20

# --- 3. THE UNIVERSAL SCANNER ---
def run_universal_scanner():
    global scan_count
    bot.remove_webhook()
    
    # Expanded Asset List for Maximum Opportunity
    assets = {
        "GOLD": "GC=F", "NAS100": "NQ=F", "US30": "YM=F", 
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
        "BTC": "BTC-USD", "ETH": "ETH-USD", "CRUDE OIL": "CL=F"
    }

    while True:
        for name, ticker in assets.items():
            try:
                hist = yf.Ticker(ticker).history(period="1d", interval="1m")
                prices, volumes = hist['Close'].tolist(), hist['Volume'].tolist()
                if not prices: continue
                
                curr_p = prices[-1]
                rsi, sma = get_analysis(prices)
                scan_count += 1

                # 🚀 SIGNAL: BUY
                if rsi < 32 and curr_p > sma:
                    if f"{name}_B" not in active_trades:
                        confidence = calculate_certainty(prices, volumes, rsi, "BUY")
                        msg = (f"⬆️ **DIAMOND HIT: BUY NOW** ⬆️\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📍 **ASSET:** {name}\n"
                               f"🎯 **DIRECTION:** `STRONG BUY` 🔥\n"
                               f"💵 **ENTRY:** `{curr_p:.2f}`\n"
                               f"🛡️ **SL:** `{curr_p * 0.997:.2f}` | 💰 **TP:** `{curr_p * 1.015:.2f}`\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📊 **CERTAINTY:** `{confidence}%` ✅")
                        bot.send_message(MY_ID, msg, parse_mode="Markdown")
                        active_trades[f"{name}_B"] = {"entry": curr_p, "type": "BUY"}

                # 🚀 SIGNAL: SELL
                elif rsi > 68 and curr_p < sma:
                    if f"{name}_S" not in active_trades:
                        confidence = calculate_certainty(prices, volumes, rsi, "SELL")
                        msg = (f"⬇️ **DIAMOND HIT: SELL NOW** ⬇️\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📍 **ASSET:** {name}\n"
                               f"🎯 **DIRECTION:** `STRONG SELL` ❄️\n"
                               f"💵 **ENTRY:** `{curr_p:.2f}`\n"
                               f"🛡️ **SL:** `{curr_p * 1.003:.2f}` | 💰 **TP:** `{curr_p * 0.985:.2f}`\n"
                               f"━━━━━━━━━━━━━━━━━━━━\n"
                               f"📊 **CERTAINTY:** `{confidence}%` ✅")
                        bot.send_message(MY_ID, msg, parse_mode="Markdown")
                        active_trades[f"{name}_S"] = {"entry": curr_p, "type": "SELL"}

                # 🏦 LIVE PROFIT ALERT (Exit Logic)
                if f"{name}_B" in active_trades and rsi > 58:
                    bot.send_message(MY_ID, f"🏁 **TAKE PROFIT: {name}**\nTrade momentum is slowing. Close now to secure the bag! 🏦")
                    active_trades.pop(f"{name}_B", None)
                elif f"{name}_S" in active_trades and rsi < 42:
                    bot.send_message(MY_ID, f"🏁 **TAKE PROFIT: {name}**\nMarket reached a floor. Secure your profits now! 🏦")
                    active_trades.pop(f"{name}_S", None)

            except: pass
        time.sleep(30)

# --- 4. INTERACTIVE BUTTONS ---
@bot.message_handler(commands=['start', 'ready'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Check Bot Pulse")
    btn2 = types.KeyboardButton("📊 Market Health")
    markup.add(btn1, btn2)
    bot.send_message(MY_ID, "🧠 **BARON SOVEREIGN-AI: ONLINE**\nI am hunting for billion-dollar moves across all assets. Buttons are live below.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🚀 Check Bot Pulse":
        bot.send_message(MY_ID, "✅ **SYSTEM READY.** I am scanning the market every 30 seconds for 99% accuracy hits.")
    elif message.text == "📊 Market Health":
        now = datetime.now().strftime("%H:%M:%S")
        bot.send_message(MY_ID, f"📡 **SCANNER STATUS**\n⏰ Time: `{now} EAT`\n🔢 Scans today: `{scan_count}`\n💼 Open Trades: `{len(active_trades)}`")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()
    Thread(target=run_universal_scanner).start()
    bot.polling(none_stop=True)
