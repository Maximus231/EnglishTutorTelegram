from googletrans import Translator
import json
import my_logging as lg
import requests
import nltk
import re

def obtain_substring_with_extra_word(original_string, a, b):
    # Split the original string into words
    words = original_string.split()

    # Find the start index of the substring
    start_index = 0
    current_char_count = 0
    for i, word in enumerate(words):
        if current_char_count + len(word) >= a:
            start_index = i
            break
        current_char_count += len(word) + 1  # Account for the space between words

    # Find the end index of the substring
    end_index = len(words) - 1
    current_char_count = 0
    for i, word in enumerate(words[start_index:], start=start_index):
        if current_char_count + len(word) >= b:
            end_index = i
            break
        current_char_count += len(word) + 1  # Account for the space between words

    # Adjust start and end indexes to include one more word from the left and right
    start_index = max(0, start_index - 1)
    end_index = min(len(words) - 1, end_index + 1)

    # Construct the new substring
    new_substring = ' '.join(words[start_index:end_index + 1])

    return new_substring


def insert_spaces_between_sentences(text):
	# List of punctuation marks that usually denote the end of a sentence
	punctuation_marks = ['.', '!', '?']

	# Initialize an empty string to store the result
	result = ''

	# Iterate through each character in the text
	for i, char in enumerate(text):
		# Add the current character to the result
		result += char

		# If the current character is a punctuation mark and the next character is not a space
		if char in punctuation_marks and i + 1 < len(text) and text[i + 1] != ' ':
			# Add a space after the punctuation mark
			result += ' '

	return result


def remove_telegram_emojis(text):
	# Regular expression pattern to match Telegram emojis
	emoji_pattern = re.compile("[\U0001F600-\U0001F64F"  # emoticons
							   "\U0001F300-\U0001F5FF"  # symbols & pictographs
							   "\U0001F680-\U0001F6FF"  # transport & map symbols
							   "\U0001F700-\U0001F77F"  # alchemical symbols
							   "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
							   "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
							   "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
							   "\U0001FA00-\U0001FA6F"  # Chess Symbols
							   "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
							   "\U00002702-\U000027B0"  # Dingbats
							   "\U000024C2-\U0001F251"
							   "]+", flags=re.UNICODE)

	# Remove Telegram emojis from the text
	text_without_emojis = emoji_pattern.sub(r'', text)

	return text_without_emojis


def translate_text(text, target_language='en'):
	#nltk.download('punkt')
	lg.log_message("INFO", "Translation. Message to translate: " + text)
	translator = Translator()
	translated_text = translator.translate(text, dest=target_language)
	# Split the translated text into sentences
	#translated_sentences = nltk.sent_tokenize(translated_text.text)
	# Join the translated sentences with spaces
	translated_text_with_spaces = insert_spaces_between_sentences(translated_text.text)
	#translated_text_with_spaces = ' '.join(translated_sentences)
	return translated_text_with_spaces


def highlight_message(message, mistakes):
	current_index = 0
	message_with_errors = ""
	for mistake in mistakes:
		i_from = int(mistake['From'])
		i_to = int(mistake['To'])
		message_with_errors += message[current_index:i_from] + "<s>" + message[i_from:i_to] + "</s> <b>" + mistake['Replace with'] + "</b>"
		current_index = mistake['To']
	message_with_errors += message[current_index:]
	return message_with_errors


def form_mistakes(mistakes):
	current_index = 1
	mistakes_message = "\n\nDetails:"
	for mistake in mistakes:
		mistakes_message += "\n"+ current_index.__str__() + ". <i>" + mistake['Text fragment'] + "</i>: <s>" + mistake['Replace text'] + "</s> -> <b>" + mistake['Replace with'] + "</b>. " + mistake['Explanation'] + "."
		current_index += 1
	return mistakes_message


def get_mistakes_topics(mistakes):
	mistakes_topics = []
	for mistake in mistakes:
		mistakes_topics.append(mistake['Explanation'])
	return mistakes_topics



