import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Load the input CSV file
input_csv = 'data/books_list.csv'
output_csv = 'data/reviews.csv'

# Read the CSV file with book titles and links
books_df = pd.read_csv(input_csv)

# Function to scrape reviews and ratings
def scrape_reviews_and_ratings(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    reviews = []
    ratings = []
    
    # Find all review blocks
    review_blocks = soup.find_all('div', class_='comment-cloud')
    for block in review_blocks:
        # Extract review text
        review_text = block.find('p', class_='expandTextNoJS p-expanded js-expanded mb-0')
        if review_text:
            reviews.append(review_text.get_text(strip=True))
        else:
            reviews.append(None)
        
        # Extract the rating associated with this review
        rating_span = block.find('span', class_='big-number')
        if rating_span:
            try:
                ratings.append(int(rating_span.get_text(strip=True)))
            except ValueError:
                ratings.append(None)
        else:
            ratings.append(None)

    return reviews, ratings

# Prepare a list to collect results
results = []

# Iterate over each book and scrape data
for index, row in books_df.iterrows():
    title = row['Title']
    url = row['Link']
    
    reviews, ratings = scrape_reviews_and_ratings(url)
    
    # Combine title, reviews, and ratings
    if reviews and ratings:
        for review, rating in zip(reviews, ratings):
            results.append([title, url, review, rating])

# Save results to a new CSV file
output_df = pd.DataFrame(results, columns=['Title', 'URL', 'Review', 'Rating'])
output_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)

print(f"Scraping completed. Results saved to {output_csv}")
