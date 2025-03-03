import requests
import re
import time
import threading
from bs4 import BeautifulSoup

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

PASTEBIN_URL = "https://pastebin.com/archive"
KEYWORDS = ["username", "user=", "login", "email", "password", "pass=", "passwd=", "api_key", "token", "secret", "credentials", "auth"]
GIFT_CARD_KEYWORDS = ["get any gift card for free", "free giftcards method", "giftcards for free", "giftcard", "$"]

found_leaks = 0
processed_pastes = set()
exit_event = threading.Event()  # Used for clean exit

def welcome_screen():
    """Displays a welcome screen before starting monitoring."""
    print("\n" + "=" * 70)
    print(" "*17 + "WELCOME TO THE PASTEBIN LEAK SCRAPER")
    print("-" * 70)
    print(ASCII_ART)
    print("-" * 70)
    print(" "*10 + "This tool lets you monitor Pastebin for new data!")
    print(" "*17 + "Program created by: Benjamin Barish")
    print("=" * 70)
    print("[+] If a leak is detected, it will be saved to 'leaked_pastes.txt'.")
    print("[+] Press CTRL+C or type 'exit' at any time to stop the script.")
    input("\nPress ENTER to start monitoring...")  # Ensures user must press Enter before starting

def get_recent_pastes():
    """Fetches recent pastes from Pastebin."""
    try:
        response = requests.get(PASTEBIN_URL, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to fetch Pastebin archive: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=re.compile(r"^/([A-Za-z0-9]{8})$"))
    return ["https://pastebin.com" + link['href'] for link in links][:10]  # Limit to last 10 pastes

def check_paste_for_keywords(paste_url):
    """Fetches paste content and checks for sensitive keywords."""
    try:
        response = requests.get(paste_url, timeout=10)
        if response.status_code != 200:
            return None, None
    except requests.exceptions.RequestException:
        return None, None
    
    content = response.text.lower()
    soup = BeautifulSoup(response.text, "html.parser")
    page_title = soup.title.string.strip() if soup.title else "Untitled"
    
    if any(keyword in page_title.lower() for keyword in GIFT_CARD_KEYWORDS):
        print(f"[-] Skipping paste (gift card related): {page_title}")
        return None, None
    
    for keyword in KEYWORDS:
        if keyword in content:
            leaked_content = re.findall(r"([^\n]*(" + "|".join(KEYWORDS) + r")[^\n]*)", content)
            leak = "\n".join([line[0] for line in leaked_content])
            return page_title, leak
    return None, None

def monitor_pastebin():
    """Monitors Pastebin for leaked credentials."""
    global found_leaks
    print("[+] Monitoring Pastebin for leaks...\n")

    while not exit_event.is_set():  # Loop until exit event is triggered
        pastes = get_recent_pastes()
        for paste in pastes:
            if exit_event.is_set():
                break  
            if paste in processed_pastes:
                continue  
            page_title, content = check_paste_for_keywords(paste)
            if content:
                found_leaks += 1
                with open("leaked_pastes.txt", "a", encoding="utf-8") as file:
                    file.write(f"Title: {page_title}\nURL: {paste}\n{'-'*50}\n")
                
                print(f"[!] Leak detected: {page_title} ({paste})")
                print(f"[+] Leak saved to leaked_pastes.txt\n")
            
            processed_pastes.add(paste)
        
        print(f"[*] Monitoring... Total leaks found: {found_leaks}", end="\r")
        time.sleep(60)  

def user_prompt():
    """Handles user input for stopping the program."""
    global exit_event
    while not exit_event.is_set():
        try:
            user_input = input("\nType 'exit' to stop monitoring: ").strip().lower()
            if user_input == "exit":
                print("\n[!] Stopping Pastebin monitoring... Goodbye!")
                exit_event.set()  # Stop the monitoring thread
                break
        except KeyboardInterrupt:
            print("\n[!] Program interrupted. Exiting gracefully...")
            exit_event.set()
            break

if __name__ == "__main__":
    welcome_screen()  # User must press Enter first

    print("[+] Starting Pastebin Leak Detector...")

    monitoring_thread = threading.Thread(target=monitor_pastebin, daemon=True)  # Daemon thread exits with main program
    monitoring_thread.start()
    
    user_prompt()  # Handles user input
    
    monitoring_thread.join()  # Wait for monitoring thread to finish
    print("[+] Program exited cleanly.")
