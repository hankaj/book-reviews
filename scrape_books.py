import csv
import requests
from bs4 import BeautifulSoup

# Define the base URL and headers
base_url = "https://lubimyczytac.pl/katalog"
params = {
    "page": 1,
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
def scrape_books():
    books = []
    while len(books) < 500:
        response = requests.get(base_url, params=params, headers=headers)
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
    return books

# Scrape the books
books_list = scrape_books()

# Save books to CSV
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Link'])
    writer.writerows(books_list)

print(f"Books saved to {csv_file_path}")
