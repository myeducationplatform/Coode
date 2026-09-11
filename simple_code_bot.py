import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)

# ضع توكن البوت الجديد هنا من BotFather
TOKEN = "8967669158:AAGE7opM5tUJB7EtlVzDW6Vm24O-wIJvA_I"

# حالات المحادثة
ADD_NAME, SEARCH_NAME = range(2)

# إنشاء قاعدة البيانات وتجهيز الجدول
def init_db():
    conn = sqlite3.connect('codes_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# توليد كود عشوائي مكون من 6 أرقام فقط
def generate_6digit_code():
    return str(random.randint(100000, 999999))

# أزرار القائمة الرئيسية
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ إدراج جديد", callback_data="add")],
        [InlineKeyboardButton("📋 عرض القائمة", callback_data="list")],
        [InlineKeyboardButton("🔍 معرفة كود", callback_data="search")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **أهلاً بك في بوت توليد وإدارة الأكواد:**\nاختر من القائمة أدناه:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# 1. خيار إدراج جديد
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📝 **أدخل الاسم المراد تسجيله وتوليد كود له:**")
    return ADD_NAME

async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    code = generate_6digit_code()

    try:
        conn = sqlite3.connect('codes_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users_codes (name, code) VALUES (?, ?)", (name, code))
        conn.commit()
        conn.close()

        await update.message.reply_text(
            f"✅ **تمت الإضافة بنجاح!**\n\n"
            f"👤 **الاسم:** `{name}`\n"
            f"🔢 **الكود المولد:** `{code}`",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    except sqlite3.IntegrityError:
        await update.message.reply_text(
            f"⚠️ **الاسم ({name}) موجود بالفعل!**\nيرجى كتابة اسم آخر أو الاستعلام عن كوده من خيار البحث.",
            reply_markup=get_main_keyboard()
        )
    
    return ConversationHandler.END

# 2. خيار عرض القائمة
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = sqlite3.connect('codes_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, code FROM users_codes ORDER BY id ASC")
    records = cursor.fetchall()
    conn.close()

    if not records:
        msg = "📜 **لا يوجد أسماء مسجلة في القائمة حالياً.**"
    else:
        msg = "📜 **قائمة الأسماء والأكواد المسجلة:**\n\n"
        for idx, item in enumerate(records, start=1):
            msg += f"**{idx}.** `{item[0]}` 👈 الكود: `{item[1]}`\n"

    await query.message.reply_text(msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# 3. خيار معرفة كود (بحث سريع)
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🔍 **أدخل الاسم المدرج لمعرفة كوده بسرعة:**")
    return SEARCH_NAME

async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_name = update.message.text.strip()

    conn = sqlite3.connect('codes_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM users_codes WHERE name = ?", (search_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        await update.message.reply_text(
            f"🔎 **نتيجة البحث:**\n\n"
            f"👤 **الاسم:** `{search_name}`\n"
            f"🔑 **الكود:** `{result[0]}`",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ **الاسم ({search_name}) غير مدرج في القائمة.**",
            reply_markup=get_main_keyboard()
        )

    return ConversationHandler.END

# إلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add, pattern="^add$"),
            CallbackQueryHandler(start_search, pattern="^search$"),
        ],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_user)],
            SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_search)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
        per_user=True,
        per_message=False
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_list, pattern="^list$"))
    app.add_handler(conv_handler)

    print("🚀 البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()