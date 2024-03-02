from flask import Flask, render_template, request, redirect, url_for
import csv
import webbrowser
import shodan
import requests
from bs4 import BeautifulSoup
import threading
from time import sleep
from random import choice
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlparse
from datetime import datetime, timedelta
from urllib3 import disable_warnings, exceptions
from employeeEnum import *

# Your Shodan API key
SHODAN_API_KEY = '038pg8hedD90mEQJoPun3IPI02NJge3h'

app = Flask(__name__)


class Timer(threading.Thread):
    def __init__(self, timeout):
        threading.Thread.__init__(self)
        self.start_time = None
        self.running = None
        self.timeout = timeout

    def run(self):
        self.running = True
        self.start_time = datetime.now()
        
        while self.running:
            if (datetime.now() - self.start_time) > timedelta(seconds=self.timeout):
                self.stop()
            sleep(0.05)

    def stop(self):
        self.running = False

def get_statuscode(resp):
    try:
        return resp.status_code
    except:
        return 0


def get_proxy(proxies):
    tmp = choice(proxies) if proxies else False
    return {"http": tmp, "https": tmp} if tmp else {}


def get_agent():
    return choice([
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.5; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ])


def web_request(url, timeout=3, proxies=[], **kwargs):
    try:
        s = requests.Session()
        r = requests.Request('GET', url, headers={'User-Agent': get_agent()}, cookies = {'CONSENT' : 'YES'}, **kwargs)
        p = r.prepare()
        return s.send(p, timeout=timeout, verify=False, proxies=get_proxy(proxies))
    except requests.exceptions.TooManyRedirects as e:
        Log.fail('Proxy Error: {}'.format(e))
    except:
        pass
    return False

def extract_domain_from_google(company_name):
    search_timer = Timer(3)
    search_timer.start()

    while search_timer.running:
        try:
            url = 'https://search.brave.com/search?q={}&spellcheck=0&source=alteredQueryOriginal'.format(company_name)
            resp = web_request(url, 3, [])
            http_code = get_statuscode(resp)

            if http_code != 200:
                # print(http_code, resp.text)
                print('None 200 response, exiting search ({})'.format(http_code))
                break

            links = []
            soup = BeautifulSoup(resp.content, 'lxml')
            for link in soup.findAll('a'):
                if link['href'].startswith("/"):
                    continue
                links.append(link['href'])
            dom = str(links[0]).split('//')[-1].split('/')[0].replace("http://","").replace("https://","").replace("www.","")
            return dom

        except Exception as e:
            print(e)
            pass

    search_timer.stop()

def search_subdomains(domain):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        # Search Shodan for subdomains of the specified domain
        results = api.search(f'hostname:{domain}')
        # Extract and write the subdomains and unique IP addresses to a CSV file
        unique_ips = set()
        with open('subdomains.csv', 'w', newline='') as csvfile:
            fieldnames = ['Subdomain', 'IP Address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results['matches']:
                for hostname in result['hostnames']:
                    ip_address = result['ip_str']
                    # Check if IP address is unique
                    if ip_address not in unique_ips:
                        unique_ips.add(ip_address)
                        writer.writerow({'Subdomain': hostname, 'IP Address': ip_address})
        return 'subdomains.csv'
    except shodan.APIError as e:
        print(f'Error: {e}')
        return None

def open_report(ip_list):
    base_url = "https://www.shodan.io/search/report?query=ip%3A{}"
    for ip in ip_list:
        url = base_url.format(ip)
        webbrowser.open(url)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['domain']
        domain = extract_domain_from_google(company_name)
        employees = get_employees(company_name)
        employeeLinks = []
        uniqueEmployees = []
        for emp in employees:
            if emp['url'] not in employeeLinks:
                employeeLinks.append(emp['url'])
                uniqueEmployees.append(emp)
        employees = uniqueEmployees
        if domain:
            csv_file = search_subdomains(domain)
            if csv_file:
                with open(csv_file, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    subdomains = [{'Subdomain': row['Subdomain'], 'IP Address': row['IP Address']} for row in reader]
                return render_template('index.html', subdomains=subdomains, employees=employees)
        return render_template('index.html', subdomains=[], employees=[])
    return render_template('index.html', subdomains=[], employees=[])

@app.route('/details/<ip>')
def details(ip):
    return redirect(f"https://www.shodan.io/search/report?query=ip%3A{ip}")

if __name__ == "__main__":
    app.run(debug=True)