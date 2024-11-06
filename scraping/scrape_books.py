import csv
import requests
from bs4 import BeautifulSoup
import argparse
import time

# Define the base URL and headers
base_url = "https://lubimyczytac.pl/katalog"
params = {
    "listId": "booksFilteredList",
    "onlyPublished": 1,
    "rating[0]": 0,
    "rating[1]": 10,
    "publishedYear[0]": 1200,
    "publishedYear[1]": 2024,
    "catalogSortBy": "ratings-desc",
    "paginatorType": "Standard"
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

# CSV file path
csv_file_path = 'data/books_list.csv'

# Function to extract book titles and links
def extract_books_from_page(soup):
    books = []
    book_divs = soup.find_all('div', class_='authorAllBooks__singleText')
    for book_div in book_divs:
        title_tag = book_div.find('a', class_='authorAllBooks__singleTextTitle')
        if title_tag:
            title = title_tag.text.strip()
            link = f"https://lubimyczytac.pl{title_tag['href']}"
            books.append((title, link))
    return books

# Function to scrape all pages
def scrape_books(start_page, num_books):
    params['page'] = start_page
    books = []
    while len(books) < num_books:
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            if response.status_code == 429:
                time.sleep(15)
            print(response.status_code)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract books from the current page
        books_on_page = extract_books_from_page(soup)
        if not books_on_page:
            break
        
        books.extend(books_on_page)
        
        # Find the pagination next button
        next_button = soup.find('li', class_='page-item next-page')
        if next_button:
            # Extract the next page number
            next_page = next_button.find('a', class_='page-link')['data-page']
            params['page'] = next_page
        else:
            # No more pages
            break
    print(f"Next page to scrape: {next_page}")
    return books

def main():
    parser = argparse.ArgumentParser(description="Scrape book data from lubimyczytac.pl")
    parser.add_argument('page', type=int, help="Starting page number for scraping")
    parser.add_argument('num_books', type=int, help="Number of books to scrape")
    args = parser.parse_args()
    
    # Scrape the books starting from the specified page
    books_list = scrape_books(args.page, args.num_books)
    
    # # Append books to the CSV file
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty and write headers
            writer.writerow(['Title', 'Link'])
        writer.writerows(books_list)
    
    print(f"Books appended to {csv_file_path}")

if __name__ == "__main__":
    main()
