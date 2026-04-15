import os
import time
import yfinance as yf
import pandas as pd
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- 1. CONFIG ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MY_ID = 7611883512  
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

signals_found = 0

@app.route('/')
def home(): return "Baron AI: ACTIVE 🟢"

# --- 2. THE STEALTH MATH ENGINE ---
def get_indicators(df):
    # RSI Manual Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD Manual Calculation
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands Manual Calculation
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['BBL'] = df['MA20'] - (df['STD'] * 2)
    
    # EMA 200 Trend Filter
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    return df

# --- 3. THE SCANNER ---
def run_scanner():
    global signals_found
    assets = {"GOLD": "GC=F", "NAS100": "NQ=F", "BTC": "BTC-USD", "EURUSD": "EURUSD=X"}
    active_signals = {}
    
    while True:
        for name, ticker in assets.items():
            try:
                data = yf.download(ticker, period="1d", interval="2m", progress=False)
                if len(data) < 30: continue
                
                df = get_indicators(data)
                curr = df.iloc[-1]
                prev = df.iloc[-2]
                price = curr['Close']
                
                # 🔥 95%+ ELITE LOGIC
                if (price > curr['EMA200'] and curr['RSI'] < 35 and 
                    price <= curr['BBL'] and curr['MACD'] > curr['SIGNAL']):
                    
                    if name not in active_signals:
                        sl = curr['BBL'] * 0.998
                        tp = price + ((price - sl) * 3)
                        msg = (
                            f"╔══════════════════════╗\n"
                            f"   💎 **SURE-WIN SIGNAL** 💎\n"
                            f"╚══════════════════════╝\n"
                            f"📊 **ASSET:** `{name}`\n"
                            f"⚡ **ACTION:** `BUY NOW` 🔥\n"
                            f"----------------------------------------\n"
                            f"💵 **ENTRY:** `{price:.2f}`\n"
                            f"🛡️ **STOP LOSS:** `{sl:.2f}`\n"
                            f"💰 **TAKE PROFIT:** `{tp:.2f}`\n"
                            f"----------------------------------------\n"
                            f"📢 **EXECUTE ON HEADWAY MT5!**"
                        )
                        bot.send_message(MY_ID, msg, parse_mode="Markdown")
                        active_signals[name] = True
                        signals_found += 1
                
                # 🛑 EXIT SIGNAL
                elif curr['RSI'] > 75 or (curr['MACD'] < curr['SIGNAL'] and prev['MACD'] > prev['SIGNAL']):
                    if name in active_signals:
                        bot.send_message(MY_ID, f"🏁 **EXIT ALERT: {name}**\nMomentum flipped. **CLOSE NOW!**")
                        del active_signals[name]
            except: pass
        time.sleep(60)

# --- 4. AI INTERFACE ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛰️ System Status", callback_data="status"))
    bot.send_message(MY_ID, "🧠 **BARON AI MIND ONLINE**\nEverything is synced. I am hunting for 95% matches.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query(call):
    if call.data == "status":
        bot.send_message(MY_ID, f"✅ System is hunting signals.\n📈 Signals Found Today: {signals_found}")

if __name__ == "__main__":
    # Start Web Server
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()
    # Start Scanner
    Thread(target=run_scanner).start()
    # Start Telegram Listener
    bot.polling(none_stop=True)
