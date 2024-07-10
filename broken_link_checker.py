import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
import logging
from datetime import datetime
import json
from dotenv import load_dotenv
from tqdm import tqdm
import http.client

# Load environment variables
load_dotenv()

# Read configuration from .env file
BASE_URL = os.getenv('BASE_URL')
CHECK_EXTERNAL = os.getenv('CHECK_EXTERNAL', 'false').lower() == 'true'
TIMEOUT_THRESHOLD = int(os.getenv('TIMEOUT_THRESHOLD', '10'))
LOG_ALL_URLS = os.getenv('LOG_ALL_URLS', 'false').lower() == 'true'

# HTTP status codes with their descriptions
HTTP_STATUS_CODES = {code: desc for code, desc in http.client.responses.items()}

def setup_logging(resume):
    if not resume and os.path.exists('checker.log'):
        os.remove('checker.log')
    logging.basicConfig(filename='checker.log', level=logging.INFO, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def save_state(visited, to_visit, broken_links, csv_filename, all_urls_filename):
    state = {
        "visited": list(visited),
        "to_visit": to_visit,
        "broken_links": broken_links,
        "csv_filename": csv_filename,
        "all_urls_filename": all_urls_filename
    }
    with open('checker_state.json', 'w') as f:
        json.dump(state, f)

def load_state():
    if os.path.exists('checker_state.json'):
        with open('checker_state.json', 'r') as f:
            state = json.load(f)
        return set(state["visited"]), state["to_visit"], state["broken_links"], state["csv_filename"], state["all_urls_filename"]
    return None

def is_external_url(url, base_url):
    return not url.startswith(base_url)

def get_status_with_description(status_code):
    status_code = int(status_code)
    description = HTTP_STATUS_CODES.get(status_code, "Unknown")
    return f"{status_code} {description}"

def check_broken_links(base_url, resume=False):
    setup_logging(resume)

    if resume:
        state = load_state()
        if state:
            visited, to_visit, broken_links, csv_filename, all_urls_filename = state
            print(f"Resuming previous job. CSV file: {csv_filename}")
        else:
            print("No previous state found. Starting a new job.")
            resume = False

    if not resume:
        visited = set()
        to_visit = [(base_url, base_url)]  # (url, source_url)
        broken_links = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f'broken_links_{timestamp}.csv'
        all_urls_filename = f'all_urls_{timestamp}.csv' if LOG_ALL_URLS else None

    csv_mode = 'a' if resume else 'w'
    with open(csv_filename, csv_mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not resume:
            csv_writer.writerow(['Date and Time', 'Type', 'URL', 'Status Code', 'Source URL'])

        if LOG_ALL_URLS:
            all_urls_mode = 'a' if resume else 'w'
            all_urls_file = open(all_urls_filename, all_urls_mode, newline='')
            all_urls_writer = csv.writer(all_urls_file)
            if not resume:
                all_urls_writer.writerow(['Date and Time', 'Type', 'URL', 'Status Code', 'Source URL'])

        with tqdm(total=len(to_visit), desc="Checking links", unit="link") as pbar:
            while to_visit:
                url, source_url = to_visit.pop(0)
                if url in visited:
                    continue

                visited.add(url)
                is_external = is_external_url(url, base_url)
                url_type = 'external' if is_external else 'internal'

                if is_external and not CHECK_EXTERNAL:
                    continue

                try:
                    response = requests.get(url, timeout=TIMEOUT_THRESHOLD)
                    status_code = response.status_code
                    status_with_description = get_status_with_description(status_code)
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if LOG_ALL_URLS:
                        all_urls_writer.writerow([current_datetime, url_type, url, status_with_description, source_url])

                    response.raise_for_status()

                    if not is_external:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'text/html' in content_type:
                            try:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                new_links = [(urljoin(base_url, link['href']), url) for link in soup.find_all('a', href=True)]
                                new_links = [link for link in new_links if link[0] not in visited]
                                to_visit.extend(new_links)
                                pbar.total += len(new_links)
                            except Exception as e:
                                logging.error(f"Error parsing HTML from {url}: {e}")
                                print(f"\nError parsing HTML from: {url}")

                except requests.Timeout:
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([current_datetime, url_type, url, '503 Service Unavailable (Timeout)', source_url])
                    broken_links.append((url, source_url))
                    logging.info(f"Timeout (503): {url} (found on {source_url})")
                    print(f"\nTimeout (503): {url} (on page: {source_url})")

                except requests.HTTPError as e:
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    error_status = get_status_with_description(e.response.status_code)
                    csv_writer.writerow([current_datetime, url_type, url, error_status, source_url])
                    broken_links.append((url, source_url))
                    logging.info(f"Broken Link ({error_status}): {url} (found on {source_url})")
                    print(f"\nBroken Link Found: {url} (on page: {source_url})")

                except requests.RequestException as e:
                    logging.error(f"Error accessing {url}: {e}")
                    print(f"\nError accessing: {url}")
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    csv_writer.writerow([current_datetime, url_type, url, 'Connection Error', source_url])
                    broken_links.append((url, source_url))

                pbar.update(1)
                pbar.set_postfix({"Visited": len(visited), "To Visit": len(to_visit), "Broken": len(broken_links)})

                # Save state every 100 visited URLs
                if len(visited) % 100 == 0:
                    save_state(visited, to_visit, broken_links, csv_filename, all_urls_filename)

        if LOG_ALL_URLS:
            all_urls_file.close()

    logging.info(f"Check completed. Broken links logged to {csv_filename}")
    print(f"\nCheck completed. Found {len(broken_links)} broken links. Details logged to {csv_filename}")
    if LOG_ALL_URLS:
        print(f"All visited URLs logged to {all_urls_filename}")

    # Clear the state file after successful completion
    if os.path.exists('checker_state.json'):
        os.remove('checker_state.json')

if __name__ == "__main__":
    if not BASE_URL:
        logging.error("BASE_URL not found in .env file")
        print("Please set the BASE_URL in the .env file")
    else:
        resume = input("Do you want to resume the previous job? (y/n): ").lower() == 'y'
        print(f"{'Resuming' if resume else 'Starting'} link check for: {BASE_URL}")
        print(f"Checking external URLs: {'Yes' if CHECK_EXTERNAL else 'No'}")
        print(f"Timeout threshold: {TIMEOUT_THRESHOLD} seconds")
        print(f"Logging all URLs: {'Yes' if LOG_ALL_URLS else 'No'}")
        check_broken_links(BASE_URL, resume)