import telebot
import re

# Bot Token ကို ဒီမှာထည့်ပါ
TOKEN = '8312775918:AAHXlFdKDveQjNaZSckB03dNidv7IGEANWk'
bot = telebot.TeleBot(TOKEN)

def calculate_bet(text):
    text = text.lower()
    
    # 1. Market % သတ်မှတ်ခြင်း
    cashback_rate = 0.07  # Default 7%
    if any(word in text for word in ['mm']):
        cashback_rate = 0.10
    elif any(word in text for word in ['global', 'ဂလို', 'glo']):
        cashback_rate = 0.03

    lines = text.split('\n')
    grand_total = 0

    for line in lines:
        if not line.strip(): continue
        
        # Amount ရှာခြင်း (စာကြောင်းအဆုံးက ဂဏန်း)
        amounts = re.findall(r'(\d+)$', line.strip())
        if not amounts: continue
        amount = int(amounts[0])

        line_total = 0
        
        # --- Keywords Logic ---
        
        # ခွေ (Normal)
        if any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            n = len(set(nums))
            line_total += (n * (n - 1)) * amount
            
        # အပူးပါခွေ
        elif any(x in line for x in ['ပူး', 'အပူးပါ', 'ခွေပူး', 'အခွေပူး', 'အပူးအပြီးပါ']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            n = len(set(nums))
            line_total += (n * n) * amount

        # ပတ်သီး (19 ကွက်)
        elif any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            line_total += (len(nums) * 19) * amount

        # ပတ်ပူးပို (20 ကွက်)
        elif any(x in line for x in ['ပတ်ပူး', 'ပူးပို', 'ပတ်အကွက်20']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            line_total += (len(nums) * 20) * amount

        # ထိပ်စီး / အပိတ် (10 ကွက်)
        elif any(x in line for x in ['ထိပ်စီး', 'ထိပ်', 'top', 't', 'အပိတ်', 'ပိတ်', 'ပ', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            line_total += (len(nums) * 10) * amount

        # ဘရိတ် (10 ကွက်)
        elif any(x in line for x in ['ဘရိတ်', 'bk']):
            nums = re.findall(r'\d', line.split(amounts[0])[0])
            line_total += (len(nums) * 10) * amount

        # အကပ်
        elif any(x in line for x in ['ကပ်', 'ကို']):
            parts = re.split(r'ကပ်|ကို', line.split(amounts[0])[0])
            if len(parts) >= 2:
                a = len(re.findall(r'\d', parts[0]))
                b = len(re.findall(r'\d', parts[1]))
                res = (a * b) * amount
                line_total += (res * 2) if 'r' in line else res

        # ဒဲ့ / R
        else:
            # ဂဏန်းအတွဲများထုတ်ယူခြင်း (ဥပမာ 12, 34)
            pairs = re.findall(r'\d{2}', line.split(amounts[0])[0])
            if pairs:
                res = len(pairs) * amount
                line_total += (res * 2) if 'r' in line else res
            
        grand_total += line_total

    return grand_total, cashback_rate

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        total, rate = calculate_bet(message.text)
        if total == 0: return

        cashback = total * rate
        net_total = total - cashback
        
        response = (
            f"👤 {message.from_user.first_name}\n"
            f"Total = {total:,.0f} ကျပ်\n"
            f"{int(rate*100)}% Cash Back = {cashback:,.0f} ကျပ်\n"
            f"Net Total = {net_total:,.0f} ကျပ် ပဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ 🍀"
        )
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Error: {e}")

bot.infinity_polling()
