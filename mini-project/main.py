import os
import re
import math
import tkinter
from collections import Counter

#### PART 1 #####

os.makedirs("cleaned", exist_ok=True)

folder_path = "speeches"

# Manually listing all entries in the folder
entries = os.listdir(folder_path)

president_names = []
for entry in entries:

    # Cut the string after a number or a point
    result = ""
    for char in entry:
        if char.isdigit() or char == '.':  # Check if the character is a digit
            break
        result += char

    # Split the string and get the part after the Nomination_
    delimiter = "Nomination_"
    president = result.split(delimiter)[1]

    # Avoid doubles
    if president not in president_names:
        president_names.append(president)

    # Let's put the files in a folder "cleaned"
    original_file_path = os.path.join(folder_path, entry)
    cleaned_file_path = os.path.join("cleaned", entry)

    with open(original_file_path, "r", encoding="UTF8") as original_file, open(cleaned_file_path, "w", encoding="UTF8") as cleaned_file:
        cleaned_file.write(original_file.read().lower())  # Copy file content to the cleaned folder

    # Let's clean the files in the cleaned folder

    # Stop words list
    with open("stop_words.txt", "r", encoding="UTF8") as file:
        stop_words = file.readlines()

    clean_file = open(cleaned_file_path, "r", encoding="UTF8")
    clean_text = clean_file.read()

    # Erase punctuation
    clean_text = re.sub(r"[^\w\s]", " ", clean_text)

    file.close()

    with open(cleaned_file_path, "w", encoding="UTF8") as file:
        file.write(clean_text)

print(president_names)

#### PART 2 #####

def count_word_occurrences(text):
    """
    Calculate the number of occurrences of each word in a text.
    :param text: str
    :return: dict
    """
    words = re.findall(r'\b\w+\b', text)
    return dict(Counter(words))

def calculate_idf_scores(directory):
    """
    Calculate IDF scores for each word in a corpus.
    :param directory: str - Path to the directory containing text files.
    :return: dict
    """
    file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    document_count = len(file_list)
    word_document_frequency = Counter()

    for file_name in file_list:
        with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
            text = file.read()
            words = set(re.findall(r'\b\w+\b', text))  # Use a set to avoid counting duplicates in the same document
            word_document_frequency.update(words)

    idf_scores = {
        word: math.log10(document_count / frequency)
        for word, frequency in word_document_frequency.items()
    }
    return idf_scores

def calculate_tf_idf_matrix(directory):
    """
    Generate the TF-IDF matrix for the corpus.
    :param directory: str - Path to the directory containing text files.
    :return: dict, list - A dictionary mapping words to their row index in the matrix, and the matrix itself.
    """
    file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    idf_scores = calculate_idf_scores(directory)

    unique_words = set()
    file_word_counts = []

    for file_name in file_list:
        with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
            text = file.read()
            word_counts = count_word_occurrences(text)
            unique_words.update(word_counts.keys())
            file_word_counts.append(word_counts)

    unique_words = sorted(unique_words)
    word_index = {word: idx for idx, word in enumerate(unique_words)}
    matrix = [[0] * len(file_list) for _ in range(len(unique_words))]

    for col, word_counts in enumerate(file_word_counts):
        for word, count in word_counts.items():
            if word in idf_scores:
                row = word_index[word]
                tf = count
                idf = idf_scores[word]
                matrix[row][col] = tf * idf

    return word_index, matrix, file_list

def list_least_important_words(directory):
    
    word_index, tf_idf_matrix, _ = calculate_tf_idf_matrix(directory)
    least_important_words = []

    for word, row in word_index.items():
        if all(value == 0 for value in tf_idf_matrix[row]):
            least_important_words.append(word)

    return least_important_words

def highest_tf_idf_words(directory):
    word_index, tf_idf_matrix, file_list = calculate_tf_idf_matrix(directory)
    max_value = -1
    max_words = []

    for word, row in word_index.items():
        max_score = max(tf_idf_matrix[row])
        if max_score > max_value:
            max_value = max_score
            max_words = [word]
        elif max_score == max_value:
            max_words.append(word)

    return max_words

def most_repeated_by_chirac(directory):
    chirac_file = next((f for f in os.listdir(directory) if "Chirac" in f), None)
    if chirac_file:
        with open(os.path.join(directory, chirac_file), 'r', encoding='utf-8') as file:
            word_counts = count_word_occurrences(file.read())
        max_count = max(word_counts.values())
        return [word for word, count in word_counts.items() if count == max_count]
    return []

def presidents_mentioning_nation(directory):
    word = "nation"
    mentions = {}

    for file_name in os.listdir(directory):
        with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
            text = file.read()
            word_count = count_word_occurrences(text).get(word, 0)
            if word_count > 0:
                president = file_name.split("Nomination_")[1].split(".")[0]
                mentions[president] = word_count

    max_mentions = max(mentions.values(), default=0)
    max_president = [president for president, count in mentions.items() if count == max_mentions]
    return mentions.keys(), max_president

def first_to_mention_climate(directory):
    keywords = {"climat", "ecologie"}

    for file_name in sorted(os.listdir(directory)):
        with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
            text = file.read()
            if any(word in text for word in keywords):
                return file_name.split("Nomination_")[1].split(".")[0]
    return None

def common_words(directory):
    word_index, tf_idf_matrix, file_list = calculate_tf_idf_matrix(directory)
    common = []

    for word, index in word_index.items():
        isCommon = True
        for file_name in file_list:
            with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
                if ' '+word+' ' not in file.read():
                    isCommon = False
        if isCommon:
            common.append(word)

    return common

#### FEATURES ####

def least_important(directory):
    return list_least_important_words(directory)

#### MENU ####

# Create the GUI application
app = tkinter.Tk()
app.geometry("640x480")
app.title("Menu")

# Functions for menu options
def display_list_least_important_words():
    words = list_least_important_words("cleaned")
    print("Words of least importance:", words)

def display_highest_tf_idf():
    words = highest_tf_idf_words("cleaned")
    print("Word(s) with the highest TF-IDF score:", words)

def display_most_repeated_by_chirac():
    words = most_repeated_by_chirac("cleaned")
    print("Most repeated word(s) by President Chirac:", words)

def display_nation_mentions():
    all_presidents, max_president = presidents_mentioning_nation("cleaned")
    print("Presidents mentioning 'Nation':", list(all_presidents))
    print("President mentioning 'Nation' the most:", max_president)

def display_first_climate_mention():
    president = first_to_mention_climate("cleaned")
    print("First president to mention 'climat' or 'écologie':", president)

def display_common_words():
    words = common_words("cleaned")
    print("Common words mentioned by all presidents:", words)

# Menu widgets
mainmenu = tkinter.Menu(app)
app.geometry("400x300")

mainmenu.add_command(label="Show least important words", command=display_list_least_important_words)
mainmenu.add_command(label="Show Highest TF-IDF", command=display_highest_tf_idf)
mainmenu.add_command(label="Most Repeated by Chirac", command=display_most_repeated_by_chirac)
mainmenu.add_command(label="Nation Mentions", command=display_nation_mentions)
mainmenu.add_command(label="First Mention of Climate", command=display_first_climate_mention)
mainmenu.add_command(label="Common Words", command=display_common_words)
mainmenu.add_command(label="Exit", command=app.destroy)
app.config(menu=mainmenu)

app.mainloop()
