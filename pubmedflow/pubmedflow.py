"""
    This class is to implement the core pubmed functions, download the articles and query based on keywords
    @author: Aaditya(Ankit) <aadityaura@gmail.com>
    @date created: 27/06/2022
    @date last modified: 02/08/2022
"""

import random
import requests
from pathlib import Path
import pandas as pd
import json
import uuid
from tqdm import tqdm
from .utils import *
from datetime import date
from metapub import FindIt
from bs4 import BeautifulSoup
from scidownl import scihub_download
from datetime import date



class LazyPubmed(object):

    def __init__(self, folder_name='pubmed_data', api_key=''):

        # creating folders for storing data
        # ---------------------------------------------------------

        self.folder_uuid = str(uuid.uuid4())
        self.folder_name = folder_name
        self.raw_pdf_path = f'{self.folder_name}/{self.folder_uuid}/raw_pdfs/'
        self.final_df = f'{self.folder_name}/{self.folder_uuid}/final_df/'
        self.raw_abs_path = f'{self.folder_name}/{self.folder_uuid}/raw_abstracts/'
        self.meta_data_path = f'{self.folder_name}/{self.folder_uuid}/meta_data/'
        self.xml2pdf_path = f'{self.folder_name}/{self.folder_uuid}/xml2df/'
        self.key = api_key

        Path(self.raw_pdf_path).mkdir(parents=True,
                                      exist_ok=True)
        Path(self.raw_abs_path).mkdir(parents=True,
                                      exist_ok=True)
        Path(self.meta_data_path).mkdir(parents=True,
                                        exist_ok=True)
        Path(self.xml2pdf_path).mkdir(parents=True,
                                      exist_ok=True)
        Path(self.final_df).mkdir(parents=True,
                                  exist_ok=True)
        # ---------------------------------------------------------
        self.user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36 OPR/88.0.4412.27',
        ]


    def pubmed_download(self, query,
                        max_documents=None,
                        download_pdf=True,
                        scihub=False,
                        ):
        """function to fetch ids, fetch abstracts and fetch respective pdf files"""

        fetch_ids = fetch(self,query, max_documents=max_documents)
        final_df = xml2df(self.raw_abs_path, self.xml2pdf_path)
        final_df = final_df[final_df['pmid'].notna()]
        final_df['pmid'] = final_df['pmid'].apply(lambda x: int(x))

        pids = list(set(list(final_df['pmid'])))

        if download_pdf:
            get_pdf(self,pids, save=True, scihub=scihub)
            dart = get_final_data(self.raw_pdf_path)
            dart = dart[dart['pmid'].notna()]
            dart['pmid'] = dart['pmid'].apply(lambda x: int(x))
            final_df = pd.merge(final_df, dart, on='pmid', how='left')

        final_df.to_csv(f'{self.final_df}final_df.csv')
        return final_df

    def pubmed_qa(self, title_query,
                  qa_query, max_documents=None,
                  download_pdf=True,
                  scihub=False):
        final_df = self.pubmed_download(title_query, max_documents=max_documents,
                                        download_pdf=download_pdf,
                                        scihub=scihub)
        from nfmodelapis.text.question_answering import QAPipeline
        pipe = QAPipeline(final_df)
        res = pipe.batch_qa(qa_query, 'pdf_content')
        return res

    def pubmed_summarize(self,
                         title_query,
                         max_documents=None,
                         download_pdf=True,
                         scihub=False):
        final_df = self.pubmed_download(title_query, max_documents=max_documents,
                                        download_pdf=download_pdf,
                                        scihub=scihub)
        from nfmodelapis.text.summarization import SummarizationPipeline
        pipe = SummarizationPipeline(final_df)
        res = pipe.batch_summarize('pdf_content')
        return res
