import os
import json
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# 1. Bulletproof .env loading
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)

google_key = os.getenv("GOOGLE_API_KEY")
if not google_key:
    raise ValueError("API Key not found! Please check your .env file.")

# 2. Initialize the Gemini 2.5 Flash Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.0,
    api_key=google_key 
)

# 3. Engineer the Moderator Persona Prompt
template = """
You are an expert Trust & Safety moderator for an online community.
Analyze the following text for harmful content (hate speech, severe toxicity, threats, or extreme harassment).
Ignore mild profanity or standard gaming/internet slang. Focus on actual malicious intent.

Comment Text: "{comment_text}"

You MUST respond with ONLY a raw JSON object. Do not use Markdown code blocks (```json).
The JSON object must have exactly these three keys:
- "verdict": "Harmful" or "Safe"
- "confidence_score": A number between 0.0 and 1.0
- "reasoning": A one-sentence explanation of why you chose this verdict.
"""

prompt = PromptTemplate(input_variables=["comment_text"], template=template)
moderator_chain = prompt | llm

def run_ai_analysis(raw_data):
    """
    Takes a list of raw reddit posts, runs them through Gemini, 
    and returns the list with AI analysis attached.
    """
    print(f"Starting AI Analysis on {len(raw_data)} posts...\n" + "-" * 40)
    analyzed_data = []

    for i, item in enumerate(raw_data):
        text = item.get('text', '')
        
        # Skip empty strings
        if not text.strip():
            continue
            
        print(f"Analyzing Post {i+1}...")
        
        try:
            # Send the text to Gemini
            response = moderator_chain.invoke({"comment_text": text})
            
            # Clean up the response just in case the AI added ```json formatting
            clean_text = response.content.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()

            # Parse the AI's string response back into a Python dictionary
            ai_verdict = json.loads(clean_text)
            
            # Combine the original comment data with the AI's verdict!
            item['ai_analysis'] = ai_verdict
            analyzed_data.append(item)
            
            print(f"Result: {ai_verdict.get('verdict', 'Unknown')}")
            
            # Pause for 1 second to avoid hitting free-tier API rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error analyzing post {i+1}: {e}")
            # Fallback so React doesn't crash if ONE comment fails
            item['ai_analysis'] = {
                "verdict": "Safe", 
                "confidence_score": 0.0, 
                "reasoning": "Error analyzing this post due to API failure."
            }
            analyzed_data.append(item)

    print("-" * 40 + "\nAI Analysis Complete!")
    return analyzed_data

    # --- The Supervisor Prompt for Full Threads ---
thread_template = """
You are a Lead Trust & Safety Moderator. Review the following Reddit comment thread.
Analyze the overall conversation for harmful intent, severe toxicity, or harassment. 
Understand the context: if a comment is sarcastic or quoting someone else, do not flag it.

Comment Thread:
{thread_text}

You MUST respond with ONLY a raw JSON object. Do not use Markdown code blocks.
The JSON object must have exactly these keys:
- "thread_verdict": "Safe", "Heated", or "Toxic"
- "overall_reasoning": A 2-sentence summary of the conversation's tone.
- "flagged_comments": A list of specific quotes from the thread that are harmful (leave empty if none).
"""

thread_prompt = PromptTemplate(input_variables=["thread_text"], template=thread_template)
thread_chain = thread_prompt | llm

def analyze_full_thread(flat_comments):
    """
    Takes a list of all nested comments, stitches them together, 
    and asks Gemini to analyze the entire conversation at once.
    """
    print(f"Starting Deep Dive Analysis on {len(flat_comments)} comments...\n")
    
    # 1. Stitch all comments into one readable script for the AI
    conversation_text = ""
    for i, comment in enumerate(flat_comments):
        conversation_text += f"Comment {i+1}: {comment['text']}\n"
    
    try:
        # 2. Send the massive text block to Gemini
        response = thread_chain.invoke({"thread_text": conversation_text})
        
        # 3. Clean the JSON formatting
        clean_text = response.content.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        # 4. Parse and return the master verdict
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"Error analyzing thread: {e}")
        return {
            "thread_verdict": "Error", 
            "overall_reasoning": "Failed to analyze thread due to API error.", 
            "flagged_comments": []
        }