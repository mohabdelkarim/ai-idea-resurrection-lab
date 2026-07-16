import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import MaxRetriesExceededError

class MaxRetriesExceededWarning(requests.exceptions.Warning):
    pass

def request_with_retry(url, retries=3):
    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount('http://', adapter)
    http.mount('https://', adapter)
    try:
        response = http.get(url)
        response.raise_for_status()
        return response
    except MaxRetriesExceededError as e:
        raise MaxRetriesExceededWarning(f"Max retries exceeded with url: {url}") from e
    except requests.RequestException as e:
        raise

if __name__ == '__main__':
    url = 'http://localhost:1111'
    try:
        response = request_with_retry(url)
        print(response.text)
    except MaxRetriesExceededWarning as e:
        print(f"Warning: {e}")
    except requests.RequestException as e:
        print(f"Request Exception: {e}")