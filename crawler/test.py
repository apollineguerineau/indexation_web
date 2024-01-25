import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from protego import Protego
import xml.etree.ElementTree as ET


def _is_allowed(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    r = requests.get(robots_url)
    rp = Protego.parse(r.text)
    return(rp.can_fetch(url, "*"))

def extract_links(url):
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)][:5]
        return links

def extract_links_2(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)][:5]

    #urls sitemap
    root = ET.fromstring(response.content)
    links.append(url.text for url in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'))
    return links

# print(_is_allowed("https://www.linkedin.com/school/ecole-nationale-de-la-statistique-et-de-l'analyse-de-l'information/"))

print(extract_links_2('https://twitter.com/ensai35?lang=fr'))

# liste = ['https://ensai.fr', 'https://twitter.com/ensai35?lang=fr', "https://www.linkedin.com/school/ecole-nationale-de-la-statistique-et-de-l'analyse-de-l'information/", 'https://www.facebook.com/Ensai35/', 'https://www.instagram.com/ensai_rennes/', 'https://ensai.fr/en/', 'https://help.twitter.com/using-twitter/twitter-supported-browsers', 'https://twitter.com/tos', 'https://twitter.com/privacy', 'https://support.twitter.com/articles/20170514', 'https://legal.twitter.com/imprint.html', 'https://help.twitter.com/using-twitter/twitter-supported-browsers#twtr-main', 'https://help.twitter.com/', 'https://microsoft.com/edge', 'https://www.apple.com/safari', 'https://www.google.com/chrome', 'https://twitter.com/tos#twtr-main', 'https://x.com/privacy', 'https://x.com/tos', 'https://help.x.com/rules-and-policies', 'https://twitter.com/privacy#twtr-main', 'https://twitter.com/privacy#x-privacy-3.1', 'https://twitter.com/privacy#x-privacy-1', 'https://help.twitter.com/en/rules-and-policies/twitter-services-and-corporate-affiliates.html', 'https://twitter.com/privacy#x-privacy-2', 'https://support.twitter.com/articles/20170514#twtr-main', 'https://support.twitter.com/en/rules-and-policies/twitter-rules.html', 'https://support.twitter.com/articles/20170514#what-are-cookies', 'https://support.twitter.com/articles/20170514#why-do-services-use', 'https://twitter.com', 'https://support.twitter.com/forms', 'mailto:de-support@twitter.com', 'https://legalrequests.twitter.com/', 'https://cdn.cms-twdigitalassets.com/content/dam/legal-twitter/twitter-netzdg-ttr/NetzDG-Jan-Jun-2023.pdf', 'https://help.twitter.com/#twtr-main', 'https://apps.apple.com/us/app/x/id333903271?pt=9551&ct=help-center&mt=8', 'https://play.google.com/store/apps/details?id=com.twitter.android', 'https://x.com/', 'https://status.twitterstat.us/', 'http://www.microsoft.com/en/us/default.aspx?redir=true', 'https://www.apple.com/', 'https://www.apple.com/us/shop/goto/store', 'https://www.apple.com/mac/', 'https://www.apple.com/ipad/', 'https://www.apple.com/iphone/', 'https://www.google.com/chrome/', 'https://www.google.com/chrome#jump-content', 'https://www.google.com/chrome/browser-tools/', 'https://www.google.com/chrome/browser-features/', 'https://x.com/privacy#twtr-main']

# print(len(liste))