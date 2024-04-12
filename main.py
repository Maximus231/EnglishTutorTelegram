import telebot
import os
import re
import lang
import requests
from random import choice
import secrets as s
import my_logging as lg
import my_stat as st


bot = telebot.TeleBot(s.telegram_bot_api_key)
lg.log_message("START", "Application has been started working")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".secrets/document-recognition-service-916db6238d60.json"

# @bot.message_handler(func=lambda message: True) #if it states "message: True", bot answers to all messages

@bot.message_handler(func=lambda message: True)
def parce_request(message):
    #print("Message thread id:", message.message_thread_id)

    # Translate the received message if posted in Translate to Eng topic
    if (message.message_thread_id == s.translation_chat_topic) or (message.message_thread_id == 956) or ("#translate" in message.text) or ("#t" in message.text):  # if topic == Translate to Eng
        bot.send_chat_action(message.chat.id, 'typing')
        #bot.reply_to(message, lang.translate_text(lang.remove_tags(message.text)))
        try:
            print('Translation')
            translated_text = lang.translate_text(lang.remove_tags(message.text))
            bot.reply_to(message, translated_text)
            st.record_txt_message_translate(message, translated_text, 2001)
            #raise TypeError("Input text must be a string.") # this is for testing to raise exception
        except Exception as e:
            bot.reply_to(message, "Unfortunately I can't translate this message.")
            lg.log_message("ERROR", "Translation. Can't translate the message from user " + str(message.from_user.id) + " (" + str(message.from_user.username)+")"+". Message: " + message.text + " ERROR: " + e.__str__())
            print(">>> An error during translation occurred:", e)

    # Find mistakes in the received message if posted in Spell checker topic
    elif (message.message_thread_id == s.short_spell_checing_chat_topic) or (message.message_thread_id == 957) or ("#check" in message.text) or ("#c" in message.text):  # if topic == Check mistakes
        bot.send_chat_action(message.chat.id, 'typing')
        #print(message.text)
        try:
            is_errors, corrected_message, mistakes_count, mistakes_topics = lang.check_mistakes(lang.remove_telegram_emojis(message.text),False,False)
            st.record_txt_message_check(message, corrected_message, mistakes_topics, mistakes_count)
            if not is_errors:
                send_ok_react(message.chat.id, message.message_id)
            else:
                bot.reply_to(message, lang.remove_tags(corrected_message), parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, "Unfortunately I can't check this message.")
            print(">>> An error during checking occurred:", e)
            lg.log_message("ERROR", "Checking. Can't check the message from user " + str(message.from_user.id) + " (" + str(message.from_user.username)+")"+". Message: " + message.text + " ERROR: " + e.__str__())


    elif (message.message_thread_id == s.full_spell_checking_chat_topic) or (message.message_thread_id == 955) or ("#full_check" in message.text) or ("#f" in message.text):  # if topic == Sandbox
        bot.send_chat_action(message.chat.id, 'typing')
        is_errors, corrected_message, mistakes_count, mistakes_topics = lang.check_mistakes(lang.remove_telegram_emojis(message.text), False, True)
        st.record_txt_message_check(message, corrected_message, mistakes_topics, mistakes_count, 1002)
        try:
            #raise TypeError("Input text must be a string.")  # this is for testing to raise exception
            #is_errors, corrected_message, mistakes_count, mistakes_topics = lang.check_mistakes(lang.remove_telegram_emojis(message.text),False,True)
            #st.record_txt_message_check(message, corrected_message, mistakes_topics, mistakes_count, 1002)
            if not is_errors:
                send_ok_react(message.chat.id, message.message_id)
            else:
                bot.reply_to(message, lang.remove_tags(corrected_message), parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, "Unfortunately I can't check this message. The report about this error has been sent to @Inyushkin.")
            print(">>> An error during checking occurred:", e)
            lg.log_message("ERROR", "Checking. Can't do full check for the message from user " + str(message.from_user.id) + " (" + message.from_user.username+")"+". Message: " + message.text + " ERROR: " + e.__str__())


def extract_and_log_topic_and_reply(message):
    # Extract the replied-to message if available
    replied_to_message = message.reply_to_message.text if message.reply_to_message else None


def send_ok_react(chat_id, message_id):
    emo = ["🔥", "👍", "😎", "👏", "🆒", "💯"]
    url = f'https://api.telegram.org/bot6859726555:AAGjsTn_V9_IRmk4ccUKx8zpGmU_gLq5P98/setMessageReaction'
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': [
            {
                'type': 'emoji',
                #'emoji': '🔥'  #Обычный вариант с одним смайлом.
                'emoji': choice(emo)  # Вариант со списком из смайликов.
            }
        ],
        'is_big': False
    }
    response = requests.post(url, json=data)
    result = response.json()


def main():
    bot.polling(none_stop=True)  #none_stop=True

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print("An error occurred:", e)
            print("Restarting the bot...")
