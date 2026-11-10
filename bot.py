import time
import requests
import threading
import telebot

API_TOKEN = '9206817833:AAHevTI01841ZdC4b0nEwZ7U_u7AoBOfdTc'
CHANNEL_ID = '@lottery875'

bot = telebot.TeleBot(API_TOKEN)
is_running = True

raw_pattern = "SSSBSBSBBBBSSB"
SIGNAL_PATTERN = [ "SMALL" if char.upper() == 'S' else "BIG" for char in raw_pattern ]
pattern_index = 0

current_step = 1
max_step = 10

API_URL = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"

def fetch_and_send_signals():
    global pattern_index, current_step
    sent_issues = set()
    
    while is_running:
        try:
            params = {'ts': int(time.time() * 1000)}
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(API_URL, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                item_list = data.get('data', {}).get('list', [])
                
                if len(item_list) > 1:
                    latest_item = item_list[0]
                    current_issue = int(latest_item.get('issueNumber', 0))
                    result_num = int(latest_item.get('number', 0))
                    
                    if current_issue and current_issue not in sent_issues:
                        sent_issues.add(current_issue)
                        
                        actual_result_type = "SMALL" if result_num <= 4 else "BIG"
                        current_bet_type = SIGNAL_PATTERN[pattern_index]
                        
                        is_win = (current_bet_type == actual_result_type)
                        status_icon = "✅" if is_win else "❌"
                        
                        if is_win:
                            current_step = 1
                        else:
                            current_step += 1
                            if current_step > max_step:
                                current_step = 1
                        
                        pattern_index = (pattern_index + 1) % len(SIGNAL_PATTERN)
                        
                        next_issue = current_issue + 1
                        next_bet_type = SIGNAL_PATTERN[pattern_index]
                        next_multiplier = f"x{current_step}"
                        
                        signal_message = (
                            f"┌── 🥇 TRX SIGNAL ──┐\n"
                            f"📌 Finished : `{current_issue}`\n"
                            f"Result : {result_num} {status_icon}\n"
                            f"--------------------\n"
                            f"👉 **Next Bet**\n"
                            f"Issue : `{next_issue}`\n"
                            f"Bet : {next_bet_type} {next_multiplier}\n"
                            f"└──────────────────┘"
                        )
                        
                        bot.send_message(CHANNEL_ID, signal_message, parse_mode="Markdown")
            
        except Exception as e:
            print(f"API Error: {e}")
            
        time.sleep(10)

if __name__ == '__main__':
    print("Cloud Martingale Bot is starting...")
    threading.Thread(target=fetch_and_send_signals).start()
    bot.infinity_polling()
