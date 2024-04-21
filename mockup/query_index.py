from porter2stemmer import Porter2Stemmer

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# documents list for user input
docs=set()

# creating the index in memory
def create_index_from_file(filename):
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
                    # docID = int(docID) -> remove this line
                    positions = [int(pos) for pos in positions_str.split(',')]
                    postings_list.append([docID, positions])
                postings_index[term] = postings_list
        print("Index created successfully!")
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
    The transformations performed on words of the collection, such as stemming, lowercasing, removing stopwords, and eliminating non-alphanumeric characters will be performed on the query as well. So, querying for computer or Computer is basically the same.
    '''
    # get input from the user
    user_input = input("Search: ")
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
    return stemmed_list, query_type

def get_docs_list_for_owq_and_ftq(terms, docs):
    # It’s like evaluating a OWQ for every query term, and taking the union of the results
    for term in terms:
        try:
            termDocs=[posting[0] for posting in postings_index[term]]
            docs |= set(termDocs)
        except:
            #term is not in index
            pass
    return list(docs)

def get_docs_list_for_pq(terms, docs):
    for term in terms:
        try:
            termDocs=[posting[0] for posting in postings_index[term]]
            if len(docs) == 0:
                docs = set(termDocs)
            else:
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
    return result

index_file = 'index.txt'
postings_index = create_index_from_file(index_file)
terms, query_type = get_query_from_user()

if query_type == "OWQ" or query_type == "FTQ":
    docs = get_docs_list_for_owq_and_ftq(terms, docs)
elif query_type == "PQ":
    docs = get_docs_list_for_pq(terms, docs)
else:
    print("unknown query type")

print("result", docs)