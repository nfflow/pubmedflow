"""
    This class is to implement the util functions for pubmed main class
    @author: Aaditya(Ankit) <aadityaura@gmail.com>
    @date created: 27/06/2022
    @date last modified: 02/08/2022
"""

import os
import re
from pathlib import Path
import pubmed_parser as pp
import pandas as pd
from tqdm import tqdm
import io
import uuid
import os, glob

from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
    
    
def preprocess_text(sentence):
    """Remove punctuations and extra spaces"""
    
    sentence = re.sub('[^a-zA-Z0-9]', ' ', sentence)
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


def pdf_in(x):
    """Read the text content of a pdf"""
    
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter        = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
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
    t           = [k for k in result_data.split('\n') if k!='']
    t_join      = " ".join(t)
    if 'References' in t_join:
        t_join  = "".join(t_join.split('References')[:-1])
    final       = preprocess_text(t_join)
    
    return final


def get_final_data(folder_name):
    """convert pdf text content into a pd.dataframe"""
    
    df_data        = {'pmid' : [], 'pdf_content': []}
    
    pdfs           = [pdf_file 
                    for pdf_file in glob.glob(f'{folder_name}*')]

    for single_pdf in tqdm(range(len(pdfs))):
        
        fname    = pdfs[single_pdf]
        pdf_name = fname.split('/')[3].split('.pdf')[0]
        df_data['pmid'].append(pdf_name)
        
        try:
            pdf_content = get_pdftext_content(fname)
            
            
            if pdf_content!=' ':
                df_data['pdf_content'].append(pdf_content)
            else:
                df_data['pdf_content'].append('')
            
        except Exception as e:
            pass
    
    df_data  = pd.DataFrame(df_data)
    return df_data


def parse_xml(file):
    """parse the xml file"""
    
    dicts_out = pp.parse_medline_xml(file)
    return dicts_out


def xml2df(folder_name, save_path):
    """xml data to pd.dataframe"""

    all_files = glob.glob(f"./{folder_name}*xml")
    u_id      = str(uuid.uuid4())
    
    df_list = []
    
    try:
        for i in tqdm(all_files):
            raw_df = parse_xml(i)
            df     = pd.DataFrame(raw_df)
            df_list.append(df)

        final_df = pd.concat(df_list)
                
        final_df.to_csv(f'./{save_path}{u_id}.csv',index=False)
        final_df   = pd.read_csv(f'./{save_path}{u_id}.csv')
        
        # it will replace blank will NaN now load again and select without NaN
        final_df   = final_df[final_df['abstract'].notna()].reset_index(drop=True)
        final_df.to_csv(f'{save_path}{u_id}.csv',index=False)
        return final_df

    except Exception as e:
        print(e)
        pass
