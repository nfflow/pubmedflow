<h2 align="center">PUBMED-FLOW </h2>
<h3 align="center"> Open source data collection tool to fetch data from pubmed</h3>
<p align="center"> Contribute and Support </p>


[![License:MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub commit](https://img.shields.io/github/last-commit/nfflow/pubmedflow)](https://github.com/nfflow/pubmedflow/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Open All Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1mjlnHAb7aqwfDEylo05z3RdIyyaNRoQ5?usp=sharing)


## 🎮 Features

- fetch pubmed ids (pmids) based on keyword query (supports multiple keywords query)
- Fetch Abstract of research papers from pubmed based on pmids
- Download the full pdf of respective pmid -> if available on pubmedcentral (pmc)
- if pdf not available on pmc -> download from scihub internally


## How to obtain ncbi key?

- Follow this [tutorial](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/#:~:text=To%20create%20the%20key%2C%20go,and%20copy%20the%20resulting%20key)

## Installation

### From source
```python
python setup.py install
```
OR
```
pip install git+https://github.com/nfflow/pubmedflow
```

## How to use api?

Arguments:   
Name | Input | Description 
 ----------- | ----------- |  -----------
folder_name | Optional, str | path to store output data 


## Quick Start:

### Download pubmed articles as PDF and DataFrame -

```python

import eutils
from pubmedflow import LazyPubmed


pb        = LazyPubmed(title_query,
                 folder_name='pubmed_data',
                 api_key='',
                 max_documents=None,
                 download_pdf=True,
                 scihub=False)
                    
```

### Perform unsupervised learning to make a pre-trained model from the collected data:

```python
pb.pubmed_train(model_name='sentence-transformers/all-mpnet-base-v2',
                                     model_output_path='pubmedflow_model',
                                     model_architecture='ct')
```

### Do question answering on the downloaded text to get answer spans from each article:

```python

qa_results = pb.pubmed_qa(qa_query = 'What are the chronic diseases',)
 print(qa_results)
 ```
 
 ### Summarise each of them
 
 ```python
 
summ_results = pb.pubmed_summarise()
 print(summ_results)
 ```
 
  ### Perform entity extraction on each of them
 
 ```python
 
ents = pb.pubmed_entity_extraction()
 print(ents)
 ```
 
 



