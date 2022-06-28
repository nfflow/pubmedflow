from pubmedflow import LazyPubmed
pb        = LazyPubmed()

result    = pb.fetch(query = "lncRNA",
                    key = "your_api_key", 
                    max_documents = 5)