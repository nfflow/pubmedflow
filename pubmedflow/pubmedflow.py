import shutup
import random
import requests
from lxml import etree
from pathlib import Path
import pubmed_parser as pp
import pandas as pd
import itertools
import os, glob

from tqdm import tqdm
from metapub import FindIt
from bs4 import BeautifulSoup
from scidownl import scihub_download

shutup.please()


class LazyPubmed(object):
    
    def __init__(self):
        
        Path('Pubmed_data/pdfs/').mkdir(parents=True, 
                                 exist_ok=True)
        Path('Pubmed_data/abstracts/').mkdir(parents=True, 
                                 exist_ok=True)

        Path('Pubmed_data/meta_data/').mkdir(parents=True, 
                                 exist_ok=True)

        Path('Pubmed_data/xmldf/').mkdir(parents=True, 
                                 exist_ok=True)
        
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
        
        headers               = requests.utils.default_headers()
        headers['User-Agent'] = random.choice(self.user_agent_list)
        r                     = requests.get(url, headers=headers, 
                                             allow_redirects=True, 
                                             verify = False)
        return r
    
    
    def pdf_links(self, pmid):
        """Get pdf links from Pubmed website"""
        
        
        data                  = {}
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



    def get_records(self, 
                    query       = None, 
                    max_records = None):
                    
        if query:

            if max_records:
                search_url    = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?sort=relevance&db=pubmed&term={query}&retmode=JSON&retmax={max_records}"
            else:
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
        with open(f'Pubmed_data/pdfs/{pmid}.pdf', 'wb') as f:
            f.write(pdf_request.content)
        return 0
    
    def scihub_mode(self, pmid):
        """scihub search"""
        
        paper_type = "pmid"
        out        = f"./Pubmed_data/pdfs/{pmid}.pdf"
        scihub_download(pmid, paper_type = paper_type, out=out)
        
    
    def download_pdf(self, pmids, save = False, scihub = True):
        """Main function to download and search pdfs -> save in local folder"""
        
        downloadble_url = {}
        not_downloaded  = {}
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
                print(e)
        
        
        return json.dumps({
                'downloaded'    : downloadble_url, 
                'not_downloaded': not_downloaded
               }, indent = 3)
    

    def get_date(self):
        currentDate = date.today()
        today       = currentDate.strftime('%Y/%m/%d')
        return today


    def write_json(path_name, data, name):
        """Write json data"""

        with open(f'{path_name}/{name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return 0


    def get_records(query = None):
        
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


    def fetch(key, 
            query = None):
        
        
        all_records = self.get_records(query)
        webenv      = all_records['webenv']
        all_rec     = all_records['total_records']
        
        print(all_rec)
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&api_key={key}&retmax=9999&retmode=xml&query_key=1&webenv="+webenv

        for i in tqdm(range(0, all_rec, 10000)):
            try:
                meta_data = {}
                u_id      = str(uuid.uuid4())
                payload = fetch_url+"&retstart="+str(i)
                print("Getting this URL: ", payload)
                fetch_r = requests.post(payload, verify = False)
                f = open('./Pubmed_data/abstracts/pubmed_batch_'+ u_id + str(i) + '_to_' + str(i+all_rec) + ".xml", 'wb')
                f.write(fetch_r.content)
                f.close()
                meta_data['uid']    = u_id
                meta_data['query']  = query
                meta_data['url']    = payload
                meta_data['total']  = all_rec
                meta_data['iter']   = i
                
                write_json('Pubmed_data/meta_data', meta_data, u_id)
                
            except Exception as e:
                with open('exceptions','a') as f:
                    f.write(f" featch_1_fetch_exception {e} number {i} \n")
                pass
            
        return 0


    def parse_xml(self, file):
        dicts_out = pp.parse_medline_xml(file)
        return dicts_out


    def xml2df(self, dir_name):

        all_files = glob.glob("./Pubmed_data/abstracts/*xml")
        u_id      = str(uuid.uuid4())
        
        df_list = []
        
        try:
            for i in tqdm(all_files):
                raw_df = self.parse_xml(i)
                df     = pd.DataFrame(raw_df)
                df_list.append(df)

            final_df = pd.concat(df_list)
            final_df.to_csv(f'./Pubmed_data/xmldf/{u_id}.csv',index=False)
            final_df   = pd.read_csv(f'./Pubmed_data/xmldf/{u_id}.csv')

        except Exception as e:
            print(e)
            pass
        
        # it will replace blank will NaN now load again and select without NaN
        final_df   = final_df[final_df['abstract'].notna()].reset_index(drop=True)
        final_df.to_csv(f'./Pubmed_data/xmldf/{u_id}.csv',index=False)
        return "saved"