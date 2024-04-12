import json
import telebot
import shutil
from datetime import datetime

def get_user(tg_user):
    users_file_name = 'stat/blah_blah_eng_group_users.json'
    try:
        with open(users_file_name, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        with open(users_file_name, 'w') as f: # create empty file if it doesn't exist
            pass
        users = []
    except json.decoder.JSONDecodeError: #if file is exist but empty
        users = []
    user_id = ''
    users_arr = []
    for user in users:
        users_arr.append(user)
        if (user['id'] == tg_user.id):
            user_id = user['id']
    if (user_id != ''):
        return user_id
    else:
        #backup old users file
        current_datetime = datetime.now()
        users_file_name_bcp = 'stat/blah_blah_eng_group_users_bcp'+current_datetime.strftime('%Y.%m.%d.%H.%M')+'.json'
        # Copy the file
        shutil.copy(users_file_name, users_file_name_bcp)
        current_user = {'id': tg_user.id, 'Username': tg_user.username, 'First name': tg_user.username, 'Last name': tg_user.username, 'Lang code': tg_user.language_code}
        users_arr.append(current_user)
        with open(users_file_name, 'w+') as f: # 'w+' means open or create if does not exist
            json.dump(users_arr, f, indent=4)
        return tg_user.id


def get_topic(topics):
    topics_file_name = 'stat/blah_blah_eng_group_topics.json'
    try:
        with open(topics_file_name, "r") as f:
            dict_topics = json.load(f)
    except FileNotFoundError:
        dict_topics = []
        with open(topics_file_name, 'w') as f:  # create empty file if it doesn't exist
            pass
    except json.decoder.JSONDecodeError: #if file is exist but empty
        dict_topics = []
    topics_arr = []
    is_dictionary_changed = False
    for topic in topics:
        topic_found = False
        for dict_topic in dict_topics:
            if dict_topic['name'] == topic:
                cur_topic = {'id': int(dict_topic['id']), 'name': dict_topic['name']}
                topics_arr.append(cur_topic)
                #print('topic found', topics_arr)
                topic_found = True
        if not topic_found:
            if len(dict_topics) > 0:
                last_topic_id = dict_topics[-1]['id']
            else:
                last_topic_id = -1
            new_topic = {'id': int(last_topic_id) + 1, 'name': topic}
            dict_topics.append(new_topic)
            is_dictionary_changed = True
            topics_arr.append(new_topic)
    if is_dictionary_changed:
        #backup old users file
        current_datetime = datetime.now()
        topics_file_name_bcp = 'stat/blah_blah_eng_group_topics_bcp'+current_datetime.strftime('%Y.%m.%d.%H.%M')+'.json'
        # Copy the file
        shutil.copy(topics_file_name, topics_file_name_bcp)
        with open(topics_file_name, 'w+') as f: # 'w+' means open or create if does not exist
            json.dump(dict_topics, f, indent=4)
    return topics_arr


def record_txt_message_check(message, response, topics, trusted_mistakes, action_type=1001):
    # 1. Get user
    tg_user_id = get_user(message.from_user)
    topics_from_dict = []
    if len(topics) > 0:
        topics_from_dict = get_topic(topics)
    action_content = {'message': message.text, 'response': response, 'trusted_mistakes': trusted_mistakes, 'topics': topics_from_dict}
    write_action_to_file(tg_user_id, action_type, action_content)
    return True


def record_txt_message_translate(message, response, action_type=2001):
    # 1. Get user
    tg_user_id = get_user(message.from_user)
    action_content = {'message': message.text, 'response': response}
    write_action_to_file(tg_user_id, action_type, action_content)
    return True


def write_action_to_file(user_id, action_type, action_content):
    log_file_name = 'stat/current_log.json'

    # Initialize an empty list if the file is empty
    try:
        with open(log_file_name) as f:
            log_array = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        log_array = []

    # Determine action ID
    if not log_array:
        action_id = 0
    else:
        action_id = log_array[-1]['id'] + 1

    # Create new action
    current_action = {"id": action_id, "user": user_id, "action_type": action_type, "content": action_content}

    # Update log list with the new action
    log_array.append(current_action)

    # Save updated log data back to file
    with open(log_file_name, 'w') as f:
        json.dump(log_array, f, indent=4)

    return True


def move_actions_to_statistics():
    return True
