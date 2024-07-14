import os
import json
import math
import time
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

postings_index = {}
index_file = "index.txt"

def update_doc_vector_space(filename, terms_list):
    ''' 
    Note:
    1. First we contruct a vector space for the document -> this is basically a frequency list of the unique terms in the document. We need to calculate and store || D || (magnitude) for each of these documents. This can be calculated  as the square root of the sum of the squares of its components. 

    2. In this implementation we are maintaining a json structure of filename and total terms per file. So if the file doc_vector_space.txt is empty, we write an empty object to the file first'''

    path = "doc_vector_space.txt"
    try:
        # first create a hashmap to store the unique term frequency as a list
        unique_term_freq = {}
        for term in terms_list:
            if term in unique_term_freq:
                unique_term_freq[term] += 1
            else:
                unique_term_freq[term] = 1
        
        '''
        We can use a vector to represent the document in bag of words model, 
        since the ordering of terms is not important.
        There is an entry for each unique term in the document with the value being 
        its term frequency. For the sake of an example, consider the document 
        “computer study computer science”. 
        The vector representation of this document will be of size 3 
        with values [2, 1, 1] corresponding to computer, study, and science respectively. 
        We can indeed represent every document in the corpus as a k-dimensonal vector, 
        where k is the number of unique terms in that document. 
        Each dimension corresponds to a separate term in the document. 
        '''
        # now calculate the vector magnitude
        sum_of_squares = 0
        doc_vector = list(unique_term_freq.values())
        for vector_ele in doc_vector:
            sum_of_squares += (vector_ele * vector_ele)

        # Initialize the dictionary to hold filename and vector magnitude
        data = {}

        # Check if the file exists
        if os.path.exists(path):
            # Read the existing data if the file is not empty
            if os.path.getsize(path) > 0:
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                # If the file is empty, write an empty dictionary {}
                with open(path, 'w') as file:
                    json.dump(data, file)

        # Update the dictionary with the vector magnitude
        data[filename] = math.sqrt(sum_of_squares)

        # Write the updated dictionary back to the file
        with open(path, 'w') as file:
            json.dump(data, file)
        # print("Term frequency updated successfully.")
    except Exception as e:
        print("Error updating term frequency:", e)



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
        # print(f"Data successfully written to {filename}")
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


def process_files():
    for filename in os.listdir(source_folder):
        filepath = os.path.join(source_folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read JSON data from the file
                data = json.load(file)
                # Extract the content attribute
                content = data.get('content', '')
                # Convert content to lower case
                content = content.lower()
                # Tokenize the content
                tokens_list = tokenizer.tokenize(content)
                # Remove all English stop words
                filtered_tokens_list = [word for word in tokens_list if word not in stopwords.words('english')]
                # Stem the filtered token list
                stemmed_list = [stemmer.stem(word) for word in filtered_tokens_list]
                # Update document vector space
                update_doc_vector_space(filename, stemmed_list)
                # Create postings index
                postings_index_map = create_postings_map_per_file(filename, stemmed_list)
                create_postings_index(postings_index_map)
            
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {filename}")
        except Exception as e:
            print(f"Error reading file {filename}: {e}")


start_time = time.time()
process_files()
end_time = time.time()
print(f"process_text_files() took {end_time - start_time:.2f} seconds.")

start_time = time.time()
create_index_file(postings_index, index_file)
end_time = time.time()
print(f"create_index_file() took {end_time - start_time:.2f} seconds.")
# print(postings_index)
