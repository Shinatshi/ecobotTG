import telebot
import random
import requests
from telebot import types
from config import TOKEN
from eco_parser import get_random_eco_news

bot = telebot.TeleBot(TOKEN)

user_quiz_progress = {}
eco_tips = [
    "🌱 Используйте многоразовые сумки вместо пластиковых пакетов.",
    "💧 Экономьте воду: выключайте кран, когда чистите зубы.",
    "💡 Используйте энергосберегающие лампы.",
    "♻️ Сортируйте мусор и сдавайте отходы на переработку.",
    "🚴 Отдавайте предпочтение общественному транспорту или велосипеду."
]

quiz_questions = [
    {
        "question": "🗑 Какой процент пластика перерабатывается в мире?",
        "options": ["9%", "20%", "35%", "50%"],
        "correct": 0
    },
    {
        "question": "🐻 Какое животное символизирует изменение климата?",
        "options": ["Лев", "Полярный медведь", "Дельфин", "Орёл"],
        "correct": 1
    },
    {
        "question": "🌿 Какое из этих действий наиболее снижает углеродный след?",
        "options": ["Использование электромобиля", "Сортировка мусора", "Вегетарианство", "Использование бумажных пакетов"],
        "correct": 2
    }
]

def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🧮 Эко-калькулятор", "🌱 Совет по экологии")
    keyboard.row("📝 Начать викторину", "📰 Новости экологии")
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я эко-бот. 🌿 Выбери функцию:", reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda message: message.text.lower() == "🌱 совет по экологии")
def send_eco_tip(message):
    bot.send_message(message.chat.id, random.choice(eco_tips))

@bot.message_handler(func=lambda message: message.text.lower() == "🧮 эко-калькулятор")
def eco_calculator(message):
    msg = bot.send_message(message.chat.id, "Введите количество километров, которые вы проезжаете на автомобиле в день: 🚗")
    bot.register_next_step_handler(msg, calculate_impact)

def calculate_impact(message):
    try:
        km = float(message.text)
        carbon_footprint = km * 0.2
        trees_needed = carbon_footprint / 22
        bot.send_message(message.chat.id, f"🌍 Ваш углеродный след составляет примерно <b>{carbon_footprint:.2f}</b> кг CO2 в день.\nЧтобы компенсировать этот выброс, необходимо высадить примерно <b>{trees_needed:.2f}</b> деревьев в год.", parse_mode="HTML")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите число.")

@bot.message_handler(func=lambda message: message.text.lower() == "📝 начать викторину")
def start_quiz(message):
    user_id = message.chat.id
    random.shuffle(quiz_questions)
    user_quiz_progress[user_id] = {
        "questions": quiz_questions[:3],
        "current_question": 0,
        "correct_answers": 0
    }
    send_question(message.chat.id, user_id)

def send_question(chat_id, user_id):
    state = user_quiz_progress[user_id]
    if state["current_question"] < len(state["questions"]):
        current_q = state["questions"][state["current_question"]]
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(option, callback_data=f"quiz_{state['current_question']}_{i}") for i, option in enumerate(current_q["options"]) ]
        markup.add(*buttons)
        bot.send_message(chat_id, f"🧩 Вопрос {state['current_question'] + 1} из {len(state['questions'])}:\n\n{current_q['question']}", reply_markup=markup)
    else:
        correct = state["correct_answers"]
        total = len(state["questions"])
        bot.send_message(chat_id, f"🎯 Викторина завершена! Ваш результат: {correct} из {total} правильных ответов.\nЭто {int(correct/total*100)}% правильных ответов.")
        del user_quiz_progress[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def handle_quiz_answer(call):
    user_id = call.from_user.id
    _, question_idx, answer_idx = call.data.split('_')
    question_idx, answer_idx = int(question_idx), int(answer_idx)
    state = user_quiz_progress[user_id]
    current_q = state["questions"][question_idx]
    is_correct = (answer_idx == current_q["correct"])
    if is_correct:
        state["correct_answers"] += 1
        bot.answer_callback_query(call.id, "✅ Правильно!")
    else:
        correct_option = current_q["options"][current_q["correct"]]
        bot.answer_callback_query(call.id, f"❌ Неправильно! Правильный ответ: {correct_option}")
    state["current_question"] += 1
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    send_question(call.message.chat.id, user_id)

@bot.message_handler(func=lambda message: message.text.lower() == "📰 новости экологии")
def send_random_news(message):
    news = get_random_eco_news()
    if news:
        bot.send_message(
            message.chat.id, 
            f"🌿 <b>Случайная новость об экологии:</b>\n\n<b>{news['title']}</b>\n\n🔗 <a href='{news['link']}'>Читать подробнее</a>", 
            parse_mode="HTML",
            disable_web_page_preview=False
        )
    else:
        bot.send_message(message.chat.id, "❌ Не удалось получить новости. Попробуйте позже.")


bot.infinity_polling()
