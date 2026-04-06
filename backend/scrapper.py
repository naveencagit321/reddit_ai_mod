import requests
import json
import os

# --- TOOL 1: The Feed Scanner ---
def scrape_reddit(subreddit: str, limit: int = 10, sort_by: str = "hot"):
    """
    Dynamically fetches posts from a given subreddit based on sort type.
    """
    valid_sorts = ["hot", "new", "top", "rising", "controversial"]
    if sort_by not in valid_sorts:
        sort_by = "hot"

    url = f"https://www.reddit.com/r/{subreddit}/{sort_by}.json?limit={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Fetching {limit} posts from r/{subreddit}...\n" + "-"*40)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        posts_list = data['data']['children']
        clean_posts_data = []
        
        for i, post in enumerate(posts_list): 
            if len(clean_posts_data) >= limit:
                break
                
            title = post['data'].get('title', '')
            body = post['data'].get('selftext', '')
            post_id = post['data'].get('id', 'Unknown')
            
            full_text = f"{title}. {body}".strip()
            
            if not full_text:
                continue
                
            post_dict = {
                "id": post_id,
                "text": full_text
            }
            clean_posts_data.append(post_dict)
            print(f"Scraped Post {i+1} successfully.")

        print("-" * 40)
        return clean_posts_data

    else:
        raise Exception(f"Reddit blocked the request. Status code: {response.status_code}")


# --- TOOL 2: The Deep Dive Investigator ---
def scrape_post_comments(subreddit: str, post_id: str):
    """
    Fetches a specific post and uses recursion to extract every nested comment.
    """
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch comments.")
        
    data = response.json()
    
    # Reddit's JSON returns a list: [0] is the Post, [1] is the Comment Tree
    comment_tree = data[1]['data']['children']
    flat_comments = []
    
    # The Recursive Engine
    def extract_replies(comments_list):
        for item in comments_list:
            if item.get('kind') == 't1': 
                comment_data = item['data']
                text = comment_data.get('body', '')
                
                if text and text not in ["[deleted]", "[removed]"]:
                    flat_comments.append({
                        "id": comment_data.get('id'),
                        "parent_id": comment_data.get('parent_id'),
                        "text": text
                    })
                
                # If this comment has replies, dig deeper!
                replies = comment_data.get('replies')
                if replies and isinstance(replies, dict):
                    extract_replies(replies['data']['children'])

    extract_replies(comment_tree)
    print(f"Successfully extracted {len(flat_comments)} nested comments from the thread!")
    return flat_comments