# Broken Link Checker

A robust Python script that crawls a specified website, follows all accessible links, and identifies broken links. This tool is essential for website maintenance, improving user experience, and SEO optimization.

## Features

- Crawls all accessible pages from a given base URL
- Detects and logs broken links with detailed status codes and descriptions
- Prevents revisiting already checked pages
- Configurable settings through environment variables (BASE_URL, CHECK_EXTERNAL, TIMEOUT_THRESHOLD, LOG_ALL_URLS).
- Ability to check both internal and external links.
- Logging of all visited URLs (optional) and broken links.
- Progress bar to show the current status of the link checking process.
- State saving and resuming capability for interrupted jobs.

## Prerequisites

- Python 3.6+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ajithrn/broken-link-checker.git
   cd broken-link-checker
   ```

2. Create a virtual environment:
   ```
   python3 -m venv myenv
   ```

3. Activate the virtual environment:
   - On macOS and Linux:
     ```
     source myenv/bin/activate
     ```
   - On Windows:
     ```
     myenv\Scripts\activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add your configuration:
   ```
   BASE_URL=https://example.com
   CHECK_EXTERNAL=false
   TIMEOUT_THRESHOLD=10
   LOG_ALL_URLS=false
   ```

## Usage

1. Ensure your `.env` file is configured with the desired settings.

2. Run the script:
   ```
   python broken_link_checker.py
   ```

3. The script will ask if you want to resume a previous job or start a new one.

4. After the check is complete, review the following files:
   - `broken_links_YYYYMMDD_HHMMSS.csv`: Contains all encountered broken links
   - `all_urls_YYYYMMDD_HHMMSS.csv`: Contains all visited URLs and their responses (if LOG_ALL_URLS is true)
   - `checker.log`: Contains general information and any errors during the check

## Configuration

Modify the `.env` file to change the following settings:
- `BASE_URL`: The website to check
- `CHECK_EXTERNAL`: Set to `true` to check external links, `false` to ignore them
- `TIMEOUT_THRESHOLD`: Number of seconds to wait before considering a link as timed out
- `LOG_ALL_URLS`: Set to `true` to log all visited URLs and their responses, `false` to log only broken links

## CSV Format

Both the broken links CSV and all URLs CSV (if enabled) contain the following columns:

1. Date (YYYY-MM-DD)
2. Type (internal/external)
3. URL
4. Status Code
5. Source URL

## HTTP Status Codes

Here's a brief explanation of common HTTP status codes you might encounter:

### Successful Responses
- 200 OK: The request was successful.
- 201 Created: The request succeeded, and a new resource was created.
- 204 No Content: The server successfully processed the request but is not returning any content.

### Redirection Messages
- 301 Moved Permanently: The URL of the requested resource has been changed permanently.
- 302 Found: The URL of the requested resource has been changed temporarily.
- 304 Not Modified: The client can use cached data.

### Client Error Responses
- 400 Bad Request: The server could not understand the request due to invalid syntax.
- 401 Unauthorized: The client must authenticate itself to get the requested response.
- 403 Forbidden: The client does not have access rights to the content.
- 404 Not Found: The server can't find the requested resource.
- 405 Method Not Allowed: The request method is known by the server but is not supported by the target resource.
- 429 Too Many Requests: The user has sent too many requests in a given amount of time.

### Server Error Responses
- 500 Internal Server Error: The server has encountered a situation it doesn't know how to handle.
- 501 Not Implemented: The request method is not supported by the server.
- 502 Bad Gateway: The server, while working as a gateway to get a response needed to handle the request, got an invalid response.
- 503 Service Unavailable: The server is not ready to handle the request.
- 504 Gateway Timeout: The server is acting as a gateway and cannot get a response in time.

### Custom Errors
- 503 (Timeout): This is a custom error used by the script to indicate that the request timed out.
- Connection Error: This is used when there's a problem establishing a connection to the server.

For a full list of HTTP status codes and their meanings, refer to the [Mozilla Developer Network HTTP Status documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Ensure you have permission to crawl the target website. Always respect the website's `robots.txt` file and crawl-delay directives. Use this tool responsibly and ethically.