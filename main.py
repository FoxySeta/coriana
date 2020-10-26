# es. 02_18
# Bot telegram
# 
# Volpe Stefano (5Bsa)
# 16/02/2020
# Python 3.8.1

#!pip install pytelegrambotapi

import json
import os.path
import telebot
from telebot import types

def get_node(state):
    flow_path, state_error = 'flow/', 'error'
    if not state:
        state = state_error
    node_filename = flow_path + state + '.dat'
    if not os.path.isfile(node_filename):
        node_filename = flow_path + state_error + '.dat'
    if os.path.isfile(node_filename):
        with open(node_filename) as node_file:
            return json.loads(node_file.read())
    else:
        return None

def reply(bot, message, states):
    stickers_path = 'stickers/'

    if message.content_type == 'text':
        user_id = str(message.from_user.id)
        if message.text[0] == '/': # command
            states[user_id] = message.text[1:]
        else: #text answer
            old_node = get_node(states[user_id])
            if old_node and 'answers' in old_node:
                for x in old_node['answers']:
                    if x['text'] == message.text:
                        states[user_id] = x['state']
                        break
                else:
                    states[user_id] = None
            else:
                states[user_id] = None
        node = get_node(states[user_id])
        if node:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard = True)
            if "answers" in node:
                markup.add(*[types.KeyboardButton(x["text"]) for x in node["answers"]])
            for x in node['messages']:
                if x['type'] == 'text':
                    bot.send_message(message.chat.id, x['text'], reply_markup=markup)
                elif x['type'] == 'sticker':
                    sticker_filename = stickers_path + x['sticker'] + '.tgs'
                    if os.path.isfile(sticker_filename):
                        with open(sticker_filename, 'rb') as sticker:
                            bot.send_sticker(message.chat.id, sticker, reply_markup=markup)
                    else:
                        print('Sticker "' + sticker_filename + '" non trovato.')
                else:
                    print('Tipo "' + x['type'] + '" ignoto.')

def main():
    token_filename, states_filename = 'token.txt' , 'states.dat'
    if not os.path.isfile(token_filename):
        print('File token "' + token_filename + '" non trovato.')
        return
    with open(token_filename) as token_file:
        coriana = telebot.TeleBot(token_file.readline())
    states = {}
    if os.path.isfile(states_filename):
        with open(states_filename) as states_file:
            states = json.loads(states_file.read())
    
    @coriana.message_handler(func=lambda message: True)
    def coriana_reply(message):
        reply(coriana, message, states)
        with open(states_filename, 'w') as states_file:
            states_file.write(json.dumps(states))
    coriana.polling()

if __name__ == '__main__':
    main()