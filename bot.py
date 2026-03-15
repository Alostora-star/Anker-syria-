#!/usr/bin/env python3
"""
🛒 Anker Syria - نظام إدارة مبيعات متكامل
Telegram Bot - python-telegram-bot v21+
"""

import json, os, logging, threading, time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ═══════════════════════════════════════════════
#  ⚙️  إعدادات
# ═══════════════════════════════════════════════
BOT_TOKEN  = "8739257029:AAHpyXVTdn7r8Nq_R6op-UDw6yG4z-3OeN8"
ADMIN_IDS  = [7524378240]
DATA_FILE  = "bot_data.json"
# ضع رابط السيرفس بعد النشر على Render هنا، مثال:
# RENDER_URL = "https://anker-syria-bot.onrender.com"
RENDER_URL = os.environ.get("RENDER_URL", "")

# ═══════════════════════════════════════════════
#  🌐  Keep-Alive — يمنع نوم Render
# ═══════════════════════════════════════════════
class _PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Anker Syria Bot is alive!")
    def log_message(self, *args): pass

def _run_http_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), _PingHandler).serve_forever()

def _self_ping():
    if not RENDER_URL:
        logging.warning("RENDER_URL not set — self-ping disabled")
        return
    time.sleep(30)
    while True:
        try:
            urllib.request.urlopen(RENDER_URL, timeout=10)
            logging.info(f"💓 Keep-alive ping OK")
        except Exception as e:
            logging.warning(f"💔 Ping failed: {e}")
        time.sleep(14 * 60)

