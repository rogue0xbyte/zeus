import pandas as pd
import random
import requests
import bs4
import sqlalchemy
from collections import OrderedDict
from sqlalchemy import create_engine, types as sqlalchemy_types
from urllib.parse import quote  
from urllib.request import Request, urlopen 


pd.set_option('max_colwidth', None)

def random_header():
    headers_list = list_dict()
    headers = random.choice(headers_list)
    return headers

def ingest_google_news():
    query = 'financial cyber-threat'     
    encoded_query = quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&tbm=nws&lr=lang_en&hl=en&sort=date&num=5"

    # Initialize lists to store data
    t_titles = []
    t_urls = []
    t_dates = [] 

    # Set header by random user agent
    headers = random_header()


    res = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(res).read()

    soup = bs4.BeautifulSoup(webpage, 'html5lib')
    # print(soup)
    
        # Extract relevant information from search results
    links = soup.find_all('div', attrs={'class':'Gx5Zad fP1Qef xpd EtOod pkphOe'})
    for l in links:
        try:
            title = l.find('div', class_='BNeawe vvjwJb AP7Wnd').text
            url_w = (l.find('a', href= True)['href'])
            date = l.find('span', class_='r0bn4c rQMQod').text

            # Append extracted data to lists
            t_titles.append(title)
            t_urls.append(url_w)
            t_dates.append(date)
            
            # Debug print statement to check URL extraction
            # print(f"Title: {title}, URL: {url_w}, Date: {date}")
        except Exception as e:
            print(f"Error processing URL: {url_w}. Error: {str(e)}")

    # Create DataFrame from collected data
    df = pd.DataFrame({
        'title': t_titles,
        'url': t_urls,
        'date_posted': t_dates
    })

    # Print DataFrame to check the collected data (for debugging) 
    print(df.head())


    
    try:
        # Connect to PostgreSQL database using SQLAlchemy
        engine = create_engine('postgresql://postgres:inr_db@db.inr.intellx.in:5432/zeus')

        with engine.connect() as conn:
            #delete existing data from table

            delete_statement = sqlalchemy.text("TRUNCATE TABLE gnews2")
            conn.execute(delete_statement)

            
            # Append data to database table
            # Modify the dtype argument in df.to_sql() to specify the data types
            # df.to_sql('gnews2', con=engine, if_exists='append', index=False, dtype={'title': sqlalchemy.String, 'url': sqlalchemy.String, 'date_posted': sqlalchemy.String})

            engine.connect().commit()  # Commit the transaction
            print("Data inserted successfully.")
    except sqlalchemy.exc.OperationalError as op_err:
        print(f"Operational error occurred: {op_err}")
    except sqlalchemy.exc.IntegrityError as int_err:
        print(f"Integrity error occurred: {int_err}")
    except Exception as e:
        print(f"Error inserting data into the database: {str(e)}")
    finally:
        # Dispose the engine
        engine.dispose()

    return(df.head())

def list_header():
    headers_list = [
        # Firefox 24 Linux
        {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Firefox Mac
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    ]
    
    return headers_list

def list_dict():
    # Get headers list
    headers_list = list_header()
    # Create ordered dict from Headers above
    ordered_headers_list = []
    for headers in headers_list:
        h = OrderedDict()
        for header,value in headers.items():
            h[header]=value
        ordered_headers_list.append(h)
    return ordered_headers_list