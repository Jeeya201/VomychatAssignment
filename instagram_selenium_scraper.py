from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime
import os
import re
from selenium.webdriver.common.keys import Keys

class InstagramSeleniumScraper:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.setup_driver()

    def setup_driver(self):
        """Initialize the Chrome WebDriver"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def login(self, username, password):
        """Login to Instagram"""
        try:
            # Open Instagram login page
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)

            # Find and fill username field
            username_field = self.driver.find_element(By.NAME, "username")
            username_field.send_keys(username)
            time.sleep(2)

            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            time.sleep(2)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(5)

            # Open new tab
            self.driver.execute_script("window.open()")
            new_tab = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_tab)
            time.sleep(6)

            self.is_logged_in = True
            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_profile_details(self, profile_url):
        """Get details of an Instagram profile"""
        if not self.is_logged_in:
            return None

        try:
            # Navigate to profile URL
            self.driver.get(profile_url)
            time.sleep(5)  # Wait for page to load

            # Initialize profile data
            profile_data = {
                'username': profile_url.split('instagram.com/')[1].replace('/', ''),
                'url': profile_url,
                'full_name': 'Not available',
                'bio': 'Not available',
                'followers_count': 0,
                'following_count': 0,
                'posts_count': 0,
                'post_urls': [],
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }

            try:
                # Get profile metrics using ul and li tags
                ul = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'ul'))
                )
                items = ul.find_elements(By.TAG_NAME, 'li')

                for li in items:
                    text = li.text.lower()
                    try:
                        if 'followers' in text:
                            followers_text = text.replace(',', '').split()[0]
                            if 'k' in followers_text.lower():
                                followers_text = float(followers_text.replace('k', '')) * 1000
                            elif 'm' in followers_text.lower():
                                followers_text = float(followers_text.replace('m', '')) * 1000000
                            profile_data['followers_count'] = int(float(followers_text))
                            print(f"Found followers: {profile_data['followers_count']}")
                        
                        elif 'following' in text:
                            following_text = text.replace(',', '').split()[0]
                            if 'k' in following_text.lower():
                                following_text = float(following_text.replace('k', '')) * 1000
                            elif 'm' in following_text.lower():
                                following_text = float(following_text.replace('m', '')) * 1000000
                            profile_data['following_count'] = int(float(following_text))
                            print(f"Found following: {profile_data['following_count']}")
                        
                        elif 'posts' in text:
                            posts_text = text.replace(',', '').split()[0]
                            profile_data['posts_count'] = int(float(posts_text))
                            print(f"Found posts: {profile_data['posts_count']}")
                    except Exception as e:
                        print(f"Error parsing metric: {str(e)}")
                        continue

                # Get full name
                try:
                    header = self.driver.find_element(By.TAG_NAME, 'header')
                    h1 = header.find_element(By.TAG_NAME, 'h1')
                    profile_data['full_name'] = h1.text
                    print(f"Found full name: {profile_data['full_name']}")
                except:
                    print("Could not find full name")

                # Get bio
                try:
                    header = self.driver.find_element(By.TAG_NAME, 'header')
                    sections = header.find_elements(By.TAG_NAME, 'section')
                    for section in sections:
                        if section.text and 'posts' not in section.text.lower():
                            profile_data['bio'] = section.text
                            print(f"Found bio: {profile_data['bio']}")
                            break
                except:
                    print("Could not find bio")

                # Get recent post URLs
                try:
                    article_elements = self.driver.find_elements(By.TAG_NAME, 'article')
                    for article in article_elements:
                        a_tags = article.find_elements(By.TAG_NAME, 'a')
                        for a in a_tags:
                            href = a.get_attribute('href')
                            if href and '/p/' in href:
                                profile_data['post_urls'].append(href)
                    print(f"Found {len(profile_data['post_urls'])} post URLs")
                except:
                    print("Could not find post URLs")

                # Take screenshot for debugging
                self.driver.save_screenshot("profile_debug.png")
                print("\nProfile Data Found:")
                for key, value in profile_data.items():
                    if key != 'post_urls':  # Don't print the full list of URLs
                        print(f"{key}: {value}")

                return profile_data

            except Exception as e:
                print(f"Error extracting profile data: {str(e)}")
                self.driver.save_screenshot("profile_error.png")
                return profile_data

        except Exception as e:
            print(f"Error accessing profile: {str(e)}")
            self.driver.save_screenshot("error_page.png")
            return None

    def get_post_details(self, post_url):
        """Get details of a specific post"""
        if not self.is_logged_in:
            return None

        try:
            # First navigate to the post URL directly (without parameters)
            self.driver.get(post_url)
            time.sleep(5)

            # Initialize post data
            post_data = {
                'url': post_url,
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'likes': 'Not available',
                'comments': 'Not available',
                'media_urls': [],
                'text': 'Not available'
            }

            try:
                # Get likes count
                likes_selectors = [
                    "//span[@class='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj']",
                    "//section[@class='x12nagc']//span//span",
                    "//a[contains(@href, 'liked_by')]/span/span"
                ]

                for selector in likes_selectors:
                    try:
                        likes_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        post_data['likes'] = likes_element.text
                        print(f"Found likes: {likes_element.text}")
                        break
                    except:
                        continue

                # Get comments count
                comments_selectors = [
                    "//span[contains(@class, '_aacl _aaco')]//span[contains(text(), 'comments')]",
                    "//div[contains(@class, 'x4h1yfo')]//span[contains(text(), 'comments')]",
                    "//span[contains(text(), 'comments')]/parent::span/parent::button"
                ]

                for selector in comments_selectors:
                    try:
                        comments_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        comments_text = comments_element.text
                        # Extract number from "X comments"
                        comments_count = comments_text.split()[0]
                        post_data['comments'] = comments_count
                        print(f"Found comments: {comments_count}")
                        break
                    except:
                        continue

                # Now get the JSON data for media URLs
                modified_url = f"{post_url}?__a=1&__d=dis"
                self.driver.get(modified_url)
                time.sleep(5)

                # Wait for and get JSON data
                pre_element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'pre'))
                )
                json_data = json.loads(pre_element.text)

                # Process JSON data for media URLs
                if 'items' in json_data:
                    item = json_data['items'][0]
                    
                    # Get carousel media if available
                    if 'carousel_media' in item:
                        for media in item['carousel_media']:
                            if 'image_versions2' in media:
                                post_data['media_urls'].append(
                                    media['image_versions2']['candidates'][0]['url']
                                )
                            if 'video_versions' in media:
                                post_data['media_urls'].append(
                                    media['video_versions'][0]['url']
                                )
                    
                    # Get single image/video if no carousel
                    else:
                        if 'image_versions2' in item:
                            post_data['media_urls'].append(
                                item['image_versions2']['candidates'][0]['url']
                            )
                        if 'video_versions' in item:
                            post_data['media_urls'].append(
                                item['video_versions'][0]['url']
                            )

                    # Get post text if available
                    if 'caption' in item and item['caption']:
                        post_data['text'] = item['caption']['text']

                # Take screenshot for debugging
                self.driver.save_screenshot("post_debug.png")
                print("\nPost Data Found:")
                for key, value in post_data.items():
                    print(f"{key}: {value}")

                return post_data

            except Exception as e:
                print(f"Error extracting post data: {str(e)}")
                self.driver.save_screenshot("post_error.png")
                return post_data

        except Exception as e:
            print(f"Error accessing post: {str(e)}")
            self.driver.save_screenshot("error_page.png")
            return None

    def verify_post_exists(self, post_url):
        """Verify if a post exists before attempting to scrape it"""
        try:
            # Navigate to the post URL
            self.driver.get(post_url)
            time.sleep(3)

            # Check if error message exists
            error_messages = [
                "Sorry, this page isn't available.",
                "This page could not be found.",
                "Page not found"
            ]

            # Get page text
            page_text = self.driver.find_element(By.TAG_NAME, "body").text

            # Check for error messages
            for error in error_messages:
                if error in page_text:
                    print(f"Post not found: {error}")
                    return False

            # If no error messages found, post exists
            return True

        except Exception as e:
            print(f"Error verifying post: {str(e)}")
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    # Instagram credentials
    USERNAME = "vomychat_assignment"
    PASSWORD = "vomychat201"
    
    # Initialize scraper
    scraper = InstagramSeleniumScraper()
    
    try:
        # Login with retry
        max_retries = 3
        login_success = False
        
        for attempt in range(max_retries):
            print(f"\nLogin attempt {attempt + 1}")
            if scraper.login(USERNAME, PASSWORD):
                login_success = True
                break
            time.sleep(5)
        
        if login_success:
            # Wait after successful login
            time.sleep(5)
            
            # Get post URL from user
            print("\nEnter the URL")
            print("Example: https://www.instagram.com/username/p/POST_ID/")
            post_url = input("URL: ").strip()
            
            if not post_url:
                print("No URL provided")
            elif 'instagram.com' not in post_url or '/p/' not in post_url:
                print("Invalid URL format. URL should be like: https://www.instagram.com/username/p/POST_ID/")
            else:
                # Verify post exists
                if scraper.verify_post_exists(post_url):
                    # Get post data
                    post_data = scraper.get_post_details(post_url)
                    
                    if post_data:
                        print("\nPost Details:")
                        print(json.dumps(post_data, indent=2))
                        
                        # Save to file
                        with open('post_data.json', 'w', encoding='utf-8') as f:
                            json.dump(post_data, f, indent=2, ensure_ascii=False)
                        print("\nData saved to post_data.json")
                    else:
                        print("Failed to get post data")
                else:
                    print("Post not found")
        else:
            print(f"\nFailed to login after {max_retries} attempts")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
    
    finally:
        # Always close the browser
        scraper.close() 