# ═══════════════════════════════════════════════
#  📦  قاعدة المنتجات
# ═══════════════════════════════════════════════
PRODUCTS = {
    "cable_1":  {"name": "Anker 322 Cable USB-C To Lightning 1M",      "category": "cable",     "price_usd": 14},
    "cable_2":  {"name": "Zolo USB-C to USB-C 240W 1M Cable",          "category": "cable",     "price_usd": 10},
    "cable_3":  {"name": "Anker 322 Cable USB-A To USB-C 1M",          "category": "cable",     "price_usd": 7},
    "cable_4":  {"name": "Anker 322 Cable USB-C To USB-C 1M",          "category": "cable",     "price_usd": 7},
    "cable_5":  {"name": "Zolo USB-C to USB-C 240W 2M Cable",          "category": "cable",     "price_usd": 10},
    "chrg_1":   {"name": "Anker 20W Zolo Charger",                     "category": "charger",   "price_usd": 9},
    "chrg_2":   {"name": "Anker 312 30W Charger",                      "category": "charger",   "price_usd": 12},
    "chrg_3":   {"name": "Anker 25W Charger + USB-C Cable",            "category": "charger",   "price_usd": 15},
    "chrg_4":   {"name": "Anker 45W Nano Charger + C to C Cable",      "category": "charger",   "price_usd": 30},
    "chrg_5":   {"name": "Anker 715 Nano Charger 65W",                 "category": "charger",   "price_usd": 28},
    "chrg_6":   {"name": "Anker Car Charger 30W 2-Port + Cables",      "category": "charger",   "price_usd": 25},
    "chrg_7":   {"name": "Anker 75W USB-C Car Charger",                "category": "charger",   "price_usd": 30},
    "chrg_8":   {"name": "Anker Charger 140W 4-Port + USB-C Cable",    "category": "charger",   "price_usd": 65},
    "chrg_9":   {"name": "Anker 313 Charger 45W",                      "category": "charger",   "price_usd": 23},
    "chrg_10":  {"name": "Anker PowerPort III 3-Port 65W",             "category": "charger",   "price_usd": 33},
    "hp_1":     {"name": "Anker Soundcore Space One Pro",              "category": "headphone", "price_usd": 118},
    "hp_2":     {"name": "Anker Soundcore Q20i",                       "category": "headphone", "price_usd": 38},
    "hp_3":     {"name": "Anker Soundcore H30i",                       "category": "headphone", "price_usd": 25},
    "hp_4":     {"name": "Anker Soundcore Q11",                        "category": "headphone", "price_usd": 25},
    "hp_5":     {"name": "Anker Soundcore Q30i",                       "category": "headphone", "price_usd": 60},
    "hp_6":     {"name": "Anker Soundcore Space Q45",                  "category": "headphone", "price_usd": 95},
    "eb_1":     {"name": "Anker Soundcore R50i",                       "category": "earbud",    "price_usd": 15},
    "eb_2":     {"name": "Anker Soundcore A20i",                       "category": "earbud",    "price_usd": 15},
    "eb_3":     {"name": "Anker Soundcore Liberty 4 Pro",              "category": "earbud",    "price_usd": 85},
    "eb_4":     {"name": "Anker Soundcore Liberty 5",                  "category": "earbud",    "price_usd": 65},
    "eb_5":     {"name": "Anker SoundCore C40i",                       "category": "earbud",    "price_usd": 52},
    "eb_6":     {"name": "Anker Soundcore P41i",                       "category": "earbud",    "price_usd": 56},
    "eb_7":     {"name": "Anker Soundcore R50i NC",                    "category": "earbud",    "price_usd": 25},
    "eb_8":     {"name": "Anker Soundcore Liberty 4 NC",               "category": "earbud",    "price_usd": 48},
    "eb_9":     {"name": "Anker SoundCore V20",                        "category": "earbud",    "price_usd": 22},
    "eb_10":    {"name": "Anker Soundcore Life U2i",                   "category": "earbud",    "price_usd": 14},
    "pw_1":     {"name": "Anker Nano Power Bank 22.5W Built-In USB-C", "category": "power",     "price_usd": 26},
    "pw_2":     {"name": "Anker Zolo 10K 30W Built-In USB-C Cable",    "category": "power",     "price_usd": 27},
    "pw_3":     {"name": "Anker Zolo PowerBank 20K 22.5W 90 Cable",   "category": "power",     "price_usd": 32},
    "pw_4":     {"name": "Anker Zolo Power Bank 25000mAh 165W",        "category": "power",     "price_usd": 77},
    "pw_5":     {"name": "Anker 548 Power Bank PowerCore 192Wh",       "category": "power",     "price_usd": 123},
    "pw_6":     {"name": "Anker Solix C200 Power Bank",                "category": "power",     "price_usd": 160},
    "pw_7":     {"name": "Anker MagGo Power Bank 10K 15W",             "category": "power",     "price_usd": 61},
    "pw_8":     {"name": "Anker 335 Power Drive 67W",                  "category": "power",     "price_usd": 22},
    "pw_9":     {"name": "Anker 533 Nano Power Bank 30W Built-In USB-C","category": "power",    "price_usd": 38},
    "pw_10":    {"name": "Anker MagGo Power Bank 10K 35W Apple Watch", "category": "power",     "price_usd": 38},
    "sp_1":     {"name": "Anker Soundcore Boom 3i",                    "category": "speaker",   "price_usd": 85},
    "sp_2":     {"name": "Anker Soundcore Rave 3S",                    "category": "speaker",   "price_usd": 275},
    "sp_3":     {"name": "Anker Soundcore Select 4Go",                 "category": "speaker",   "price_usd": 25},
    "eufy_1":   {"name": "Anker Eufy Security Indoor Cam C220",        "category": "eufy",      "price_usd": 33},
    "eufy_2":   {"name": "Anker Eufy Video Doorbell C30",              "category": "eufy",      "price_usd": 55},
    "hub_1":    {"name": "Anker 5-in-1 USB-C Hub",                     "category": "hub",       "price_usd": 35},
}

CATEGORIES = {
    "cable":     {"label": "كابلات",         "emoji": "🔌"},
    "charger":   {"label": "شواحن",          "emoji": "⚡"},
    "headphone": {"label": "سماعات رأس",      "emoji": "🎧"},
    "earbud":    {"label": "إيرباد لاسلكي",   "emoji": "🎵"},
    "power":     {"label": "بنك الطاقة",      "emoji": "🔋"},
    "speaker":   {"label": "سبيكر",          "emoji": "🔊"},
    "eufy":      {"label": "كاميرات Eufy",    "emoji": "📷"},
    "hub":       {"label": "هاب USB",         "emoji": "💻"},
}

# ═══════════════════════════════════════════════
#  💾  قاعدة البيانات
# ═══════════════════════════════════════════════
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "exchange_rate": 14000,
        "users": {},
        "orders": [],
        "search_stats": {},
        "products": {},
        "favorites": {},
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════
#  🛠️  دوال مساعدة
# ═══════════════════════════════════════════════
def fmt_syp(price_usd, rate):
    return f"{price_usd * rate:,.0f}"

