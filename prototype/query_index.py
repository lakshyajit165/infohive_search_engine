from porter2stemmer import Porter2Stemmer
import json
import os
import math
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import time
import concurrent.futures

# documents list for user input
docs=set()
# percentage multiplier for rank docs' scores
# eg, if results contain 10 docs with scores 1-10, the result list will
# contain docs with ranks >= 6 only
RANK_THRESHOLD_FOR_SEARCH = 0.6

# creating the index in memory
def create_index_from_file(filename):
    start_time = time.time()
    postings_index = {}
    try:
        with open(filename, 'r') as file:
            # Iterate over each line in the file
            for line in file:
                term, postings_str = line.strip().split('|')
                postings_list = []
                # Split postings list by ';'
                for posting in postings_str.split(';'):
                    docID, positions_str = posting.split(':')
                    positions = [int(pos) for pos in positions_str.split(',')]
                    postings_list.append([docID, positions])
                postings_index[term] = postings_list
        print("Index created successfully!")
        end_time = time.time()
        print(f"create_index_from_file took {end_time - start_time:.6f} seconds.")
        return postings_index
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

'''
Query Types
Let's first remember the query types. Our search engine is going to answer 3 types of queries that we generally use while searching.
1) One Word Queries (OWQ): OWQ consist of only a single word. Such as computer, or university. The matching documents are the ones containing the single query term.
2) Free Text Queries (FTQ): FTQ contain sequence of words separated by space like an actual sentence. Such as computer science, or Brown University. The matching documents are the ones that contain any of the query terms.
3) Phrase Queries (PQ): PQ also contain sequence of words just like FTQ, but they are typed within double quotes. The meaning is, we want to see all query terms in the matching documents, and exactly in the order specified. Such as “Turing Award”, or “information retrieval and web search”.
'''
def determine_query_type(query):
    if '"' in query and query.count('"') == 2 and query[0] == '"' and query[-1] == '"':
        return 'PQ'  # Phrase Query
    elif ' ' in query:
        return 'FTQ'  # Free Text Query
    else:
        return 'OWQ'  # One Word Query
    
def get_query_from_user():
    tokenizer = RegexpTokenizer(r'\w+')
    stemmer = Porter2Stemmer()  
    '''
    The transformations performed on words of the collection, such as stemming, lowercasing, removing stopwords, 
    and eliminating non-alphanumeric characters will be performed on the query as well. 
    So, querying for computer or Computer is basically the same.
    '''
    # get input from the user
    user_input = input("Search: ")
    start_time = time.time()
    # determine the query type
    query_type = determine_query_type(user_input)
    # lower case the strings
    text = user_input.lower()
    # # Get all tokens, where a token is a string of alphanumeric characters terminated by a non-alphanumeric character.
    tokens_list = tokenizer.tokenize(text)
    # Remove all the english stop words such as 'a', 'an', 'the' etc
    filtered_tokens_list = [word for word in tokens_list if word not in stopwords.words('english')]
    # stem the filtered token list
    stemmed_list = [stemmer.stem(word) for word in filtered_tokens_list]
    end_time = time.time()
    print(f"get_query_from_user took {end_time - start_time:.6f} seconds.")
    return stemmed_list, query_type

def get_docs_list_for_owq_and_ftq(terms, docs):
    start_time = time.time()
    # It’s like evaluating a OWQ for every query term, and taking the union of the results
    for term in terms:
        try:
            termDocs=[posting[0] for posting in postings_index[term]]
            # take a union of all the matching docs
            docs |= set(termDocs)
        except:
            #term is not in index
            pass
    end_time = time.time()
    print(f"get_docs_list_for_owq_and_ftq took {end_time - start_time:.6f} seconds.")
    return list(docs)

def get_docs_list_for_pq(terms, docs):
    start_time = time.time()
    for term in terms:
        try:
            termDocs=[posting[0] for posting in postings_index[term]]
            if len(docs) == 0:
                docs = set(termDocs)
            else:
                # take an intersection of all the matching docs
                docs &= set(termDocs)
        except:
            #term is not in index
            pass
    docs = list(docs)
    result = []
    # now check if the order is correct or not
    for doc in docs:
        query_term_position_list = []
        for term in terms:
            try:
                postings_list = postings_index[term]
                for posting in postings_list:
                    if posting[0] == doc:
                        query_term_position_list.append(posting[1])
            except:
                pass
        # print("query term position list", query_term_position_list)
        # perform subtractions
        query_term_position_list_after_sub = []
        for i, sublist in enumerate(query_term_position_list):
            new_sublist = []
            for x in sublist:
                new_element = x - i
                new_sublist.append(new_element)
            query_term_position_list_after_sub.append(new_sublist)

        # print("query term position list after subtraction", query_term_position_list_after_sub)
        # Convert each sublist into a set
        sets = [set(sublist) for sublist in query_term_position_list_after_sub]

        # Find the intersection of all sets
        list_intersection = set.intersection(*sets)
        if len(list_intersection) != 0:
            result.append(doc)
    end_time = time.time()
    print(f"get_docs_list_for_pq took {end_time - start_time:.6f} seconds.")
    return result

