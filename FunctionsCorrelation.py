from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sn
import Dictionary


def tag_clean(soup):
    for tag in soup.find_all(['sup', 'tfoot']):
        tag.decompose()    

## Getting all tables from url as a list of dictionaries using BeautifulSoup library 
def get_tables_list(url, table_class):

    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get(url, headers = headers)
    soup = bs(r.content, features="lxml")
    tag_clean(soup)
    tables = soup.find_all(class_ = table_class)
    all_tables = []
    
    for index, table in enumerate (tables): 
        rows = table.find_all('tr')
        current_table = []
        for index, row in enumerate(rows):
            if index == 0:
                keys = row.find_all('th')
            
            else:
                table_dictionary = {}
                cells = row.find_all('td')
                
                for index, cell in enumerate(cells):
                    content_value = cell.get_text(' ', strip=True)
                    try:
                        content_key = keys[index].get_text(' ', strip=True)
                    except:
                        content_key = 'index Exeption'
                    table_dictionary[content_key] = content_value
                    
                current_table.append(table_dictionary)
                
        all_tables.append(current_table)
        
    return all_tables

# Returning container of dictionaries for multiple urls using get_tables_list function
def multiple_url_tables(urls, table_class): 
    tables_container = []
        
    for url in urls:
        tables_from_url = get_tables_list(url, table_class)
        tables_container.append(tables_from_url)
    return tables_container


########## Geting list of tables for diffrents stats ##################

def get_clean_sheets_table(clean_sheets_urls):

    clean_sheets_table = []
    clean_sheets_tables = multiple_url_tables(clean_sheets_urls, 'tablepress')
    for table in clean_sheets_tables:
        clean_sheets_table.append(table[0])
    
    return clean_sheets_table
    

def get_scores_first_table(urls):

    scores_first_table = []
    tables = multiple_url_tables(urls, 'tablepress')
    for index, table in enumerate(tables):
        if index < 2:
            scores_first_table.append(table[0])
        elif index == 2:
            scores_first_table.append(table[19])
        elif index == 3:
            scores_first_table.append(table[18])
            
    return scores_first_table

def get_attendance_table(urls_attendance):

    attendance_table = []
    tables = multiple_url_tables(urls_attendance, 'tablepress')
    for index, table in enumerate(tables):
        if index < 2:
             attendance_table.append(table[0])
        else:
            attendance_table.append(table[3])
    return attendance_table

def get_standigs_table(urls_stats):

    stats_tables = multiple_url_tables(urls_stats, 'tablepress')
    stats_table = []
    
    for table in stats_tables:
        stats_table.append(table[0])
    
    return stats_table

def get_tm_table(urls_tm):

    tm_tables = multiple_url_tables(urls_tm, 'responsive-table')
    tm_table = []
    for table in tm_tables:
        tm_table.append(table[0])
    
    return tm_table

def get_cards_table(urls_cards):

    cards_tables = multiple_url_tables(urls_cards, 'tablepress')
    cards_table = []
    
    for index, table in enumerate(cards_tables):
        if index == 4:
            cards_table.append(table[50])
        else:
            cards_table.append(table[0])
    
    return cards_table

def get_trainers_table(urls_wikipedia):

    wiki_tables = multiple_url_tables(urls_wikipedia, 'wikitable')
    trainers_table = []
    for index, table in enumerate(wiki_tables):
        if index == 0:
            trainers_table.append(table[24])
        elif index == 1:
            trainers_table.append(table[17])
        elif index == 2:
            trainers_table.append(table[15])
        elif index == 3:
            trainers_table.append(table[19])
        elif index == 4:
            trainers_table.append(table[18])
    
    return trainers_table

def get_exp_table(expgoals_urls):

    exp_table = []
    exp_tables = multiple_url_tables(expgoals_urls, 'tablepress')
    for table in exp_tables:
        exp_table.append(table[1])
        
    return exp_table



########### Dataframes creation for diffrent tables ##################

# Custom dataframe creation (from attandace, cards, scores_first)
def get_df (table, i):

    df = pd.DataFrame.from_dict(table[i])
    df = df.replace(Dictionary.clubs_names)
    df.columns = df.columns.str.lower()

    return df

def get_clean_sheets_df(clean_sheets_table, i):

    df_clean_sheets = pd.DataFrame(clean_sheets_table[i])
    df_clean_sheets.columns = df_clean_sheets.columns.str.lower()
    df_clean_sheets['czyste konta'] = df_clean_sheets['czyste konta'].astype(int)
    df_clean_sheets = df_clean_sheets.groupby('klub').sum()

    return df_clean_sheets

def get_standings_df(standings_table, i): 
            
    df_stats = pd.DataFrame.from_dict(standings_table[i])
    df_stats['pozycja'] = df_stats.index + 1
    df_stats.columns = df_stats.columns.str.lower()
    df_stats['klub'] = df_stats['klub'].replace(Dictionary.clubs_names)
        
    return df_stats

def get_tm_df(tm_table, i):

    df_tm = pd.DataFrame.from_dict(tm_table[i])
    df_tm = df_tm.rename(columns = {'Klub':'Lp', 'name':'klub'})
    df_tm.columns = df_tm.columns.str.lower()
    df_tm['klub'] = df_tm['klub'].replace(Dictionary.clubs_names)

    return df_tm
 
def get_trainers_df(trainers_table, i):

    df_trainers = pd.DataFrame()
    df = pd.DataFrame.from_dict(trainers_table[i])
    df = df.rename(columns = {'Kapitan' : 'date'})
    df['date'] = df['date'].str.split(' ').str[1]
    df['date'] = pd.to_datetime(df['date'],format = '%d.%m.%Y')
    year = 2020-i
    df['dni pracy trenera'] = pd.to_datetime(f'{year}-06-30') - df['date']
    df['dni pracy trenera'] = df['dni pracy trenera'].dt.days
    df.columns = df.columns.str.lower()
    df['klub'] = df['klub'].replace(Dictionary.clubs_names)

    df = df.drop(columns = ['date', 'index exeption'])
    
    df_trainers = df
    
    return df_trainers
    
def get_exp_df(exp_tables, i):

    df_exp = pd.DataFrame()
    df_temp = pd.DataFrame.from_dict(exp_tables[i])
    df_temp = df_temp.rename(columns={'DLA EXPG' : 'DLA xG',
                                     'PRZECIW EXPG' : 'PRZECIW xG'})
    df_temp.columns = df_temp.columns.str.lower()
    if i == 3:
        df_temp['klub'] = df_temp['klub'].replace({'Górnik' : 'Górnik Ł'})
    df_temp['klub'] = df_temp['klub'].replace(Dictionary.clubs_names)
    df_temp = df_temp.replace({',' : '.'},regex=True)
    
    df_temp['bilans xg'] = df_temp['dla xg'].astype(float) - df_temp['przeciw xg'].astype(float)
    df_temp['bilans g'] = df_temp['g dla'].astype(float) - df_temp['g przeciw'].astype(float)
    df_temp['G-xG'] = df_temp['bilans g'] - df_temp['bilans xg'] 
    df_exp = df_temp
    
    return df_exp