def is_admin(uid):
    return uid in ADMIN_IDS

def get_stock(pid, data):
    info = data.get("products", {}).get(pid, {})
    if "in_stock" in info and not info["in_stock"]:
        return 0
    return info.get("quantity", -1)

def stock_label(pid, data):
    q = get_stock(pid, data)
    if q == 0:  return "❌ نفذت"
    if q == -1: return "✅ متوفر"
    return f"✅ متوفر ({q} قطعة)"

def register_user(update, data):
    uid = str(update.effective_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "name":     update.effective_user.full_name,
            "username": update.effective_user.username or "",
            "joined":   datetime.now().isoformat()
        }
        save_data(data)

# ═══════════════════════════════════════════════
#  🎹  لوحات المفاتيح
# ═══════════════════════════════════════════════
def main_kb():
    return ReplyKeyboardMarkup([
        ["🛍️ تصفح الكتالوج",  "🔍 بحث سريع"],
        ["❤️ المفضلة",         "🛒 طلباتي"],
        ["📞 تواصل معنا",      "ℹ️ عن المتجر"],
    ], resize_keyboard=True)

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💱 تحديث سعر الصرف",    callback_data="admin_rate")],
        [InlineKeyboardButton("📦 إدارة المخزون",      callback_data="admin_stock_p1")],
        [InlineKeyboardButton("📢 إرسال إعلان",        callback_data="admin_broadcast")],
        [InlineKeyboardButton("📋 آخر الطلبات",        callback_data="admin_orders")],
        [InlineKeyboardButton("📊 الإحصائيات",         callback_data="admin_stats")],
    ])

# ═══════════════════════════════════════════════
#  🚀  /start
# ═══════════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    register_user(update, data)
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"أهلاً وسهلاً {name}! 👋\n\n"
        "🎧 *متجر Anker Syria*\n"
        "الوكيل الرسمي لمنتجات Anker وSoundcore في سوريا\n\n"
        "اختر من القائمة أدناه 👇",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )

