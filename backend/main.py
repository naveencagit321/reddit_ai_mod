from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scrapper import scrape_reddit, scrape_post_comments
from ai_engine import run_ai_analysis, analyze_full_thread  # <-- ADD THIS LINE
import json
import os

app = FastAPI(title="Reddit AI Moderation API")

# --- 1. CORS Setup ---
# This allows your React frontend to talk to this Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# --- 2. Static Dashboard Endpoint ---
# This loads the saved JSON file when you first open the React app
@app.get("/api/comments")
async def get_comments():
    try:
        # Navigate to the data folder and read the JSON
        file_path = os.path.join(os.path.dirname(__file__), "..", "data", "moderated_thread_data.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 3. Dynamic Search Endpoint ---
# This listens for the new search bar requests from React
@app.get("/api/scan")
async def scan_subreddit(
    subreddit: str = Query(..., description="The name of the subreddit"),
    limit: int = Query(10, description="Number of posts to analyze")
):
    try:
        # 1. Call your brand new scraper function!
        raw_data = scrape_reddit(subreddit, limit)
        
        analyzed_data = run_ai_analysis(raw_data)
        # 2. THE FINAL MISSING PIECE: The AI Engine
        # We will plug your ai_engine.py function in right here next.
        # analyzed_data = run_ai_analysis(raw_data)
        
        # Temporarily return the RAW data to React just to prove the scraper works
        return {"status": "success", "data": analyzed_data}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/deep-dive")
async def deep_dive_thread(
    subreddit: str = Query(..., description="The name of the subreddit"),
    post_id: str = Query(..., description="The ID of the specific post")
):
    try:
        # 1. Recursively scrape every nested comment
        flat_comments = scrape_post_comments(subreddit, post_id)
        
        # 2. If the thread is empty, handle it gracefully
        if not flat_comments:
            return {
                "status": "success", 
                "data": {
                    "thread_verdict": "Safe", 
                    "overall_reasoning": "No comments found on this post.", 
                    "flagged_comments": []
                }
            }
            
        # 3. Send the whole tree to Gemini
        thread_analysis = analyze_full_thread(flat_comments)
        
        # 4. Return the master report to React
        return {"status": "success", "data": thread_analysis}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}    

        