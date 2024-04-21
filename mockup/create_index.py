import os
from porter2stemmer import Porter2Stemmer

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

'''
While parsing the articles we will perform the following operations on each page in this order:
1) Concatenate the title and the text of the page(initially we only have text files).
2) Lowercase all words.
3) Get all tokens, where a token is a string of alphanumeric characters terminated by a non-alphanumeric character. The alphanumeric characters are defined to be [a-z0-9]. So, the tokens for the word 'apple+orange' would be 'apple' and 'orange'.
4) Filter out all the tokens that are in the stop words list, such as 'a', 'an', 'the'.
5) Stem each token using to finally obtain the stream of terms. Porter Stemmer removes common endings from words. For example the stemmed version of the words fish, fishes, fishing, fisher, fished are all fish.

'''

# Directory containing the source files
source_folder = "source_files"

# List to store collected text from all files
collected_text = []

tokenizer = RegexpTokenizer(r'\w+')
stemmer = Porter2Stemmer()
# doc_id = 0 -> remove this line
postings_index = {}
index_file = "index.txt"

def create_index_file(postings_index, filename):
    try:
        with open(filename, 'w') as file:
            for term, postings_list in postings_index.items():
                file.write(term + '|')
                for i, posting in enumerate(postings_list):
                    docID, positions = posting
                    file.write(f'{docID}:{",".join(map(str, positions))}')
                    if i < len(postings_list) - 1:
                        file.write(';')
                file.write('\n')
        print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def create_postings_index(postings_index_map):
    for key, value in postings_index_map.items():
        if key not in postings_index:
            postings_index[key] = [value]
        else:
            postings_index[key].append(value)

def create_postings_map_per_file(doc_id, stemmed_list):
    postings_index_map = {}
    for i in range(len(stemmed_list)):
        if stemmed_list[i] not in postings_index_map:
            positions_list = []
            positions_list.append(i)
            postings_index_map[stemmed_list[i]] = [doc_id, positions_list]
        else:
            postings_index_map[stemmed_list[i]][1].append(i)

    return postings_index_map


for filename in os.listdir(source_folder):
    filepath = os.path.join(source_folder, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # doc_id += 1 -> remove this line
            # Read text from the file and append to the list
            text = file.read()
            # lower case the strings
            text = text.lower()
            # # Get all tokens, where a token is a string of alphanumeric characters terminated by a non-alphanumeric character.
            tokens_list = tokenizer.tokenize(text)
            # Remove all the english stop words such as 'a', 'an', 'the' etc
            filtered_tokens_list = [word for word in tokens_list if word not in stopwords.words('english')]
            # stem the filtered token list
            stemmed_list = [stemmer.stem(word) for word in filtered_tokens_list]
            print(filename, stemmed_list)
            postings_index_map = create_postings_map_per_file(filename, stemmed_list)
            create_postings_index(postings_index_map)
            
            
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

create_index_file(postings_index, index_file)
print(postings_index)
