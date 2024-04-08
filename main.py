import telebot
import re
import lang
import requests
from random import choice

bot = telebot.TeleBot('6859726555:AAGjsTn_V9_IRmk4ccUKx8zpGmU_gLq5P98')


# @bot.message_handler(func=lambda message: True) #if it states "message: True", bot answers to all messages

@bot.message_handler(func=lambda message: True)


def parce_request(message):
    #print("Message thread id:", message.message_thread_id)

    # Translate the received message if posted in Tanslate to Eng topic
    if (message.message_thread_id == 5) or ("#translate" in message.text) or ("#t" in message.text):  # if topic == Translate to Eng
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, lang.translate_text(lang.remove_tags(message.text)))
    # Find mistakes in the received message if posted in Spell checker topic
    elif (message.message_thread_id == 56) or ("#check" in message.text) or ("#c" in message.text):  # if topic == Check mistakes
        bot.send_chat_action(message.chat.id, 'typing')
        is_errors, corrected_message = lang.check_mistakes(message.text,False,False)
        if not is_errors:
            send_ok_react(message.chat.id, message.message_id)
        else:
            bot.reply_to(message, lang.remove_tags(corrected_message), parse_mode='HTML')
    elif (message.message_thread_id == 194) or ("#full_check" in message.text) or ("#f" in message.text):  # if topic == Sandbox
        bot.send_chat_action(message.chat.id, 'typing')
        is_errors, corrected_message = lang.check_mistakes(message.text,False,True)
        if not is_errors:
            send_ok_react(message.chat.id, message.message_id)
        else:
            bot.reply_to(message, lang.remove_tags(corrected_message), parse_mode='HTML')



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

bot.polling() #none_stop=True

# if __name__ == '__main__':
#    main()
