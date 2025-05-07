import praw
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

# Reddit API credentials
client_id = "Y7Wm0o9zxTxEfSDMH_80Zw"
client_secret = "8175uluLf3xI480uypujZEWjkHNwGQ"
user_agent = "media_scraper"

# Initialize Reddit client
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# Function to search Reddit
def search_reddit(keyword, limit=10):
    search_results = []
    try:
        # Search Reddit for the given keyword
        for submission in reddit.subreddit("all").search(keyword, limit=limit):
            search_results.append({
                'title': submission.title,
                'url': submission.url,
                'media_type': 'link'  # Default to link, can be adjusted for images/videos later
            })
    except Exception as e:
        print(f"Error while fetching data from Reddit: {e}")
    return search_results

# Function to search simpcity.su
def search_simpcity_su(keyword, limit=10):
    search_results = []
    try:
        # Replace spaces with '+' to match URL format
        keyword = keyword.replace(" ", "+")
        
        # Format the URL to include the search term
        url = f"https://simpcity.su/search/30078589/?q={keyword}&c[title_only]=1&o=date"
        
        # Make a request to the website's search page with the formatted URL
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Example: Assume the website has <a> tags for links in a specific structure
        results = soup.find_all("a", class_="result-link", limit=limit)  # Adjust the tag and class as needed

        for result in results:
            title = result.get_text()
            url = result['href']
            media_type = 'link'  # Assuming it's a link for now

            # Check if it's an image or video (very basic example)
            if url.endswith(('jpg', 'jpeg', 'png', 'gif')):
                media_type = 'image'
            elif url.endswith(('mp4', 'mov', 'webm')):
                media_type = 'video'

            search_results.append({
                'title': title,
                'url': url,
                'media_type': media_type
            })
    except Exception as e:
        print(f"Error while fetching data from simpcity.su: {e}")
    return search_results

# Function to search spankbang.com
def search_spankbang_com(keyword, limit=10):
    search_results = []
    try:
        # Make a request to the website's search page with the keyword
        response = requests.get(f"https://spankbang.com/search/{keyword}")
        soup = BeautifulSoup(response.content, "html.parser")

        # Example: Assume the website has <a> tags for links in a specific structure
        results = soup.find_all("a", class_="thumb__title", limit=limit)  # Adjust the tag and class as needed

        for result in results:
            title = result.get_text()
            url = result['href']
            media_type = 'link'  # Default as link

            # Check if it's an image or video (very basic example)
            if url.endswith(('jpg', 'jpeg', 'png', 'gif')):
                media_type = 'image'
            elif url.endswith(('mp4', 'mov', 'webm')):
                media_type = 'video'

            search_results.append({
                'title': title,
                'url': url,
                'media_type': media_type
            })
    except Exception as e:
        print(f"Error while fetching data from spankbang.com: {e}")
    return search_results

# Flask route to handle search requests
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]
        limit = int(request.form["limit"])
        source = request.form.get("source", "reddit")

        if source == "reddit":
            results = search_reddit(keyword, limit)
        elif source == "simpcity":
            results = search_simpcity_su(keyword, limit)
        elif source == "spankbang":
            results = search_spankbang_com(keyword, limit)

        if results:
            return render_template("index.html", keyword=keyword, results=results, source=source)
        else:
            return render_template("index.html", error="No results found or error fetching data.")
    
    return render_template("index.html", keyword="", results=[])

if __name__ == "__main__":
    app.run(debug=True)
