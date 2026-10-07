import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# База данных школ
SCHOOLS_DB = {
    "21": {
        "name": "21-sonli umumta'lim maktabi",
        "director": "Karimov Botir Ergashevich (+998931112233)",
        "deputy": "Sodiqova Lola Rahimovna (+998944445566)"
    },
    "45": {
        "name": "45-sonli maktab",
        "director": "Ahmedov Rustam Qodirovich (+998909998877)",
        "deputy": "Usmanova Dilnoza (+998935554433)"
    },
    "12": {
        "name": "12-sonli maktab",
        "director": "Tursunov Jamshid Mahmudovich (+998912223344)",
        "deputy": "Yusupova Feruza (+998908887766)"
    }
}

# База данных учеников
STUDENTS_DB = [
    {
        "full_name": "Valiyev Ali Akmalovich",
        "search_name": "ali valiyev",
        "birth_date": "15.03.2008",
        "passport": "FA 1234567",
        "father": "Valiyev Akmal Karimovich (+998901234567)",
        "mother": "Valiyeva Salima Sobirovna (+998907654321)",
        "children": "Yo'q",
        "crimes_count": "1 ta (Mayda bezorilik)",
        "school_id": "21",
        "class": "10-'B' sinf"
    },
    {
        "full_name": "Oripov Hasan Husanovich",
        "search_name": "hasan oripov",
        "birth_date": "04.05.2008",
        "passport": "FA 4455667",
        "father": "Oripov Husan (+998901110022)",
        "mother": "Oripova Kamola (+998903330044)",
        "children": "Yo'q",
        "crimes_count": "Yo'q",
        "school_id": "21",
        "class": "10-'A' sinf"
    },
    {
        "full_name": "Rahimov Sardor Ilhomovich",
        "search_name": "sardor rahimov",
        "birth_date": "22.08.2007",
        "passport": "FA 7654321",
        "father": "Rahimov Ilhom (+998911112233)",
        "mother": "Rahimova Nargiza (+998913332211)",
        "children": "Yo'q",
        "crimes_count": "Yo'q (Sudlanmagan)",
        "school_id": "45",
        "class": "11-'A' sinf"
    },
    {
        "full_name": "Bekzodov Jasur Alisherovich",
        "search_name": "jasur bekzodov",
        "birth_date": "10.01.2009",
        "passport": "FA 9988776",
        "father": "Bekzodov Alisher (+998977771122)",
        "mother": "Bekzodova Gulnora (+998977773344)",
        "children": "Yo'q",
        "crimes_count": "2 ta (O'g'irlikga urunish, Mayda bezorilik)",
        "school_id": "12",
        "class": "9-'V' sinf"
    }
]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Xush kelibsiz!\n\n"
        " Qidirish uchun **Ism-Familiya** (masalan: *Ali Valiyev*) "
        "yoki **Maktab nomini/raqamini** (masalan: *21*) kiriting:",
        parse_mode="Markdown"
    )

# Главная функция поиска
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip().lower()
    input_words = set(user_text.split())

    # --- 1. Поиск по школе ---
    matched_school_id = None
    for s_id, s_info in SCHOOLS_DB.items():
        if s_id in user_text or s_info["name"].lower() in user_text:
            matched_school_id = s_id
            break

    if matched_school_id:
        school = SCHOOLS_DB[matched_school_id]
        
        # Находим всех учеников этой школы
        students_in_school = [s for s in STUDENTS_DB if s["school_id"] == matched_school_id]
        
        list_text = ""
        for idx, student in enumerate(students_in_school, 1):
            list_text += f"{idx}. *{student['full_name']}* ({student['class']}) - Jinoyatlari: {student['crimes_count']}\n"

        if not list_text:
            list_text = "Ushbu maktab bo'yicha o'quvchilar topilmadi."

        response = (
            f"🏫 *{school['name']} bo'yicha ma'lumot:*\n\n"
            f"👔 *Maktab direktori:* {school['director']}\n"
            f"📋 *Zamdirektor:* {school['deputy']}\n"
            f"👥 *Bazada ro'yxatda turgan o'quvchilar soni:* {len(students_in_school)} ta\n\n"
            f"📜 *O'quvchilar ro'yxati:*\n{list_text}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
        return

    # --- 2. Поиск по человеку ---
    found_student = None
    for student in STUDENTS_DB:
        name_words = set(student["search_name"].split())
        if input_words == name_words or user_text in student["full_name"].lower():
            found_student = student
            break

    if found_student:
        school = SCHOOLS_DB.get(found_student["school_id"], {
            "name": "Noma'lum", "director": "Noma'lum", "deputy": "Noma'lum"
        })
        
        response = (
            f"🔍 *Qidiruv natijasi (O'quvchi):*\n\n"
            f"👤 *F.I.SH:* {found_student['full_name']}\n"
            f"📅 *Tug'ilgan sana:* {found_student['birth_date']}\n"
            f"🪪 *Pasport / ID:* {found_student['passport']}\n\n"
            f"⚠️ *Sodir etgan jinoyatlari soni:* {found_student['crimes_count']}\n\n"
            f"👨 *Otasining ma'lumotlari:* {found_student['father']}\n"
            f"👩 *Onasining ma'lumotlari:* {found_student['mother']}\n"
            f"👶 *Farzandlari:* {found_student['children']}\n\n"
            f"🏫 *O'qiydigan maktabi:* {school['name']} ({found_student['class']})\n"
            f"👔 *Maktab direktori:* {school['director']}\n"
            f"📋 *Maktab zamdirektori:* {school['deputy']}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
        return

    # Если ничего не найдено
    await update.message.reply_text(
        "❌ Ma'lumot topilmadi. Ism-familiya yoki maktab raqamini to'g'ri kiriting.",
        parse_mode="Markdown"
    )

def main():
    # Замените на ваш настоящий токен от @BotFather
    BOT_TOKEN = "8883494527:AAExbvpsKQbJlN5Ly7LMj52vHobrA-Z25RI"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()