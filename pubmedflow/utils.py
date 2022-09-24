"""
    This class is to implement the util functions for pubmed main class
    @author: Aaditya(Ankit) <aadityaura@gmail.com>
    @date created: 27/06/2022
    @date last modified: 02/08/2022
"""
import re
import pubmed_parser as pp
import pandas as pd
from tqdm import tqdm
import io
import uuid
import glob

from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter

import random
import requests

import json

from datetime import date
from metapub import FindIt
from bs4 import BeautifulSoup
from scidownl import scihub_download


def preprocess_text(sentence):
    """Remove punctuations and extra spaces"""

    sentence = re.sub('[^a-zA-Z0-9]', ' ', sentence)
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


def pdf_in(x):
    """Read the text content of a pdf"""

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(
        resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(x, 'rb') as fh:

        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    return text


def get_pdftext_content(pdf_name):
    """read multiple pdfs from a folder"""

    result_data = pdf_in(pdf_name)
    t = [k for k in result_data.split('\n') if k != '']
    t_join = " ".join(t)
    if 'References' in t_join:
        t_join = "".join(t_join.split('References')[:-1])

    return t_join


def get_final_data(folder_name):
    """convert pdf text content into a pd.dataframe"""

    df_data = {'pmid': [], 'pdf_content': []}

    pdfs = [pdf_file
            for pdf_file in glob.glob(f'{folder_name}*')]

    for single_pdf in tqdm(range(len(pdfs))):

        fname = pdfs[single_pdf]
        pdf_name = fname.split('/')[3].split('.pdf')[0]
        df_data['pmid'].append(pdf_name)

        try:
            pdf_content = get_pdftext_content(fname)

            if pdf_content != ' ':
                df_data['pdf_content'].append(pdf_content)
            else:
                df_data['pdf_content'].append('')

        except Exception as e:
            pass

    df_data = pd.DataFrame(df_data)
    return df_data


def parse_xml(file):
    """parse the xml file"""

    dicts_out = pp.parse_medline_xml(file)
    return dicts_out


def xml2df(folder_name, save_path):
    """xml data to pd.dataframe"""

    all_files = glob.glob(f"./{folder_name}*xml")
    u_id = str(uuid.uuid4())

    df_list = []

    try:
        for i in tqdm(all_files):
            raw_df = parse_xml(i)
            df = pd.DataFrame(raw_df)
            df_list.append(df)

        final_df = pd.concat(df_list)

        final_df.to_csv(f'./{save_path}{u_id}.csv', index=False)
        final_df = pd.read_csv(f'./{save_path}{u_id}.csv')

        # it will replace blank will NaN now load again and select without NaN
        final_df = final_df[final_df['abstract'].notna()
                            ].reset_index(drop=True)
        final_df.to_csv(f'{save_path}{u_id}.csv', index=False)
        return final_df

    except Exception as e:
        print(e)
        pass


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
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    url_request = request_head(self, url)
    soup = BeautifulSoup(url_request.text, 'html.parser')

    try:
        full_text_class = soup.find_all(
            "div", {"class": "full-text-links"})
        full_content = full_text_class[0].find_all(
            "div", {"class": "full-text-links-list"})
        all_links = full_content[0].findAll("a", href=True)

        for single_link in all_links:
            data[single_link.text.strip()] = single_link['href']
        return data
    except Exception as e:
        print(e)
        return {'data': None}


def get_date(self):
    currentDate = date.today()
    today = currentDate.strftime('%Y/%m/%d')
    return today


def pmc(self, url):
    """Download pdf from pmc website"""

    url_request = request_head(self, url)
    soup = BeautifulSoup(url_request.text, 'html.parser')
    full_text_class = soup.find_all(
        "ul", {"class": "pmc-sidebar__formats"})
    link_ = full_text_class[0].find_all(
        "li", {"class": "pdf-link other_item"})[0].findAll("a", href=True)[0]
    link_url = f"https://www.ncbi.nlm.nih.gov{link_['href']}"

    return link_url


def save_pdf(self, pmid, pdf_url):
    """save pdf in local folder"""

    pdf_request = request_head(self, pdf_url)
    with open(f'{self.raw_pdf_path}{pmid}.pdf', 'wb') as f:
        f.write(pdf_request.content)
    return 0


def scihub_mode(self, pmid):
    """scihub search"""

    paper_type = "pmid"
    out = f'{self.raw_pdf_path}{pmid}.pdf'
    scihub_download(pmid, paper_type=paper_type, out=out)


def get_pdf(self, pmids, save=False, scihub=True):
    """Main function to download and search pdfs -> save in local folder"""

    downloadble_url = {}
    not_downloaded = {}

    pdf_count = len(pmids)
    print(f"Total pdf downloading : {pdf_count}.. \n")

    for pmid in tqdm(pmids):

        try:
            pdf_source = pdf_links(self, pmid)
            if 'Free PMC article' in pdf_source.keys():
                pdf_url = pmc(self, pdf_source['Free PMC article'])
                downloadble_url[pmid] = pdf_url
                if save:
                    save_pdf(self, pmid, pdf_url)

            else:
                if FindIt(pmid).url:
                    print("saving from findit")
                    findit_url = FindIt(pmid).url
                    save_pdf(self, pmid, findit_url)
                    downloadble_url[pmid] = findit_url

                elif scihub:
                    print("saving from scihub")
                    scihub_mode(self, pmid)
                    downloadble_url[pmid] = 'sci_hub'
                else:
                    not_downloaded[pmid] = pdf_source

        except Exception as e:
            pass

    return json.dumps({
        'downloaded': downloadble_url,
        'not_downloaded': not_downloaded
    }, indent=3)


def write_json(self, path_name, data, name):
    """Write json data"""

    with open(f'{path_name}{name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return 0


def get_records(self, query=None):
    """get fetch result and ids from ncbi website using api"""

    if query:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?sort=relevance&db=pubmed&term={query}&mindate=1800/01/01&maxdate={get_date(self)}&usehistory=y&retmode=json"
    else:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrdefez/eutils/esearch.fcgi?db=pubmed&mindate=1800/01/01&maxdate={self.get_date()}&usehistory=y&retmode=json"

    search_r = requests.post(search_url, verify=False)
    search_data = search_r.json()

    webenv = search_data["esearchresult"]['webenv']
    total_records = int(search_data["esearchresult"]['count'])

    return {'total_records': total_records,
            'webenv': webenv,
            'search_data': search_data}


def fetch(self, query,
          max_documents=None):
    """function to do multi task -> fetch ids, based on ids fetch abstracts"""

    all_records = get_records(self, query)
    webenv = all_records['webenv']
    all_rec = all_records['total_records']

    if max_documents:
        all_rec = max_documents
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&api_key={self.key}&retmax={max_documents}&retmode=xml&query_key=1&webenv="+webenv
    else:
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&api_key={self.key}&retmax=9999&retmode=xml&query_key=1&webenv="+webenv

    print("-------------------------------------------\n")
    print(f" Fetching total documents -> {all_rec}..\n")
    print("-------------------------------------------\n")

    for i in tqdm(range(0, all_rec, 10000)):
        try:
            meta_data = {}
            u_id = str(uuid.uuid4())
            payload = fetch_url+"&retstart="+str(i)

            print(f"Getting this URL: {payload} \n")

            fetch_r = requests.post(payload, verify=False)
            pre_name = f'{self.raw_abs_path}/pubmed_batch_{u_id}_{str(i)}_to_{str(i+all_rec)}.xml'

            f = open(pre_name, 'wb')
            f.write(fetch_r.content)
            f.close()

            meta_data['uid'] = u_id
            meta_data['query'] = query
            meta_data['url'] = payload
            meta_data['total'] = all_rec
            meta_data['iter'] = i

            write_json(self, self.meta_data_path, meta_data, u_id)

        except Exception as e:
            with open('exceptions', 'a') as f:
                f.write(f" featch_1_fetch_exception {e} number {i} \n")
            pass

    return 0
