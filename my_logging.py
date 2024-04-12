import csv
import datetime

import lang


def log_message(message_type, data):
    # Create the directory if it doesn't exist
    file_name = 'logs/audit_log_april_2024.csv'

    # Get the current time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Write the log entry to the CSV file
    with open(file_name, "a", newline="") as file:
        try:
            writer = csv.writer(file)
            writer.writerow([current_time, message_type, data])
        except Exception as e:
            writer.writerow([current_time, message_type, "Cant log message with emoji. Message w/o emoji: " + lang.remove_telegram_emojis(data), e])
            print("Problems with update log!", e)
