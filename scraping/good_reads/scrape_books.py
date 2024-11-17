import requests
from bs4 import BeautifulSoup
import csv

# URL of the Goodreads page to scrape
url = 'https://www.goodreads.com/list/show/1.Best_Books_Ever?ref=ls_pl_car_0'

# Set headers to include User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

# Send a GET request to the webpage
response = requests.get(url, headers=headers)
if response.status_code == 200:
    # Parse the content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all book title elements
    book_elements = soup.select('a.bookTitle')
    
    # Open a CSV file for writing
    with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'URL'])  # Write the header row
        
        # Iterate through the elements and extract the titles and URLs
        for book in book_elements:
            title = book.text.strip()
            book_url = 'https://www.goodreads.com' + book['href']
            writer.writerow([title, book_url])  # Write each book's data to the CSV
    
    print("Books have been saved to 'books.csv'")
else:
    print(f'Failed to retrieve the page. Status code: {response.status_code}')
