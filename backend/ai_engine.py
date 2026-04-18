import os
# 1. FORCE THE OS TO USE SINGLE-THREADING BEFORE LOADING AI
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MALLOC_ARENA_MAX"] = "2"

import torch
# 2. FORCE PYTORCH TO ONLY USE 1 THREAD
torch.set_num_threads(1)
from transformers import pipeline

print("Downloading and Loading Local AI Model...")
classifier = pipeline("text-classification", model="martin-ha/toxic-comment-model")
print("Model loaded successfully!")

print("Warming up the AI engine...")
classifier("This is a test run to warm up the tensor memory.") 

print("Model loaded successfully and ready for production!")

def analyze_toxicity_locally(reddit_comments):
    analysis_results = []
    
    for item in reddit_comments:
        try:
            # 1. THE FIX: Extract the actual text string from the dictionary
            if isinstance(item, dict):
                # Most Reddit scrapers save the text under 'title', 'body', 'selftext', or 'text'
                # This safely grabs whatever text is available.
                comment_text = item.get('title', '') + " " + item.get('selftext', item.get('body', item.get('text', '')))
            else:
                # If it's already a string, just use it
                comment_text = str(item)

            # Clean up extra spaces
            comment_text = comment_text.strip()
            
            # Skip if the post has no text
            if not comment_text:
                continue

            # 2. NOW we can safely slice the string!
            ai_prediction = classifier(comment_text[:512])[0] 
            label = ai_prediction['label']
            confidence = round(ai_prediction['score'] * 100, 2)
            
            analysis_results.append({
                "text": comment_text,
                "is_toxic": label == 'toxic',
                "confidence_score": confidence,
                "reasoning": f"Flagged by local ML model with {confidence}% confidence."
            })
            
        except Exception as e:
            print(f"Error analyzing comment: {e}")
            
    toxic_count = sum(1 for item in analysis_results if item['is_toxic'])
    total_comments = len(analysis_results)
    
    if total_comments > 0:
        overall_safety = 100 - ((toxic_count / total_comments) * 100)
    else:
        overall_safety = 100.0
    
    return {
        "overall_safety_score": round(overall_safety, 2),
        "analyzed_comments": analysis_results
    }