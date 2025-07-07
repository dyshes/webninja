# WebNinja


# setup

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
=======
WebNinja is a lightweight automation and scraping toolkit. Instead of writing
Python code for each task, you describe the steps to perform in a JSON
configuration file. The parser interprets this file and uses Selenium,
`requests`/`requests-html`, and BeautifulSoup to drive the browser or fetch
pages. It is designed to make building web parsers and small robots simple.

## Architecture

The repository is composed of a few key modules:

- `parser.py` – entry point that reads a configuration file and executes the
  described actions.
- `bandit.py` – helpers around Selenium for browser automation.
- `surfer.py` – utilities for fetching pages and downloading content with
  `requests` or `requests-html`.
- `reader.py` – HTML parsing helpers used by other modules.
- `documenter.py` – writes collected data to JSON or spreadsheets.
- `mfa.py` – multiprocessing helpers to parallelise work.

Example configurations live in the `confs/` directory and tests can be found in
`test/`.

## Prerequisites

- Python 3.8 or higher.
- Firefox installed with `geckodriver` available in `PATH` for Selenium.
- Python packages:
  `selenium`, `requests`, `requests-html`, `beautifulsoup4`, `flask`,
  `xlsxwriter`, `Pillow`, `pyautogui`, and `pytest` for the test suite.

Install the required packages with:

```bash
pip install selenium requests requests-html beautifulsoup4 flask \
    xlsxwriter Pillow pyautogui pytest
```

## Setup

1. Clone the repository and change into the project directory.
2. *(Optional)* Create and activate a virtual environment.
3. Install the dependencies using the command above.
4. Prepare a JSON configuration file. The `confs/proton.json` file can be used
   as a starting point:

```json
[
  { "do": "go", "by": "firefox", "loc": "http://account.proton.me/login", "folder": "proton" },
  { "do": "post", "loc": "//*[@id=\"username\"]", "file": "username" },
  { "do": "post", "loc": "//*[@id=\"password\"]", "file": "12345" },
  { "do": "click", "loc": "/html/body/div[1]/div[3]/div[1]/div/main/div[2]/form/button" }
]
```

5. Run the parser with your configuration:

```bash
python3 parser.py confs/proton.json
```

The parser will perform the operations defined in the file and store any output
in the `files/` directory.

## Running Tests

With `pytest` installed, run the test suite from the project root:

```bash
pytest
```

The tests exercise the Selenium helpers, multiprocessing utilities and the HTML
parsing logic.
