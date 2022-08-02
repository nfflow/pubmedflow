"""
    This class is to implement the core pubmed functions, download the articles and query based on keywords
    @author: Aaditya(Ankit) <aadityaura@gmail.com>
    @date created: 27/06/2022
    @date last modified: 02/08/2022
"""

import shutup
import random
import requests
from pathlib import Path
import pandas as pd
import json
import uuid
from tqdm import tqdm
from .utils import *
from metapub import FindIt
from bs4 import BeautifulSoup
from scidownl import scihub_download


shutup.please()


class LazyPubmed(object):

    def __init__(self):

        # creating folders for storing data
        # ---------------------------------------------------------

        self.folder_uuid = str(uuid.uuid4())
        self.raw_pdf_path = f'Pubmed_data/{self.folder_uuid}/raw_pdfs/'
        self.final_df = f'Pubmed_data/{self.folder_uuid}/final_df/'
        self.raw_abs_path = f'Pubmed_data/{self.folder_uuid}/raw_abstracts/'
        self.meta_data_path = f'Pubmed_data/{self.folder_uuid}/meta_data/'
        self.xml2pdf_path = f'Pubmed_data/{self.folder_uuid}/xml2df/'

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

    def request_head(self, url):
        """Request function for urls"""

        headers = requests.utils.default_headers()
        headers['User-Agent'] = random.choice(self.user_agent_list)
        r = requests.get(url, headers=headers,
                         allow_redirects=True,
                         verify=False)
        return r

    def pdf_links(self, pmid):
        """Get pdf links from Pubmed website"""


        data = {}
        url                   = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        url_request           = self.request_head(url)
        soup                  = BeautifulSoup(url_request.text,'html.parser')
        
        try:
            full_text_class       = soup.find_all("div", {"class": "full-text-links"})
            full_content          = full_text_class[0].find_all("div", {"class": "full-text-links-list"})
            all_links             = full_content[0].findAll("a", href=True)

            for single_link in all_links:
                data[single_link.text.strip()] = single_link['href']
            return data
        except Exception as e:
            return {'data': None}


    def get_date(self):
        currentDate = date.today()
        today       = currentDate.strftime('%Y/%m/%d')
        return today

        
    def pmc(self, url):
        """Download pdf from pmc website"""
        
        url_request           = self.request_head(url)
        soup                  = BeautifulSoup(url_request.text,'html.parser')
        full_text_class       = soup.find_all("ul", {"class": "pmc-sidebar__formats"})
        link_                 = full_text_class[0].find_all("li", {"class": "pdf-link other_item"})[0].findAll("a", href=True)[0]
        link_url              = f"https://www.ncbi.nlm.nih.gov{link_['href']}"
        
        return link_url
    
    
    def save_pdf(self, pmid, pdf_url):
        """save pdf in local folder"""
        
        pdf_request = self.request_head(pdf_url)
        with open(f'{self.raw_pdf_path}{pmid}.pdf', 'wb') as f:
            f.write(pdf_request.content)
        return 0
    
    def scihub_mode(self, pmid):
        """scihub search"""
        
        paper_type = "pmid"
        out        = f'{self.raw_pdf_path}{pmid}.pdf'
        scihub_download(pmid, paper_type = paper_type, out=out)
        
    
    def download_pdf(self, pmids, save = False, scihub = True):
        """Main function to download and search pdfs -> save in local folder"""
        
        downloadble_url = {}
        not_downloaded  = {}
        

        pdf_count       = len(pmids)
        print(f"Total pdf downloading : {pdf_count}.. \n")

        
        for pmid in tqdm(pmids):
            
            try:
                pdf_source = self.pdf_links(pmid)
                if 'Free PMC article' in pdf_source.keys():
                    pdf_url = self.pmc(pdf_source['Free PMC article'])
                    downloadble_url[pmid] = pdf_url
                    if save:
                        self.save_pdf(pmid, pdf_url)
                            
                else:
                    if FindIt(pmid).url:
                        print("saving from findit")
                        findit_url = FindIt(pmid).url
                        self.save_pdf(pmid, findit_url)
                        downloadble_url[pmid] = findit_url

                    elif scihub:
                        print("saving from scihub")
                        self.scihub_mode(pmid)
                        downloadble_url[pmid] = 'sci_hub'
                    else:
                        not_downloaded[pmid] = pdf_source
            
            
            except Exception as e:
                pass
        
        
        return json.dumps({
                'downloaded'    : downloadble_url, 
                'not_downloaded': not_downloaded
               }, indent = 3)
    

    def get_date(self):
        currentDate = date.today()
        today       = currentDate.strftime('%Y/%m/%d')
        return today


    def write_json(self, path_name, data, name):
        """Write json data"""

        with open(f'{path_name}{name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return 0


    def get_records(self, query = None):
        """get fetch result and ids from ncbi website using api"""
        
        
        if query:
            search_url    = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?sort=relevance&db=pubmed&term={query}&mindate=1800/01/01&maxdate={self.get_date()}&usehistory=y&retmode=json"
        else:
            search_url    = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&mindate=1800/01/01&maxdate={self.get_date()}&usehistory=y&retmode=json"

        search_r      = requests.post(search_url, verify = False)
        search_data   = search_r.json()

        webenv        = search_data["esearchresult"]['webenv']
        total_records = int(search_data["esearchresult"]['count'])

        return {'total_records': total_records, 
                'webenv'       : webenv, 
                'search_data'  : search_data}


    def fetch(self, query,
                    key, 
                    max_documents = None):
        """main function to do multi task -> fetch ids, based on ids fetch abstracts"""
        
        
        all_records = self.get_records(query)
        webenv      = all_records['webenv']
        all_rec     = all_records['total_records']
        
        if max_documents:
            all_rec   = max_documents
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&api_key={key}&retmax={max_documents}&retmode=xml&query_key=1&webenv="+webenv
        else:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&api_key={key}&retmax=9999&retmode=xml&query_key=1&webenv="+webenv
        
        print("-------------------------------------------\n")
        print(f" Fetching total documents -> {all_rec}..\n")
        print("-------------------------------------------\n")

        for i in tqdm(range(0, all_rec, 10000)):
            try:
                meta_data = {}
                u_id      = str(uuid.uuid4())
                payload   = fetch_url+"&retstart="+str(i)
                
                print(f"Getting this URL: {payload} \n")
                
                fetch_r = requests.post(payload, verify = False)
                pre_name = f'{self.raw_abs_path}/pubmed_batch_{u_id}_{str(i)}_to_{str(i+all_rec)}.xml'
                
                f = open(pre_name, 'wb')
                f.write(fetch_r.content)
                f.close()
                
                meta_data['uid']    = u_id
                meta_data['query']  = query
                meta_data['url']    = payload
                meta_data['total']  = all_rec
                meta_data['iter']   = i
                
                self.write_json(self.meta_data_path, meta_data, u_id)
                
            except Exception as e:
                with open('exceptions','a') as f:
                    f.write(f" featch_1_fetch_exception {e} number {i} \n")
                pass
            
        return 0
    
    
    def pubmed_search(self, query, key,
                      max_documents = None, 
                      download_pdf  = True, 
                      scihub        = False):
        """function to fetch ids, fetch abstracts and fetch respective pdf files"""

        fetch_ids        = self.fetch(query, key,
                                      max_documents = max_documents)
        final_df         = xml2df(self.raw_abs_path, self.xml2pdf_path)
        final_df         = final_df[final_df['pmid'].notna()]
        final_df['pmid'] = final_df['pmid'].apply(lambda x: int(x))




        pids      = list(set(list(final_df['pmid'])))

        if download_pdf:
            self.download_pdf(pids, save = True, scihub = scihub)
            dart             = get_final_data(self.raw_pdf_path)
            dart             = dart[dart['pmid'].notna()]
            dart['pmid']     = dart['pmid'].apply(lambda x: int(x))
            final_df         = pd.merge(final_df, dart, on = 'pmid', how = 'left')

        
        final_df.to_csv(f'{self.final_df}final_df.csv')
        return final_df
