from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pymongo import MongoClient

# Replace the TOKEN and MongoDB connection string with your values
TOKEN: Final = '7847258274:AAEbJq1L5tG6J89QQEAzgzEfwJ81FIOzbZ0'
BOT_USERNAME: Final = '@hackerinterviewbot'

# Connection string from MongoDB Atlas
client = MongoClient("mongodb+srv://anik:AnirudhMongoDB@interviewhacker.fwixr.mongodb.net/?retryWrites=true&w=majority&appName=InterviewHacker")
db = client['coding_questions']  # Your database name

# Collections
topics_collection = db['topics']
questions_collection = db['questions']

# Function to get the topics from MongoDB
def get_topics():
    topics = topics_collection.find({})
    return [t["name"] for t in topics]

# Function to get questions by topic
def get_questions_by_topic(topic_name):
    questions = questions_collection.find({"topic": topic_name})
    return [q["question_text"] for q in questions]

# Function to get approach and intuition by question text
def get_approach_by_question(question_text):
    question = questions_collection.find_one({"question_text": question_text})
    if question:
        return question.get("approach"), question.get("intuition")
    return None, None

# Start command handler to show the topic selection menu
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(topic, callback_data=topic)] for topic in get_topics()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Select a topic:", reply_markup=reply_markup)

# Handler for topic selection
async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    topic_name = query.data
    
    questions = get_questions_by_topic(topic_name)
    if questions:
        question_buttons = [[InlineKeyboardButton(q, callback_data=f"question:{q}")] for q in questions]
        reply_markup = InlineKeyboardMarkup(question_buttons)
        await query.edit_message_text(f"Here are some questions for {topic_name}: Select one to view the approach.", reply_markup=reply_markup)
    else:
        await query.edit_message_text(f"No questions found for {topic_name}.")

# Handler for question selection
async def handle_question_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    question_text = query.data.split(':')[1]  # Extract the question from callback_data

    approach, intuition = get_approach_by_question(question_text)
    if approach and intuition:
        await query.edit_message_text(f"Approach: {approach}\nIntuition: {intuition}")
    else:
        await query.edit_message_text("No approach found for this question.")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print("Starting BOT...")
    app = Application.builder().token(TOKEN).build()
    
    # Command handler to show the topic menu
    app.add_handler(CommandHandler('start', start_command))
    
    # CallbackQuery handlers for topic and question selection
    app.add_handler(CallbackQueryHandler(handle_topic_selection, pattern="^((?!question:).)*$"))  # For topics
    app.add_handler(CallbackQueryHandler(handle_question_selection, pattern="^question:.*$"))  # For questions

    # Errors:
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
