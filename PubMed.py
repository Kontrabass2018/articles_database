from io import StringIO
from Bio import Entrez
from time import sleep
import csv
import pandas as pd
import pdb
import os 
from bs4 import BeautifulSoup
import re 
from textstat import *
from bs4 import XMLParsedAsHTMLWarning
import warnings
import urllib
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
# data_list = []
# for fname in os.listdir("Articles_Data/pubmed"):

#     data_list.append(pd.read_csv(f"Articles_Data/pubmed/{fname}"))

# pdb.set_trace()
# Load the journal table
from Bio import Entrez, Medline


def extract_text(TXT):
    soup = BeautifulSoup(TXT, "html.parser")
    for sup_tag in soup.find_all("sup"):
        sup_tag.decompose()
    return soup.get_text(separator=" ", strip = True)

def filter_text(TXT):
    if re.search("abstract", TXT.lower()) is None :
        return None 
    if re.search("references", TXT.lower()) is None :
        return None 
    pstart = re.search("abstract",TXT.lower()).span()[1]
    if re.search("references", TXT.lower()).span()[0] < pstart :
        return  None
    pend  = pstart + re.search("references", TXT[pstart:].lower()).span()[0]
    return TXT[pstart:pend]

def search_medline(query, email):
    Entrez.email = email
    search = Entrez.esearch(db='pmc', retmax = 9998, term=query, usehistory='y')
    handle = Entrez.read(search)
    try:
        return handle
    except Exception as e:
        raise IOError(str(e))
    finally:
        search.close()

def fetch_rec(rec_id, entrez_handle):
    fetch_handle = Entrez.efetch(db='pmc', id=rec_id,
                                 retmode='xml', retmax = 9998)
                                #  webenv=entrez_handle['WebEnv'],
                                #  query_key=entrez_handle['QueryKey'])
    rec = fetch_handle.read()
    return rec


    
# email = "leonardsauve@gmail.com"
# journal_name = "Nature"
# start_date = "2020/06/05"
# end_date = "2025/05/01"
# query = f'"{journal_name}"[Journal] AND ({start_date}[PDAT] : {end_date}[PDAT])'
# rec_handler = search_medline(query, email)
# for rec_id in rec_handler['IdList']:
#     # pdb.set_trace()
#     rec = fetch_rec(rec_id, rec_handler).decode("utf8")
#     # rec_file = StringIO(rec)
#     raw = extract_text(rec) 
#     # print(f"ID [{rec_id}]")              
#     textf = filter_text(raw)
#     if textf is not None :
#         wc = len(textf.split())
#         fkgl = flesch_kincaid_grade(textf)
#         print(f"ID [{rec_id}] \t FKGL: {fkgl} \t WC : {wc}")
#     else:
#         print(f"ID [{rec_id}] not available")
        # pdb.set_trace()
    # medline_rec = Medline.read(rec_file)
    # if 'AB' in medline_rec:
    #     print(medline_rec['AB'])

df_journals = pd.read_csv("journals_quartiles.csv")

def get_pubmed_articles_by_journal(journal_name, start_date, end_date, email, max_return =10000,  batch_size=100):
    Entrez.email = email
    search_term = f'"{journal_name}"[Journal] AND ({start_date}[PDAT] : {end_date}[PDAT])'

    # Get total number of results
    search_handle = Entrez.esearch(
        db="pmc",
        term=search_term,
        retmax=9998
    )
    search_results = Entrez.read(search_handle)
    search_handle.close()

    total_count = min(int(search_results["Count"]), 9998)
    print(f"[{journal_name}] Found {total_count} articles.")
    
    all_articles = []

    for start in range(0, total_count, batch_size):
        print(f"  Fetching records {start} to {start + batch_size}...")
        fetch_handle = Entrez.esearch(
            db="pmc",
            term=search_term,
            retmax=batch_size,
            retstart=start
        )
        fetch_record = Entrez.read(fetch_handle)
        fetch_handle.close()
        id_list = fetch_record["IdList"]

        summary_handle = Entrez.esummary(db="pmc", id=",".join(id_list))
        summaries = Entrez.read(summary_handle)
        summary_handle.close()

        for item in summaries:
            
            wc, fkgl = get_wc_fkgl(item["Id"], fetch_handle)
            newline = {
                "journal": journal_name,
                "title": item.get("Title"),
                "pubdate": item.get("PubDate"),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{item['Id']}/",
                "wc": wc,
                "fkgl":fkgl
            }
            all_articles.append(newline)
        outfile = f"Articles_Data/pubmed/{journal_name}_pubmed_articles_by_journal.csv"
        WRITE(outfile, all_articles)
        sleep(0.5)

    return all_articles

def get_wc_fkgl(ID, fetch_handle):
    try :
        rec = fetch_rec(ID, fetch_handle).decode("utf8")
        # rec_file = StringIO(rec)
        raw = extract_text(rec) 
        # print(f"ID [{rec_id}]")              
        textf = filter_text(raw)
        fkgl, wc  = None, None
        if textf is not None :
            wc = len(textf.split())
            fkgl = flesch_kincaid_grade(textf)
        return wc, fkgl 
    except urllib.error.HTTPError:
        return None, None

# ---- CONFIGURATION ----
email = "your.email@example.com"
start_date = "2020/06/05"
end_date = "2025/05/01"
# end_date = "2025/05/01"
def WRITE(output_file, all_data):
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["journal", "title", "pubdate", "url", "wc", "fkgl"])
        writer.writeheader()
        for entry in all_data:
            writer.writerow(entry)

    print(f"\n✅ Finished: {len(all_data)} total articles saved to {output_file}")


for journal in df_journals["Nom périodique"]:
    all_data = []   
    articles = get_pubmed_articles_by_journal(journal, start_date, end_date, email, max_return = 10000, batch_size=100)
    all_data.extend(articles)

output_file = f"Articles_Data/pubmed_articles_by_journal.csv"
WRITE(output_file, all_data)

# Save to CSV
output_file = f"{journal}_pubmed_articles_by_journal.csv"
