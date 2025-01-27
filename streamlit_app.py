import streamlit as st
import pandas as pd
import json
from datetime import datetime
from instagram_selenium_scraper import InstagramSeleniumScraper
# from youtube_selenium_scraper import YouTubeSeleniumScraper
import time
import atexit
import re

# Initialize Streamlit app
st.set_page_config(page_title="Social Media Scraper")
st.title("Social Media Scraper")
st.markdown("Enter an URL to scrape data")

# Initialize session state for scrapers
if 'instagram_scraper' not in st.session_state:
    st.session_state['instagram_scraper'] = None
if 'youtube_scraper' not in st.session_state:
    st.session_state['youtube_scraper'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Instagram credentials
USERNAME = "vomychat_assignment"
PASSWORD = "vomychat201"

# Input fields
url_input = st.text_input("Enter URL")

# Initialize appropriate scraper based on URL
def initialize_scraper(url):
    if 'instagram.com' in url:
        if not st.session_state['instagram_scraper']:
            st.session_state['instagram_scraper'] = InstagramSeleniumScraper()
        return 'instagram'
    # elif 'youtube.com' in url or 'youtu.be' in url:
        # if not st.session_state['youtube_scraper']:
            # st.session_state['youtube_scraper'] = YouTubeSeleniumScraper()
        # return 'youtube'
    # return None

# Scrape button
if st.button("Scrape"):
    if not url_input:
        st.warning("Please enter a URL")
    else:
        platform = initialize_scraper(url_input)
        
        if not platform:
            st.warning("Invalid URL. Please enter a valid Instagram or YouTube URL")
        else:
            try:
                with st.spinner('Scraping data...'):
                    if platform == 'instagram':
                        # Login to Instagram first if not logged in
                        if not st.session_state['logged_in']:
                            with st.spinner('Logging in to Instagram...'):
                                max_retries = 3
                                for attempt in range(max_retries):
                                    if st.session_state['instagram_scraper'].login(USERNAME, PASSWORD):
                                        st.session_state['logged_in'] = True
                                        st.success("Successfully logged in to Instagram!")
                                        break
                                    time.sleep(5)
                                
                                if not st.session_state['logged_in']:
                                    st.error(f"Failed to login after {max_retries} attempts")
                                    st.stop()

                        # Determine if it's a profile or post URL
                        is_post = '/p/' in url_input
                        is_profile = bool(re.match(r'https?://(?:www\.)?instagram\.com/[^/]+/?$', url_input))

                        if is_post:
                            # Handle post URL
                            if st.session_state['instagram_scraper'].verify_post_exists(url_input):
                                post_data = st.session_state['instagram_scraper'].get_post_details(url_input)
                                
                                if post_data:
                                    # Display post data
                                    st.markdown("## Instagram Post Details")
                                    
                                    # Engagement metrics
                                    st.markdown("### Engagement Metrics")
                                    # Handle likes with commas
                                    likes = post_data.get('likes', '0')
                                    if isinstance(likes, str):
                                        likes = int(likes.replace(',', ''))
                                    st.metric("Likes", value=f"{int(likes):,}")
                                    
                                    # Post text
                                    if post_data.get('text', 'Not available') != 'Not available':
                                        st.markdown("### Post Text")
                                        st.write(post_data['text'])
                                    
                                    # Download buttons
                                    st.markdown("### Download Data")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.download_button(
                                            "Download JSON",
                                            data=json.dumps(post_data, indent=2),
                                            file_name=f"instagram_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json"
                                        )
                                    with col2:
                                        df = pd.DataFrame([post_data])
                                        st.download_button(
                                            "Download CSV",
                                            data=df.to_csv(index=False),
                                            file_name=f"instagram_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv"
                                        )
                                else:
                                    st.error("Failed to get post data")
                            else:
                                st.error("This post doesn't exist or has been removed")

                        elif is_profile:
                            # Handle profile URL
                            profile_data = st.session_state['instagram_scraper'].get_profile_details(url_input)
                            
                            if profile_data:
                                # Display profile data
                                st.markdown("## Instagram Profile Details")
                                
                                # Basic information
                                st.markdown("### Basic Information")
                                st.write(f"Username: {profile_data.get('username', 'Not available')}")
                                
                                # Profile metrics
                                st.markdown("### Profile Metrics")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    followers = profile_data.get('followers_count', 'Not available')
                                    st.metric("Followers", value=followers)
                                with col2:
                                    following = profile_data.get('following_count', 'Not available')
                                    st.metric("Following", value=following)
                                with col3:
                                    posts = profile_data.get('posts_count', 'Not available')
                                    st.metric("Posts", value=posts)
                                
                                # Recent posts
                                if profile_data.get('post_urls'):
                                    st.markdown("### Recent Posts")
                                    st.write(f"Found {len(profile_data['post_urls'])} recent posts")
                                    for url in profile_data['post_urls'][:5]:  # Show first 5 posts
                                        st.write(url)
                                
                                # Download buttons
                                st.markdown("### Download Data")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "Download JSON",
                                        data=json.dumps(profile_data, indent=2),
                                        file_name=f"instagram_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                with col2:
                                    df = pd.DataFrame([profile_data])
                                    st.download_button(
                                        "Download CSV",
                                        data=df.to_csv(index=False),
                                        file_name=f"instagram_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                st.error("Failed to get profile data")
                        
                        else:
                            st.error("Please enter a valid Instagram profile or post URL")
                            
                    elif platform == 'youtube':
                        # Handle YouTube URL
                        if 'watch?v=' in url_input or 'youtu.be' in url_input:
                            video_data = st.session_state['youtube_scraper'].get_video_details(url_input)
                            
                            if video_data:
                                # Display YouTube video data
                                st.markdown("## YouTube Video Details")
                                
                                # Basic information
                                st.markdown("### Basic Information")
                                st.write(f"Title: {video_data.get('title', 'Not available')}")
                                st.write(f"Channel: {video_data.get('channel_name', 'Not available')}")
                                st.write(f"Published: {video_data.get('created_date', 'Not available')}")
                                
                                # Handle subscriber count formatting
                                subscribers = video_data.get('subscribers_count', 'Not available')
                                if isinstance(subscribers, (int, float)):
                                    st.write(f"Subscribers: {int(subscribers):,}")
                                else:
                                    st.write(f"Subscribers: {subscribers}")
                                
                                # Engagement metrics
                                st.markdown("### Engagement Metrics")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    views = video_data.get('views', 0)
                                    if isinstance(views, (int, float)):
                                        st.metric("Views", value=f"{int(views):,}")
                                    else:
                                        st.metric("Views", value="0")
                                
                                with col2:
                                    likes = video_data.get('likes', 0)
                                    if isinstance(likes, (int, float)):
                                        st.metric("Likes", value=f"{int(likes):,}")
                                    else:
                                        st.metric("Likes", value="0")
                                
                                with col3:
                                    comments = video_data.get('comments', 0)
                                    if isinstance(comments, (int, float)):
                                        st.metric("Comments", value=f"{int(comments):,}")
                                    else:
                                        st.metric("Comments", value="0")
                                
                                # Description
                                if video_data.get('description', 'Not available') != 'Not available':
                                    st.markdown("### Description")
                                    st.write(video_data['description'])
                                
                                # Download buttons
                                st.markdown("### Download Data")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "Download JSON",
                                        data=json.dumps(video_data, indent=2),
                                        file_name=f"youtube_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                with col2:
                                    df = pd.DataFrame([video_data])
                                    st.download_button(
                                        "Download CSV",
                                        data=df.to_csv(index=False),
                                        file_name=f"youtube_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                st.error("Failed to get YouTube video data")
                        else:
                            st.error("Please enter a valid YouTube video URL")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Cleanup on session end
def cleanup():
    if st.session_state.get('instagram_scraper'):
        st.session_state['instagram_scraper'].close()
    if st.session_state.get('youtube_scraper'):
        st.session_state['youtube_scraper'].close()

# Register cleanup
atexit.register(cleanup)