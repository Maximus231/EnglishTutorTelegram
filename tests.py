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

# Example usage
original_string = "This is an example string to demonstrate the function."
a = 8  # Index indicating the start of the substring
b = 14  # Index indicating the end of the substring
new_substring = obtain_substring_with_extra_word(original_string, a, b)
print(new_substring)
