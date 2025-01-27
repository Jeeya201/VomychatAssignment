# 📸 Instagram Scraper Bot 🚀

## 🌟 Overview
The **Instagram Scraper Bot** is a powerful and efficient application designed to scrape Instagram post or profile data seamlessly. With automated login capabilities using Selenium and a user-friendly interface built with Streamlit, this bot makes it easy to gather valuable information from Instagram effortlessly.

---

## ✨ Features

- 🔐 **Automatic Login**: Securely logs into Instagram using your credentials.
- 👥 **Profile Scraping**: Scrapes follower and following data from any public profile.
- ❤️ **Post Scraping**: Extracts likes and comments data from Instagram posts.
- 💻 **Modern UI**: A sleek and intuitive user interface powered by Streamlit.
- 🛠️ **Customizable Options**: Choose between scraping followers, following, likes, or comments.
- 🛡️ **Secure Credentials Handling**: Uses environment variables to store Instagram login credentials securely.

---

## 🛠️ Tech Stack

- **Backend**: Selenium for browser automation.
- **Frontend**: Streamlit for a seamless user experience.
- **Environment Management**: Python dotenv for secure credentials management.

---

## 📋 Prerequisites

1. **Python**: Make sure Python 3.7 or higher is installed on your system.
2. **Browser Driver**: Install the appropriate WebDriver for Selenium (e.g., ChromeDriver for Google Chrome).
3. **Instagram Account**: Ensure your Instagram account is active and can log in manually.

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/instagram-scraper-bot.git
   cd instagram-scraper-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install and configure the WebDriver for your browser.

---

## 🚀 Usage

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open the app in your browser at `http://localhost:8501`.

3. Enter the Instagram URL you want to scrape and select the desired action (e.g., scrape followers, following, likes, or comments).

4. View the scraped data directly in the app or export it as a CSV file.

---

## 📷 Screenshots

1. **🔒 Login Screen**  
   *A simple and secure interface to log in to Instagram.*

2. **📊 Scraping Dashboard**  
   *Choose between scraping followers, following, likes, or comments.*

3. **📁 Results Viewer**  
   *View or export the scraped data in real-time.*

---

## 🔒 Security

- **Rate Limiting**: Built-in mechanisms to avoid triggering Instagram's rate limits or bot detection.

---

## 🌟 Future Improvements
- ⚡ Adding other social media options apart from instagram
- 🖼️ Support for additional scraping options such as stories and hashtags.
- 📈 Enhanced error handling and logging for a smoother experience.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Scraping data from Instagram may violate their Terms of Service. Use responsibly.
