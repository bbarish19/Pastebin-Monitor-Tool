# Pastebin-Monitor-Tool

Description
This program monitors Pastebin for new pastes that contain sensitive information such as usernames, passwords, and API keys. It periodically checks Pastebin's recent pastes, filters out pastes related to gift cards, and saves any detected leaks to a file (leaked_pastes.txt). The tool can be stopped at any time by typing exit or using CTRL+C.

Features
1. Monitors Pastebin for leaked credentials.
2. Filters out gift card-related pastes by checking page titles.
3. Saves detected leaks to a file with URLs and titles.
4. Runs in the background and can be stopped via user input.
   
Installation
Prerequisites
Python 3.6+ should be installed on your system.
Required libraries: requests, beautifulsoup4
Install Dependencies Open a terminal or command prompt, and run the following command to install the required libraries:
pip install requests beautifulsoup4

Running the Program
Simply run the script using Python or run the executable:
python pastebin_leak_scraper.py

Stopping the Program
Type exit in the console to stop the script.
Alternatively, you can press CTRL+C to stop it immediately.

Output
The detected leaks will be saved in a file named leaked_pastes.txt.
Each entry includes the paste URL, title, and the sensitive content (if found), with a separator line between each entry.

Usage
Run the script as described above.
The program will start checking for leaks from Pastebin, filtering out gift card-related pastes.
If a leak is found, the program will save the URL and the content of the leak to leaked_pastes.txt.
You can monitor the process in the terminal, and the script will show the number of leaks found.
When done, type exit or use CTRL+C to stop the program.

Notes
The program checks the last 10 pastes from Pastebin for sensitive content.
Be respectful of Pastebin's terms of service when using this tool.
Rate limiting may occur if too many requests are made in a short period. Adding a delay (e.g., time.sleep(60)) can help mitigate this.
