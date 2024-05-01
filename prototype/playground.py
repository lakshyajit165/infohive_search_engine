doc = 'Replication And Sharding.txt'

list_of_docs_for_term = [['Availability.txt', [56]], ['Proxies.txt', [50, 80]], ['MapReduce.txt', [93]], ['Network Protocols.txt', [50, 80]], ['Configuration.txt', [70]], ['Publish_Subscribe Pattern.txt', [156]], ['Hashing.txt', [66]], ['Relational Databases.txt', [11, 26, 28, 29, 56, 61, 73, 109, 192, 195, 209, 212, 214, 216, 224, 228, 234, 243, 244, 252, 257, 261, 262, 270, 287, 328, 335, 351, 358, 369, 409, 422]], ['Caching.txt', [138]], ['Load Balancers.txt', [53]], ['Rate Limiting.txt', [39]], ['Key-Value Stores.txt', [33, 36, 50, 53, 55, 57, 65, 69, 78]], ['Security And HTTPS.txt', [54, 84]], ['Leader Election.txt', [107]], ['Client—Server Model.txt', [46, 76]], ['Storage.txt', [12, 27, 28, 55, 60, 72, 108]], ['Specialized Storage Paradigms.txt', [9, 12, 26, 29, 31, 33, 41, 45, 51, 60, 61, 69, 74, 78, 79, 92, 105, 112, 128, 135, 146, 156, 177, 217, 266, 270, 290, 292, 302, 312, 326, 331, 353, 358, 378, 388, 390, 400, 620, 627, 635]], ['Replication And Sharding.txt', [4, 137, 138, 165, 170, 182, 218, 247, 280, 289]]]

term_freq_for_doc = 0
for doc_and_freq in list_of_docs_for_term:
    if doc_and_freq[0] == doc:
        term_freq_for_doc = len(doc_and_freq[1])
        break;

print(term_freq_for_doc)