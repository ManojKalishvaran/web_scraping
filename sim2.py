from urllib.parse import parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

def search_and_scrape(search_term, video_limit):
    edge_driver_path = r'msedgedriver.exe'

    options = webdriver.EdgeOptions()
    options.use_chromium = True
    driver = webdriver.Edge(options=options)

    try:
        driver.get('https://www.youtube.com/')
        
        # Search for the term
        search_bar = driver.find_element(By.XPATH, '//input[@id="search"]')
        search_bar.click()
        search_bar.clear()
        search_bar.send_keys(search_term)
        search_bar.send_keys(Keys.RETURN)

        # Wait for search results to load using WebDriverWait
        wait = WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="video-title"]')))

        # Get the URLs of the first N videos in the search results
        video_urls = [a_tag.get_attribute('href') for a_tag in driver.find_elements(By.XPATH, '//a[@id="video-title"]')[:video_limit]]

        # Lists to store details for each video
        views_list = []
        titles_list = []
        dates_list = []
        hashtags_list = []

        # Scrape details for each video
        for video_url in video_urls:
            views, title, date, hashtags = scrape_video_details(video_url)
            views_list.append(views)
            titles_list.append(title)
            dates_list.append(date)
            hashtags_list.append(hashtags)

        # Print or use the lists as needed
        print("Titles:", titles_list)
        print("Views:", views_list)
        print("Date of upload:", dates_list)
        print("Hashtags:", hashtags_list)

        # Save data in CSV
        save_to_csv(titles_list, views_list, dates_list, hashtags_list)

    finally:
        driver.quit()

def extract_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'v' in query_params:
        video_id = query_params['v'][0]
        return video_id
    else:
        print("Error: Could not extract video ID from the URL.")
        return None

def scrape_video_details(url):
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    driver = webdriver.Edge(options=options)

    try:
        video_id = extract_video_id(url)

        if video_id:
            new_url = f'https://www.youtube.com/watch?v={video_id}'

            driver.get(new_url)
            driver.minimize_window()

            # Wait for the view count element to load
            view_count_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="info"]/span[1]'))
            )

            views = view_count_element.text

            title_vid_element = driver.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')
            title = title_vid_element.text

            date_vid_element = driver.find_element(By.XPATH, '//*[@id="info"]/span[3]')
            date = date_vid_element.text

            # Find and extract hashtags if available
            try:
                hashtags_elements = driver.find_elements(By.XPATH, '//*[@id="info"]//a')
                hashtags = [tag.text for tag in hashtags_elements if tag.text.startswith('#') ]
                
            except Exception as e:
                print("Error occurred while trying to extract hashtags:", e)
                hashtags = None

            return views, title, date, hashtags
    finally:
        driver.quit()

def save_to_csv(titles, views, dates, hashtags):
    with open("my_yt_data.csv", "w", newline='', encoding='utf-16') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(['Title', 'Views', 'Date of upload', 'Hashtags'])
        for title, view, date, hashtag in zip(titles, views, dates, hashtags):
            writer.writerow([title, view, date, hashtag])

if __name__ == "__main__":
    search_term = input("Enter the term to search on YouTube: ")
    video_limit = int(input("Enter how many videos to be scraped: "))
    search_and_scrape(search_term, video_limit)