def get_doc_vector_space():
    start_time = time.time()
    try:
        with open("doc_vector_space.txt", 'r') as file:
            data = json.load(file)
            end_time = time.time()
            print(f"get_doc_vector_space took {end_time - start_time:.6f} seconds.")
            return data
    except:
        print("Error fetching total terms per file")

def rank_documents(terms, docs):
    start_time = time.time()
    # return empty list, if docs length is 0
    if len(docs) == 0:
        return []
    
    doc_rank_map = {}
    document_scores = {}
    for doc in docs:
        rank_meta_data = {}
        normalized_term_freq = []
        inverse_doc_freq = []
        for term in terms:
            # calculate Normalized term frequency(TF) for all the terms
            # get the total no of terms in the doc
            total_terms = doc_vector_space_map[doc]
            # get the term frequency,  in this doc
            if term not in postings_index:
                continue
            list_of_docs_for_term = postings_index[term]
            # print("list of docs for term", doc, term, list_of_docs_for_term)
            # term_freq_for_doc = len([element for element in list_of_docs_for_term if element[0] == doc])
            term_freq_for_doc = 0
            for doc_and_freq in list_of_docs_for_term:
                if doc_and_freq[0] == doc:
                    term_freq_for_doc = len(doc_and_freq[1])
                    break

            TF = term_freq_for_doc / total_terms
            # print("Doc, term, TF and total_terms", doc, term, term_freq_for_doc, total_terms)
            normalized_term_freq.append(TF)
            # now calculate the inverse doc frequency for this term
            term_freq_in_corpus = len(postings_index[term])
            total_docs_in_corpus = len(doc_vector_space_map)
            # check if total_docs_in_corpus / term_freq_in_corpus == 1
            if total_docs_in_corpus == term_freq_in_corpus: # it means the input term is present in all the documents
                IDF = 1 # because log 1 will be 0
            else:
                IDF = math.log(total_docs_in_corpus / term_freq_in_corpus)
            # print("Doc, term, IDF", doc, term, IDF)
            inverse_doc_freq.append(IDF)
        rank_meta_data["TF"] = normalized_term_freq
        rank_meta_data["IDF"] = inverse_doc_freq
        doc_rank_map[doc] = rank_meta_data
    
    for doc, tf_idf in doc_rank_map.items():
        score = 0
        for i in range(len(tf_idf['TF'])):
            score += tf_idf['TF'][i] * tf_idf['IDF'][i]
        document_scores[doc] = score

    max_score = max(document_scores.values())
    # Sort documents based on combined scores in descending order
    sorted_documents = [
        {"document": doc, "score": score} 
        for doc, score in sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        if score >= RANK_THRESHOLD_FOR_SEARCH * max_score
    ]
    end_time = time.time()
    print(f"rank_documents took {end_time - start_time:.6f} seconds.")
    return sorted_documents

def get_doc_metadata(ranked_docs):
    start_time = time.time()
    snippets = {}
    source_dir = "source_files"
    
    for doc_id in ranked_docs:
        try:
            with open(os.path.join(source_dir, doc_id), 'r', encoding='utf-8') as file:
                data = json.load(file)
                url = data.get('url', '')
                title = data.get('title', '')
                content = data.get('content', '')[:250]
                
                snippets[doc_id] = {
                    "doc_id": doc_id,
                    "metadata": {
                        "title": title,
                        "url": url,
                        "content": content
                    }
                }
        except FileNotFoundError:
            print(f"File not found: {doc_id}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {doc_id}")
        except Exception as e:
            print(f"Error reading file {doc_id}: {e}")
    end_time = time.time()
    print(f"get_doc_metadata took {end_time - start_time:.6f} seconds.")
    return snippets


index_file = 'index.txt'
# get input from user
terms, query_type = get_query_from_user()

start_time = time.time()
# create the index and vector_space_map in memory parallely
# because they are separate files
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit the functions to the executor
    future_index = executor.submit(create_index_from_file, index_file)
    future_doc_vector = executor.submit(get_doc_vector_space)

    # Wait for all futures to complete and get the results
    postings_index = future_index.result()
    doc_vector_space_map = future_doc_vector.result()

print("processed input terms", terms)
if query_type == "OWQ" or query_type == "FTQ":
    docs = get_docs_list_for_owq_and_ftq(terms, docs)
elif query_type == "PQ":
    docs = get_docs_list_for_pq(terms, docs)
else:
    print("unknown query type")

''' now we have the "docs" list i.e the list of documents in which our input terms appear. 
We can run the "rank_documents" method and another method "get_doc_metadata" in
parallel which will fetch the relevant snippets for each document
'''
# now that we have the doc list, we need to rank the docs based on TF-IDF
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit the functions to the executor
    future_ranked_docs = executor.submit(rank_documents, terms, docs)
    future_metadata_per_doc = executor.submit(get_doc_metadata, docs)

    # Wait for all futures to complete and get the results
    ranked_docs = future_ranked_docs.result()
    metadata_per_doc = future_metadata_per_doc.result()


for ranked_doc in ranked_docs:
    # ranked_doc['metadata'] = metadata_per_doc[ranked_doc['document']]
    response = metadata_per_doc[ranked_doc['document']]['metadata']
    response['score'] = ranked_doc['score']
    print(response)
    print()

end_time = time.time()
print(f"Returned {len(ranked_docs)} results in {end_time - start_time:.6f} seconds.")






