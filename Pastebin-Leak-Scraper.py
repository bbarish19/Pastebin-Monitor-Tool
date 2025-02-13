import requests
import re
import time
import os
import threading
from bs4 import BeautifulSoup

# ASCII Art to display at the start
ASCII_ART = """8888888888888888888888888888888888888888888888888888888888888888888888
8888888888888888888888888888888888888888888888888888888888888888888888
888888888888888888888888888888P""  ""988888888888888888888888888888888
888888888888888888888P"88888P          988888"988888888888888888888888
888888888888888888888  "9888            888P"  88888888888888888888888
88888888888888888888888bo "9  d8o  o8b  P" od8888888888888888888888888
88888888888888888888888888bob 98"  "8P dod8888888888888888888888888888
88888888888888888888888888888    db    8888888888888888888888888888888
8888888888888888888888888888888      888888888888888888888888888888888
8888888888888888888888888888P"9bo  odP"9888888888888888888888888888888
8888888888888888888888888P" od88888888bo "9888888888888888888888888888
88888888888888888888888   d88888888888888b   8888888888888888888888888
888888888888888888888888oo8888888888888888oo88888888888888888888888888
8888888888888888888888888888888888888888888888888888888888888888888888"""

def welcome_screen():
    """Displays a welcome screen with ASCII art and some nice formatting."""
    print("\n" + "="*70)
    print(" "*17 + "WELCOME TO THE PASTEBIN LEAK SCRAPER")
    print("-"*70)
    print(ASCII_ART)
    print("-"*70)
    print(" "*10 +"This tool lets you monitor Pastebin for new data!")
    print(" "*17 + "Program created by: Benjamin Barish")
    print("="*70)
    print("[+] If a leak is detected, it will be saved to 'leaked_pastes.txt'.")
    print("[+] Press CTRL+C or type 'exit' at any time to stop the script.")
    input("\nPress ENTER to start monitoring...")

PASTEBIN_URL = "https://pastebin.com/archive"
# Refined keywords to focus on usernames and passwords
KEYWORDS = [
    "username", "user=", "login", "email", "password", "pass=", 
    "passwd=", "api_key", "token", "secret", "credentials", "auth"
]

# Define a list of gift card-related phrases to filter out
GIFT_CARD_KEYWORDS = [
    "get any gift card for free", "free giftcards method", "giftcards for free"
]

found_leaks = 0  # Counter for detected leaks
running = True  # Flag to control program execution
processed_pastes = set()  # Set to store processed paste URLs

def get_recent_pastes():
    """Fetches recent pastes from Pastebin."""
    try:
        response = requests.get(PASTEBIN_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to fetch Pastebin archive: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=re.compile(r"^/([A-Za-z0-9]{8})$"))
    paste_links = ["https://pastebin.com" + link['href'] for link in links]
    return paste_links[:10]  # Limit to last 10 pastes

def check_paste_for_keywords(paste_url):
    """Fetches paste content and checks for sensitive keywords."""
    response = requests.get(paste_url)
    if response.status_code != 200:
        return None

    content = response.text.lower()

    # Extract the page's title and check for gift card-related keywords
    soup = BeautifulSoup(response.text, "html.parser")
    page_title = soup.title.string.lower() if soup.title else ""

    # Debugging output to track processed pastes (with title)
    print(f"Checking paste: {paste_url}")
    print(f"Page Title: {page_title}")

    # Check if the page's title contains any gift card-related content
    if any(gift_card_keyword in page_title for gift_card_keyword in GIFT_CARD_KEYWORDS):
        print(f"[-] Skipping gift card related paste (title contains keyword)")
        return None

    # Check if the paste contains any of the sensitive keywords in the content
    for keyword in KEYWORDS:
        if keyword in content:
            # Extract the actual leaked content (before saving)
            leaked_content = re.findall(r"([^\n]*(" + "|".join(KEYWORDS) + r")[^\n]*)", content)
            # Join all the found leaks to make it easier to read
            leak = "\n".join([line[0] for line in leaked_content])
            return leak
    return None

def monitor_pastebin():
    """Monitors Pastebin for leaked credentials."""
    global found_leaks
    print("[+] Monitoring Pastebin for leaks...\n")

    while running:
        pastes = get_recent_pastes()
        for paste in pastes:
            if not running:
                break  # Stop loop if user exits
            if paste in processed_pastes:
                continue  # Skip paste if already processed
            content = check_paste_for_keywords(paste)
            if content:
                found_leaks += 1
                with open("leaked_pastes.txt", "a", encoding="utf-8") as file:
                    file.write(f"{paste}\n{content}\n{'-'*50}\n")
                
                print(f"[!] Leak detected: {paste}")
                print(f"[+] Leak saved to leaked_pastes.txt\n")
            
            # Mark the paste as processed
            processed_pastes.add(paste)
        
        print(f"[*] Monitoring... Total leaks found: {found_leaks}", end="\r")
        time.sleep(60)  # Wait 1 minute before checking again

def user_prompt():
    """Handles user input for stopping the program."""
    global running
    while running:
        try:
            user_input = input("\nType 'exit' to stop monitoring: ").strip().lower()
            if user_input == "exit":
                print("\n[!] Stopping Pastebin monitoring... Goodbye!")
                running = False
                break
        except KeyboardInterrupt:
            print("\n[!] Program interrupted. Exiting gracefully...")
            running = False
            break

if __name__ == "__main__":
    welcome_screen()

    # Run monitoring in a separate thread so user can stop it anytime
    monitoring_thread = threading.Thread(target=monitor_pastebin)
    monitoring_thread.start()
    
    # Handle user input and catch KeyboardInterrupt for graceful exit
    user_prompt()  

    monitoring_thread.join()  # Ensure thread stops before exiting
