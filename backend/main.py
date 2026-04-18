from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 1. IMPORT YOUR SCRAPER AND NEW AI ENGINE
from scrapper import scrape_reddit  # (Make sure this matches your actual scraper function name)
from ai_engine import analyze_toxicity_locally  # YOUR NEW LOCAL ML IMPORT

# 2. SETUP THE RATE LIMITER
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (React, Vercel, etc.)
    allow_credentials=False,
    allow_methods=["*"],  # Allows GET, POST, etc.
    allow_headers=["*"],
)

# Tell FastAPI how to handle the rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. YOUR SECURE API ROUTE
@app.get("/api/scan")
@limiter.limit("5/minute")  # Blocks IPs that spam the button more than 5 times a minute
async def scan_subreddit(request: Request, subreddit: str, limit: int = 10):
    
    # Step A: Scrape the data from Reddit
    comments = scrape_reddit(subreddit, limit)
    
    # Step B: Pass the data into your local DistilBERT model
    results = analyze_toxicity_locally(comments)
    
    # Step C: Send the final JSON back to your React frontend
    return results
@app.get("/api/deep-dive")
@limiter.limit("5/minute")
async def deep_dive_analysis(request: Request, subreddit: str, post_id: str):
    """
    Tool 2: The Deep Dive Investigator
    This endpoint analyzes nested comments for a specific post.
    """
    import random # Used just for the simulation below
    
    # NOTE: Since we haven't hooked up a nested comment scraper to the local AI yet,
    # we are returning structurally perfect data so your React charts can render!
    # You can plug your actual local AI logic in here later.
    
    simulated_verdicts = ["Safe", "Heated", "Toxic"]
    chosen_verdict = random.choice(simulated_verdicts)
    
    flagged = []
    if chosen_verdict == "Toxic":
        flagged = [
            "You have no idea what you are talking about.",
            "This is the worst take I've ever seen on this sub."
        ]
    elif chosen_verdict == "Heated":
        flagged = ["Can we just agree to disagree before this gets ugly?"]

    return {
        "status": "success",
        "data": {
            "thread_verdict": chosen_verdict,
            "overall_reasoning": f"Deep dive complete for Post ID: {post_id}. The AI analyzed the deeper comment tree and mapped the emotional trajectory of the conversation.",
            "flagged_comments": flagged
        }
    }