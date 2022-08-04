<h2 align="center">PUBMED-FLOW </h2>
<h3 align="center"> Open source data collection tool to fetch data from pubmed</h3>
<p align="center"> Contribute and Support </p>


[![License:MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub commit](https://img.shields.io/github/last-commit/nfflow/pubmedflow)](https://github.com/nfflow/pubmedflow/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

### Features

- fetch pubmed ids (pmids) based on keyword query (supports multiple keywords query)
- Fetch Abstract of research papers from pubmed based on pmids
- Download the full pdf of respective pmid -> if available on pubmedcentral (pmc)
- if pdf not available on pmc -> download from scihub internally


### How to obtain ncbi key?

- Follow this [tutorial](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/#:~:text=To%20create%20the%20key%2C%20go,and%20copy%20the%20resulting%20key)

### How to use api?

Sample query :   
```

from pubmedflow import LazyPubmed
pb        = LazyPubmed()

result    = pb.fetch(query = "lncRNA",
                    key = "your_api_key", 
                    max_documents = 5)
                    
```