def ginger_parser(ginger_response="", initial_message=""):  # input: ginger's response, output: revised text, errors, ...
	if ginger_response == "":
		file_path = 'data/ginger_response_example.txt'
		with open(file_path, 'r') as file:
			ginger_response = json.load(file)
		initial_message = 'hi this are errors in tho message'
	# 1. Replace all errors and build array with mistakes
	corrected_message = ""
	is_errors = False
	mistakes_characters = []
	mistakes = []
	current_loop = 0
	current_index = 0
	ginger_response = ginger_response.json()
	if (len(ginger_response['GingerTheDocumentResult']['Corrections']) > 0):
		for correction in ginger_response['GingerTheDocumentResult']['Corrections']:
			# 1.1 Replace current error
			if (correction['Confidence'] >= 3) and (correction['ShouldReplace']):
				is_errors = True
				from_index = int(correction['From'])
				to_index = int(correction['To']) + 1 # ???
				suggested_replacement_0 = correction['Suggestions'][0]['Text']
				corrected_message += initial_message[current_index:from_index] + suggested_replacement_0
				current_index = to_index
				# 1.2 Mistakes list
				mistk = {}
				mistk['No'] = current_loop
				mistk['Text fragment'] = obtain_substring_with_extra_word(initial_message, from_index, to_index)
				mistk['Replace text'] = correction['MistakeText']
				mistk['Replace with'] = correction['Suggestions'][0]['Text']
				mistk['Explanation'] = correction['TopCategoryIdDescription']
				mistk['From'] = from_index
				mistk['To'] = to_index
				mistakes.append(mistk)

				current_loop += 1
		corrected_message += initial_message[current_index:]
	return corrected_message, mistakes, is_errors


def check_mistakes(message, test_mode=True, show_descriptions=False):
	lg.log_message("INFO", "Start working with MESSAGE:" + message)
	message = remove_tags(message)
	if not test_mode:
		lg.log_message("TEST", "LIVE MODE (TEST = FALSE)")
		url = "https://ginger4.p.rapidapi.com/correction"
		querystring = {"lang": "US", "generateRecommendations": "true", "flagInfomralLanguage": "true"}
		payload = message
		#main.log.log_message("INFO", "MESSAGE (tags removed):"+message)
		headers = {
			"content-type": "text/plain",
			"Content-Type": "text/plain",
			"Accept-Encoding": "identity",
			"X-RapidAPI-Key": "3fcd771099msh8c3893b5292a80ep171395jsn7b52a76a079d",
			"X-RapidAPI-Host": "ginger4.p.rapidapi.com"
		}

		try:
			lg.log_message("PAYED", "Payed function has started. SERVICE: Ginger")
			ginger_resp = requests.post(url, data=payload, headers=headers, params=querystring)
			ginger_errors = ginger_resp.raise_for_status()  # Raise an exception for HTTP errors
		except requests.RequestException as e:
			lg.log_message("ERROR", "Can't receive an answer from Ginger" + e)
			lg.log_message("ERROR DATA", "Request:" + message)
			lg.log_message("ERROR DATA", "Ginger response:" + ginger_resp.text)
			print('Problem in lang.py, line 181')
		initial_message = message
		print("Called payed function!")
	else:
		lg.log_message("TEST?", "TRUE, TEST MODE")
		file_path = 'data/ginger_response_example.txt'
		with open(file_path, 'r') as file:
			ginger_resp = json.load(file)
		initial_message = '#c hi this are errors in tho message'
		initial_message = remove_tags(initial_message)
	corrected_message1, mistakes, is_errors = ginger_parser(ginger_resp, initial_message)
	if not show_descriptions:
		return is_errors, corrected_message1, len(mistakes), get_mistakes_topics(mistakes)
	else:
		corrected_message_with_mistakes = highlight_message(initial_message, mistakes)
		corrected_message_with_mistakes += form_mistakes(mistakes)
		return is_errors, corrected_message_with_mistakes, len(mistakes), get_mistakes_topics(mistakes)

def remove_tags (message):
	string = str(message)
	return string.replace("#t", "").replace("#c", "").replace("#f", "").replace("#check", "").replace("#full_check", "").replace("#translate", "")