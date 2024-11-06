import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import argparse
import time

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape book reviews and ratings")
    parser.add_argument('--start_row', type=int, required=True, help="The row number to start scraping from (0-indexed)")
    parser.add_argument('--num_rows', type=int, required=True, help="The number of rows to process")
    args = parser.parse_args()
    return args.start_row, args.num_rows

# Function to scrape reviews and ratings
def scrape_reviews_and_ratings(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(response.status_code)
        if response.status_code == 429:
            time.sleep(15)
        return None, None

    soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')
    
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

# Main script to scrape reviews and save to CSV
def main():
    # Parse command-line arguments
    start_row, num_rows = parse_arguments()
    
    # Load the input CSV file
    input_csv = 'data/books_list.csv'
    output_csv = 'data/reviews.csv'
    
    # Read the CSV file with book titles and links
    books_df = pd.read_csv(input_csv)
    
    # Adjust the DataFrame slice based on start_row and num_rows
    books_df = books_df.iloc[start_row:start_row + num_rows]
    
    # Prepare a list to collect results
    results = []

    batch_size = 500

    # Iterate over each book and scrape data
    for index, row in books_df.iterrows():
        title = row['Title']
        url = row['Link']
        
        reviews = None
        while not reviews:
            reviews, ratings = scrape_reviews_and_ratings(url)
        
        # Combine title, reviews, and ratings
        if reviews and ratings:
            for review, rating in zip(reviews, ratings):
                results.append([title, url, review, rating])

        if len(results) >= batch_size:
            with open(output_csv, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                if f.tell() == 0:  # Write header if file is empty
                    writer.writerow(['Title', 'URL', 'Review', 'Rating'])
                writer.writerows(results)
            
            # Clear the results list after writing to the file
            results.clear()
        
    # Print the last scraped row index
    print(f"Last scraped row index: {index}")
    
    # Append results to the output CSV file
    if results:
        with open(output_csv, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            if f.tell() == 0:  # Write header if file is empty
                writer.writerow(['Title', 'URL', 'Review', 'Rating'])
            writer.writerows(results)

    print(f"Scraping completed. Results appended to {output_csv}")

if __name__ == "__main__":
    main()
