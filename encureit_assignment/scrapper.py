import requests
from bs4 import BeautifulSoup

# scraps and formats the data
def scrape_data(base_url,urls_to_scrape):
    final_text=""
    for urls in urls_to_scrape:
        url = base_url + urls
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        main_content = soup.find('article') or soup.find('main') or soup.find('div', {'id': 'content'}) or soup.body

        clean_text = main_content.get_text(separator='\n', strip=True)

        heading=urls.split("/")[-1].replace("-"," ").title()+" "
        final_text=final_text+"\n # "+heading+"\n"+clean_text+ "\n"
    return final_text

# saves the formatted data into a text file
def save_text(final_text):
    with open("BOM_scraped_content.txt", "w", encoding="utf-8") as f:
        f.write(final_text)