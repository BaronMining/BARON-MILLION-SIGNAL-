import os
import time
import yfinance as yf
import telebot
from flask import Flask
from threading import Thread

# --- 1. CONFIG ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 7611883512  
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "Baron AI: Invincible Mode 🟢"

# --- 2. RAW MATH ENGINE (No Pandas/NumPy Needed) ---
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- 3. THE SCANNER ---
def run_scanner():
    assets = {"GOLD": "GC=F", "NAS100": "NQ=F", "BTC": "BTC-USD", "EURUSD": "EURUSD=X"}
    active_signals = {}
    
    while True:
        for name, ticker in assets.items():
            try:
                # Fetching raw data
                ticker_data = yf.Ticker(ticker)
                hist = ticker_data.history(period="1d", interval="2m")
                prices = hist['Close'].tolist()
                
                if len(prices) < 20: continue
                
                # Logic: Simple Trend + RSI
                current_price = prices[-1]
                rsi = calculate_rsi(prices)
                sma_20 = sum(prices[-20:]) / 20
                
                # 🔥 SIGNAL: Price below average (Dip) + RSI Oversold
                if current_price < sma_20 and rsi < 30:
                    if name not in active_signals:
                        sl = current_price * 0.995
                        tp = current_price * 1.01
                        msg = (f"╔══════════════════╗\n"
                               f"   💎 **SURE-WIN: {name}**\n"
                               f"╚══════════════════╝\n"
                               f"⚡ **ACTION:** BUY NOW\n"
                               f"💵 **PRICE:** {current_price:.2f}\n"
                               f"🛡️ **SL:** {sl:.2f} | 💰 **TP:** {tp:.2f}\n"
                               f"📢 **EXECUTE ON MT5!**")
                        bot.send_message(MY_ID, msg)
                        active_signals[name] = True
                
                elif rsi > 70 and name in active_signals:
                    bot.send_message(MY_ID, f"🏁 **EXIT {name}** - Take Profit Now!")
                    del active_signals[name]
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()
    Thread(target=run_scanner).start()
    bot.polling(none_stop=True)