# ═══════════════════════════════════════════════
#  📂  الكتالوج
# ═══════════════════════════════════════════════
async def show_catalog(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for cid, cat in CATEGORIES.items():
        count = sum(1 for p in PRODUCTS.values() if p["category"] == cid)
        buttons.append([InlineKeyboardButton(
            f"{cat['emoji']} {cat['label']} ({count})",
            callback_data=f"cat_{cid}"
        )])
    await update.message.reply_text(
        "📂 *الكتالوج* — اختر التصنيف:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def cb_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cid  = q.data.replace("cat_", "")
    data = load_data()
    cat  = CATEGORIES.get(cid, {})
    items = {pid: p for pid, p in PRODUCTS.items() if p["category"] == cid}
    buttons = []
    for pid, p in items.items():
        sl = stock_label(pid, data)
        buttons.append([InlineKeyboardButton(
            f"{sl[:2]} {p['name'][:38]} — ${p['price_usd']}",
            callback_data=f"prod_{pid}"
        )])
    buttons.append([InlineKeyboardButton("🔙 رجوع للتصنيفات", callback_data="back_catalog")])
    await q.edit_message_text(
        f"{cat.get('emoji','')} *{cat.get('label','')}*\n"
        f"💱 سعر الصرف: {data['exchange_rate']:,} ل.س",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def back_catalog_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    buttons = []
    for cid, cat in CATEGORIES.items():
        count = sum(1 for p in PRODUCTS.values() if p["category"] == cid)
        buttons.append([InlineKeyboardButton(
            f"{cat['emoji']} {cat['label']} ({count})",
            callback_data=f"cat_{cid}"
        )])
    await q.edit_message_text(
        "📂 *الكتالوج* — اختر التصنيف:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ═══════════════════════════════════════════════
#  🏷️  تفاصيل المنتج
# ═══════════════════════════════════════════════
async def cb_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    pid  = q.data.replace("prod_", "")
    data = load_data()
    if pid not in PRODUCTS:
        await q.edit_message_text("المنتج غير موجود."); return

    p    = PRODUCTS[pid]
    rate = data["exchange_rate"]
    sl   = stock_label(pid, data)
    cat  = CATEGORIES.get(p["category"], {})
    uid  = str(q.from_user.id)
    favs = data.get("favorites", {}).get(uid, [])
    fav_btn = "💔 إزالة من المفضلة" if pid in favs else "❤️ أضف للمفضلة"

    text = (
        f"🛍️ *{p['name']}*\n\n"
        f"📂 التصنيف: {cat.get('emoji','')} {cat.get('label','')}\n"
        f"💵 السعر: *${p['price_usd']}*\n"
        f"💴 بالليرة: *{fmt_syp(p['price_usd'], rate)} ل.س*\n"
        f"📦 الحالة: {sl}\n"
        f"_(سعر الصرف: {rate:,} ل.س)_"
    )
    buttons = []
    if get_stock(pid, data) != 0:
        buttons.append([InlineKeyboardButton("🛒 اطلب الآن", callback_data=f"order_qty_{pid}")])
    buttons.append([InlineKeyboardButton(fav_btn, callback_data=f"fav_{pid}")])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"cat_{p['category']}")])
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

# ═══════════════════════════════════════════════
#  ❤️  المفضلة
# ═══════════════════════════════════════════════
async def cb_favorite(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    pid  = q.data.replace("fav_", "")
    data = load_data()
    uid  = str(q.from_user.id)
    data.setdefault("favorites", {})
    favs = data["favorites"].get(uid, [])
    if pid in favs:
        favs.remove(pid)
        msg = "💔 تمت الإزالة من المفضلة"
    else:
        favs.append(pid)
        msg = "❤️ تمت الإضافة للمفضلة!"
    data["favorites"][uid] = favs
    save_data(data)
    await q.answer(msg, show_alert=True)
    # تحديث صفحة المنتج
    q.data = f"prod_{pid}"
    await cb_product(update, ctx)

async def show_favorites(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid  = str(update.effective_user.id)
    favs = data.get("favorites", {}).get(uid, [])
    if not favs:
        await update.message.reply_text(
            "❤️ قائمة المفضلة فارغة!\nتصفح الكتالوج وأضف ما يعجبك.",
            reply_markup=main_kb()
        ); return
    rate    = data["exchange_rate"]
    buttons = []
    for pid in favs:
        if pid in PRODUCTS:
            p  = PRODUCTS[pid]
            sl = stock_label(pid, data)
            buttons.append([InlineKeyboardButton(
                f"{sl[:2]} {p['name'][:38]} — ${p['price_usd']}",
                callback_data=f"prod_{pid}"
            )])
    await update.message.reply_text(
        f"❤️ *مفضلتك* ({len(favs)} منتج)\n💱 سعر الصرف: {rate:,} ل.س",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ═══════════════════════════════════════════════
#  🛒  الطلب — اختيار الكمية
# ═══════════════════════════════════════════════
async def cb_order_qty(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    pid   = q.data.replace("order_qty_", "")
    data  = load_data()
    p     = PRODUCTS[pid]
    rate  = data["exchange_rate"]
    avail = get_stock(pid, data)
    max_q = 5 if avail == -1 else min(avail, 5)
    qty_row = [
        InlineKeyboardButton(str(i), callback_data=f"oconf_{pid}_{i}")
        for i in range(1, max_q + 1)
    ]
    buttons = [qty_row, [InlineKeyboardButton("🔙 رجوع", callback_data=f"prod_{pid}")]]
    await q.edit_message_text(
        f"🛒 *{p['name']}*\n\n"
        f"💵 سعر القطعة: ${p['price_usd']} | {fmt_syp(p['price_usd'], rate)} ل.س\n\n"
        f"📦 كم قطعة تريد؟",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def cb_order_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    # oconf_<pid>_<qty>  — pid قد يحتوي على _ فنفصل من اليمين
    parts = q.data.replace("oconf_", "").rsplit("_", 1)
    pid, qty = parts[0], int(parts[1])
    data = load_data()
    user = q.from_user
    p    = PRODUCTS[pid]
    rate = data["exchange_rate"]
    total_usd = p["price_usd"] * qty
    total_syp = fmt_syp(total_usd, rate)

    order = {
        "order_id":  len(data["orders"]) + 1,
        "user_id":   user.id,
        "user_name": user.full_name,
        "username":  user.username or "N/A",
        "product":   p["name"],
        "pid":       pid,
        "qty":       qty,
        "price_usd": p["price_usd"],
        "total_usd": total_usd,
        "total_syp": total_syp,
        "status":    "جديد",
        "time":      datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data["orders"].append(order)

    # تحديث الكمية إن كانت محددة
    avail = get_stock(pid, data)
    if avail > 0:
        data.setdefault("products", {}).setdefault(pid, {})
        new_qty = avail - qty
        data["products"][pid]["quantity"] = new_qty
        data["products"][pid]["in_stock"]  = new_qty > 0

    save_data(data)

    await q.edit_message_text(
        f"✅ *تم استقبال طلبك!*\n\n"
        f"🔢 رقم الطلب: *#{order['order_id']}*\n"
        f"📦 {p['name']}\n"
        f"🔢 الكمية: {qty} قطعة\n"
        f"💵 الإجمالي: ${total_usd} | {total_syp} ل.س\n\n"
        f"📞 سيتواصل معك فريقنا على واتساب:\n"
        f"*+963-940-902-808*",
        parse_mode="Markdown"
    )

    for aid in ADMIN_IDS:
        try:
            await ctx.bot.send_message(aid,
                f"🔔 *طلب جديد #{order['order_id']}*\n\n"
                f"👤 {user.full_name} (@{user.username or 'N/A'})\n"
                f"🆔 `{user.id}`\n"
                f"📦 {p['name']} x{qty}\n"
                f"💵 ${total_usd} | {total_syp} ل.س\n"
                f"🕐 {order['time']}",
                parse_mode="Markdown"
            )
        except Exception:
            pass

# ═══════════════════════════════════════════════
#  🛒  طلباتي
# ═══════════════════════════════════════════════
async def show_my_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data   = load_data()
    uid    = update.effective_user.id
    orders = [o for o in data["orders"] if o["user_id"] == uid]
    if not orders:
        await update.message.reply_text(
            "🛒 لا توجد طلبات سابقة بعد.", reply_markup=main_kb()
        ); return
    text = "🛒 *طلباتك الأخيرة:*\n\n"
    for o in orders[-5:][::-1]:
        text += (
            f"*#{o['order_id']}* — {o['product']}\n"
            f"  الكمية: {o['qty']} | ${o['total_usd']} | {o['status']}\n"
            f"  🕐 {o['time']}\n\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_kb())

# ═══════════════════════════════════════════════
#  🔍  البحث
# ═══════════════════════════════════════════════
async def search_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["mode"] = "search"
    await update.message.reply_text(
        "🔍 اكتب اسم المنتج أو الموديل:\n_(مثلاً: R50i، Liberty، 65W)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["🏠 الرئيسية"]], resize_keyboard=True)
    )

async def do_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q_text = update.message.text.strip().lower()
    data   = load_data()
    data["search_stats"][q_text] = data["search_stats"].get(q_text, 0) + 1
    save_data(data)
    results = {pid: p for pid, p in PRODUCTS.items() if q_text in p["name"].lower()}
    ctx.user_data["mode"] = None
    if not results:
        await update.message.reply_text(
            f"❌ لا توجد نتائج لـ «{q_text}»\nجرب كلمة أخرى.", reply_markup=main_kb()
        ); return
    buttons = []
    for pid, p in list(results.items())[:10]:
        sl = stock_label(pid, data)
        buttons.append([InlineKeyboardButton(
            f"{sl[:2]} {p['name'][:38]} — ${p['price_usd']}",
            callback_data=f"prod_{pid}"
        )])
    await update.message.reply_text(
        f"🔍 نتائج «{q_text}» ({len(results)} نتيجة):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ═══════════════════════════════════════════════
#  📞  تواصل + ℹ️ عن المتجر
# ═══════════════════════════════════════════════
async def contact_us(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 تواصل مع Anker Syria\n\n"
        "📱 واتساب: +963-940-902-808\n"
        "📸 إنستغرام: @AnkerSyria\n\n"
        "نسعد بخدمتك! 😊",
        reply_markup=main_kb()
    )

async def about_store(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    await update.message.reply_text(
        "🏪 *متجر Anker Syria*\n\n"
        "الوكيل الرسمي لمنتجات:\n"
        "• Anker — شواحن وكابلات\n"
        "• Soundcore — سماعات وسبيكر\n"
        "• Eufy — كاميرات أمنية\n\n"
        f"📦 إجمالي المنتجات: {len(PRODUCTS)}\n"
        f"💱 سعر الصرف: {data['exchange_rate']:,} ل.س / دولار",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )

# ═══════════════════════════════════════════════
#  👑  لوحة الأدمن
# ═══════════════════════════════════════════════
async def admin_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح."); return
    data = load_data()
    await update.message.reply_text(
        f"👑 *لوحة تحكم Anker Syria*\n\n"
        f"👥 المستخدمون: {len(data['users'])}\n"
        f"🛒 الطلبات: {len(data['orders'])}\n"
        f"💱 سعر الصرف: {data['exchange_rate']:,} ل.س",
        parse_mode="Markdown",
        reply_markup=admin_kb()
    )

async def admin_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_admin(q.from_user.id):
        await q.answer("⛔ غير مصرح.", show_alert=True); return
    await q.answer()
    act = q.data

    if act == "admin_rate":
        ctx.user_data["admin_action"] = "set_rate"
        await q.edit_message_text(
            "💱 أدخل سعر الصرف الجديد (ليرة/دولار)\nمثال: *14500*",
            parse_mode="Markdown"
        )

    elif act == "admin_stats":
        data = load_data()
        top  = sorted(data["search_stats"].items(), key=lambda x: x[1], reverse=True)[:5]
        top_txt = "\n".join([f"  • {k}: {v} مرة" for k, v in top]) or "لا يوجد"
        new_orders = sum(1 for o in data["orders"] if o.get("status") == "جديد")
        await q.edit_message_text(
            f"📊 *الإحصائيات*\n\n"
            f"👥 المستخدمون: {len(data['users'])}\n"
            f"🛒 إجمالي الطلبات: {len(data['orders'])}\n"
            f"🆕 طلبات جديدة: {new_orders}\n\n"
            f"🔍 أكثر ما بُحث عنه:\n{top_txt}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")
            ]])
        )

    elif act == "admin_broadcast":
        ctx.user_data["admin_action"] = "broadcast"
        await q.edit_message_text("📢 اكتب نص الإعلان — سيُرسل لجميع المستخدمين:")

    elif act == "admin_orders":
        data   = load_data()
        orders = data["orders"][-8:][::-1]
        if not orders:
            await q.edit_message_text(
                "لا توجد طلبات بعد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_back")]])
            ); return
        text = "📋 *آخر الطلبات:*\n\n"
        for o in orders:
            text += (
                f"*#{o['order_id']}* {o['status']} — {o['user_name']}\n"
                f"  📦 {o['product']} x{o['qty']}\n"
                f"  💵 ${o['total_usd']} | {o['time']}\n\n"
            )
        await q.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")
            ]])
        )

    elif act.startswith("admin_stock_p"):
        page  = int(act.replace("admin_stock_p", ""))
        data  = load_data()
        pids  = list(PRODUCTS.keys())
        per   = 8
        start_i = (page - 1) * per
        chunk = pids[start_i:start_i + per]
        buttons = []
        for pid in chunk:
            p   = PRODUCTS[pid]
            sl  = stock_label(pid, data)
            q_v = get_stock(pid, data)
            qty_txt = f" ({q_v})" if q_v > 0 else ""
            buttons.append([InlineKeyboardButton(
                f"{sl[:2]}{qty_txt} {p['name'][:33]}",
                callback_data=f"stock_edit_{pid}"
            )])
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"admin_stock_p{page-1}"))
        if start_i + per < len(pids):
            nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"admin_stock_p{page+1}"))
        if nav: buttons.append(nav)
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
        await q.edit_message_text(
            f"📦 *إدارة المخزون* (صفحة {page} / {(len(pids)-1)//per+1}):",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif act.startswith("stock_edit_"):
        pid  = act.replace("stock_edit_", "")
        data = load_data()
        p    = PRODUCTS[pid]
        sl   = stock_label(pid, data)
        ctx.user_data["stock_pid"]    = pid
        ctx.user_data["admin_action"] = "set_stock"
        await q.edit_message_text(
            f"📦 *{p['name']}*\n"
            f"الحالة: {sl}\n\n"
            f"أدخل الكمية المتوفرة:\n"
            f"• رقم موجب = كمية محددة\n"
            f"• *0* = نفذت الكمية\n"
            f"• *-1* = متوفر بدون تحديد",
            parse_mode="Markdown"
        )

    elif act == "admin_back":
        data = load_data()
        await q.edit_message_text(
            f"👑 *لوحة تحكم Anker Syria*\n\n"
            f"👥 المستخدمون: {len(data['users'])}\n"
            f"🛒 الطلبات: {len(data['orders'])}\n"
            f"💱 سعر الصرف: {data['exchange_rate']:,} ل.س",
            parse_mode="Markdown",
            reply_markup=admin_kb()
        )

# ═══════════════════════════════════════════════
#  ✉️  معالج النصوص العام
# ═══════════════════════════════════════════════
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text   = update.message.text.strip()
    action = ctx.user_data.get("admin_action")
    mode   = ctx.user_data.get("mode")
    uid    = update.effective_user.id

    # أزرار الرئيسية
    if text == "🛍️ تصفح الكتالوج": await show_catalog(update, ctx); return
    if text == "🔍 بحث سريع":        await search_prompt(update, ctx); return
    if text == "📞 تواصل معنا":       await contact_us(update, ctx); return
    if text == "ℹ️ عن المتجر":        await about_store(update, ctx); return
    if text == "❤️ المفضلة":          await show_favorites(update, ctx); return
    if text == "🛒 طلباتي":           await show_my_orders(update, ctx); return
    if text == "🏠 الرئيسية":
        ctx.user_data["mode"] = None
        await start(update, ctx); return

    # أدمن: سعر الصرف
    if action == "set_rate" and is_admin(uid):
        try:
            rate = int(text.replace(",", "").replace(".", ""))
            data = load_data()
            data["exchange_rate"] = rate
            save_data(data)
            ctx.user_data.pop("admin_action", None)
            await update.message.reply_text(
                f"✅ تم تحديث سعر الصرف إلى *{rate:,} ل.س*",
                parse_mode="Markdown", reply_markup=admin_kb()
            )
        except ValueError:
            await update.message.reply_text("❌ رقم غير صحيح. مثال: 14500")
        return

    # أدمن: تحديث الكمية
    if action == "set_stock" and is_admin(uid):
        pid = ctx.user_data.get("stock_pid")
        try:
            qty = int(text)
            data = load_data()
            data.setdefault("products", {}).setdefault(pid, {})
            data["products"][pid]["quantity"] = qty
            data["products"][pid]["in_stock"]  = qty != 0
            save_data(data)
            ctx.user_data.pop("admin_action", None)
            ctx.user_data.pop("stock_pid", None)
            await update.message.reply_text(
                f"✅ تم!\n📦 {PRODUCTS[pid]['name']}\n{stock_label(pid, data)}",
                reply_markup=admin_kb()
            )
        except ValueError:
            await update.message.reply_text("❌ أدخل رقماً صحيحاً.")
        return

    # أدمن: إعلان
    if action == "broadcast" and is_admin(uid):
        data = load_data()
        ctx.user_data.pop("admin_action", None)
        await update.message.reply_text("📤 جاري الإرسال...")
        sent = failed = 0
        for u in data["users"]:
            try:
                await ctx.bot.send_message(
                    int(u),
                    f"📢 *إعلان من Anker Syria*\n\n{text}",
                    parse_mode="Markdown"
                )
                sent += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ اكتمل!\n✔️ نجح: {sent} | ❌ فشل: {failed}",
            reply_markup=admin_kb()
        )
        return

    # وضع البحث
    if mode == "search":
        await do_search(update, ctx); return

    await update.message.reply_text("اختر من القائمة 👇", reply_markup=main_kb())

# ═══════════════════════════════════════════════
#  ▶️  تشغيل البوت
# ═══════════════════════════════════════════════
def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(cb_category,      pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(cb_product,       pattern=r"^prod_"))
    app.add_handler(CallbackQueryHandler(cb_favorite,      pattern=r"^fav_"))
    app.add_handler(CallbackQueryHandler(cb_order_qty,     pattern=r"^order_qty_"))
    app.add_handler(CallbackQueryHandler(cb_order_confirm, pattern=r"^oconf_"))
    app.add_handler(CallbackQueryHandler(back_catalog_cb,  pattern=r"^back_catalog$"))
    app.add_handler(CallbackQueryHandler(admin_callback,
        pattern=r"^(admin_|stock_edit_)"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ── تشغيل Keep-Alive في الخلفية ─────────────
    threading.Thread(target=_run_http_server, daemon=True).start()
    threading.Thread(target=_self_ping,       daemon=True).start()

    print("🚀 Anker Syria Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
