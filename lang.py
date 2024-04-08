from googletrans import Translator
import requests
import json

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


def translate_text(text, target_language='en'):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language)
    res = translated_text.text
    return res


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
	message = remove_tags(message)
	if not test_mode:
		url = "https://ginger4.p.rapidapi.com/correction"
		querystring = {"lang": "US", "generateRecommendations": "true", "flagInfomralLanguage": "true"}
		payload = message
		headers = {
			"content-type": "text/plain",
			"Content-Type": "text/plain",
			"Accept-Encoding": "identity",
			"X-RapidAPI-Key": "3fcd771099msh8c3893b5292a80ep171395jsn7b52a76a079d",
			"X-RapidAPI-Host": "ginger4.p.rapidapi.com"
		}
		ginger_resp = requests.post(url, data=payload, headers=headers, params=querystring)
		initial_message = message
		print("Called payed function!")
		print("REQUEST")
		print(initial_message)
		print("RESPONSE")
		print(ginger_resp.text)
	else:
		file_path = 'data/ginger_response_example.txt'
		with open(file_path, 'r') as file:
			ginger_resp = json.load(file)
		initial_message = '#c hi this are errors in tho message'
		initial_message = remove_tags(initial_message)
	corrected_message1, mistakes, is_errors = ginger_parser(ginger_resp, initial_message)
	if not show_descriptions:
		return is_errors, corrected_message1
	else:
		corrected_message_with_mistakes = highlight_message(initial_message, mistakes)
		corrected_message_with_mistakes += form_mistakes(mistakes)
		return is_errors, corrected_message_with_mistakes

def remove_tags (message):
	string = str(message)
	return string.replace("#t", "").replace("#c", "").replace("#f", "").replace("#check", "").replace("#full_check", "").replace("#translate", "")