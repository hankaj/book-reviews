import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Load your CSV with book titles and URLs
input_csv = 'books.csv'  # Replace with your CSV file path
output_csv = 'scraped_reviews.csv'

# Read the CSV file
df = pd.read_csv(input_csv)

# Headers to use in the GET request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

# List to store scraped data
scraped_data = []

# Iterate over each URL in the CSV
for index, row in df.iterrows():
    book_title = row['Title']  # Adjust this if your CSV has different column names
    url = row['URL']           # Adjust this column name as necessary
    
    # Send a GET request to the book page with headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all review elements
        reviews = soup.find_all('article', class_='ReviewCard')
        
        for review in reviews:
            # Extract the review text
            review_content = review.find('div', class_='TruncatedContent__text')
            review_text = review_content.get_text(strip=True) if review_content else ''
            
            # Extract the rating from a nearby 'ShelfStatus' div
            shelf_status = review.find('div', class_='ShelfStatus')

            rating_element = shelf_status.find('span') if shelf_status else None

            rating = int(re.search(r'\d+', rating_element['aria-label']).group()) if rating_element else None
            
            # Add data to the list
            scraped_data.append({
                'Book Title': book_title,
                'Review': review_text,
                'Rating': rating
            })
            break # Scrape 1 review for testing purposes
    else:
        print(f"Failed to fetch {url} (Status code: {response.status_code})")

    break # Scrape 1 book for testing purposes

# Create a DataFrame and save to CSV
output_df = pd.DataFrame(scraped_data)
output_df.to_csv(output_csv, index=False)

print(f"Scraping completed. Data saved to {output_csv}.")
