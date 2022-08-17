<h2 align="center">PUBMED-FLOW </h2>
<h3 align="center"> Open source data collection tool to fetch data from pubmed</h3>
<p align="center"> Contribute and Support </p>


[![License:MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub commit](https://img.shields.io/github/last-commit/nfflow/pubmedflow)](https://github.com/nfflow/pubmedflow/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Open All Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1mjlnHAb7aqwfDEylo05z3RdIyyaNRoQ5?usp=sharing)


### 🎮 Features

- fetch pubmed ids (pmids) based on keyword query (supports multiple keywords query)
- Fetch Abstract of research papers from pubmed based on pmids
- Download the full pdf of respective pmid -> if available on pubmedcentral (pmc)
- if pdf not available on pmc -> download from scihub internally


### How to obtain ncbi key?

- Follow this [tutorial](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/#:~:text=To%20create%20the%20key%2C%20go,and%20copy%20the%20resulting%20key)

### How to use api?

Arguments:   
Name | Input | Description 
 ----------- | ----------- |  -----------
folder_name | Optional, str | path to store output data 


### Quick Start

#### Download pubmed articles as PDF and DataFrame -

```python

import eutils
from pubmedflow import LazyPubmed


pb        = LazyPubmed(folder_name=folder_name)
df_result = pb.pubmed_download(query         = 'Chronic',
                             key           = "api_key",
                             max_documents = 2,
                             download_pdf  = True, 
                             scihub        = False)
                    
```
#### Download articles and do question answering on the downloaded text to get answer spans from each article:

```python

import eutils
from pubmedflow import LazyPubmed


pb        = LazyPubmed(folder_name=folder_name)
qa_results = pb.pubmed_qa(title_query = 'Chronic',
                          qa_query = 'What are the chronic diseases',
                          key      = "api_key",
                          max_documents = 2,
                          download_pdf  = True, 
                          scihub        = False)
 print(qa_results)
 ```
 
 #### Download articles and summarise each of them
 
 ```python
 
import eutils
from pubmedflow import LazyPubmed


pb        = LazyPubmed(folder_name=folder_name)
summ_results = pb.pubmed_summarise(title_query='Chronic',
                                  qa_query='What are the chronic diseases',
                                  key= "api_key",
                                  max_documents = 2,
                                  download_pdf = True, 
                                  scihub = False)
 print(summ_results)
 ```
 



