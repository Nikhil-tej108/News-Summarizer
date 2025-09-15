from flask import Flask, render_template, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import time

load_dotenv()

app = Flask(__name__)

# ---------- Load API keys ----------
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Debug: Check if API keys are loaded
print(f"🔍 Groq API Key present: {bool(GROQ_API_KEY)}")
print(f"🔍 NewsData API Key present: {bool(NEWSDATA_API_KEY)}")

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY environment variable is not set!")
if not NEWSDATA_API_KEY:
    print("❌ ERROR: NEWSDATA_API_KEY environment variable is not set!")

# ---------- Enhanced Helper function ----------
def groq_chat(messages, model="llama-3.1-70b-versatile", temperature=0.3, max_tokens=2048):
    """Generic Groq API call with enhanced error handling"""
    if not GROQ_API_KEY:
        print("❌ Groq API key is missing!")
        return None
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        print(f"🔍 Making Groq API call to: {url}")
        print(f"🔍 Using model: {model}")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Authentication failed - check your API key")
            return None
        elif response.status_code == 429:
            print("❌ Rate limit exceeded - try again later")
            return None
        elif response.status_code >= 400:
            print(f"❌ API error: {response.status_code}, Response: {response.text}")
            return None
            
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"].strip()
                print(f"🔍 Generated content length: {len(content)} characters")
                return content
        
        print("❌ No valid content found in response")
        return None
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet connection")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# ---------- Enhanced Web Scraping Function ----------
def fetch_full_article(url):
    """Fetch and extract main content from a news article URL with improved extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"🌐 Fetching full article from: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        if len(response.content) < 1000:
            print("⚠️ Response too small, might be blocked")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for selector in ['script', 'style', 'nav', 'footer', 'aside', 'header', 
                        '.advertisement', '.ad', '.popup', '.modal', '.newsletter',
                        '.social-share', '.comments', '.related-articles']:
            for element in soup.select(selector):
                element.decompose()
        
        # Try multiple content extraction strategies
        content_selectors = [
            'article', 'main', '[role="main"]', 
            '.article-content', '.story-content', '.post-content',
            '.entry-content', '.content__article-body', '.article__body',
            '.article-text', '.post-body', '.story-body',
            '[class*="content"]', '[class*="article"]', '[class*="story"]',
            '#article', '#content', '#main-content'
        ]
        
        content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0]
                print(f"✅ Found content using selector: {selector}")
                break
        
        # Fallback: Look for the largest text container
        if not content:
            print("⚠️ No specific content container found, trying largest text block")
            paragraphs = soup.find_all('p')
            if paragraphs and len(paragraphs) > 3:
                # Group paragraphs by their common parent
                parent_paragraphs = {}
                for p in paragraphs:
                    parent = p.find_parent()
                    if parent:
                        if parent not in parent_paragraphs:
                            parent_paragraphs[parent] = []
                        parent_paragraphs[parent].append(p)
                
                # Find the parent with the most paragraphs
                if parent_paragraphs:
                    best_parent = max(parent_paragraphs.items(), key=lambda x: len(x[1]))[0]
                    content = best_parent
                    print("✅ Found content using paragraph grouping")
        
        # Extract and clean text
        if content:
            # Extract all text elements
            texts = []
            for element in content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = element.get_text().strip()
                if (len(text) > 30 and 
                    not any(prefix in text.lower() for prefix in 
                           ['advertisement', 'related:', 'read more:', 'share this:',
                            'subscribe', 'newsletter', 'comment', 'sponsored'])):
                    texts.append(text)
            
            if not texts:
                # Fallback to all text
                text = content.get_text()
            else:
                text = '\n'.join(texts)
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'ADVERTISEMENT.*?\.\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(?:please|subscribe|share|comment|like)\b.*?\.', '', text, flags=re.IGNORECASE)
            text = text.strip()
            
            print(f"📄 Extracted {len(text)} characters from article")
            
            if len(text) > 200:
                return text
            else:
                print("⚠️ Extracted text too short")
                return None
        else:
            print("❌ Could not extract article content")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching article: {e}")
        return None

# ---------- Enhanced Sentiment Analysis Function ----------
def analyze_sentiment(text):
    """Analyze sentiment of text using Groq API with better prompting"""
    if not text.strip():
        return "neutral", 0.5
    
    truncated_text = text[:4000]
    
    messages = [
        {"role": "system", "content": "You are a sentiment analysis expert. Analyze the sentiment of the provided news text and respond with ONLY a JSON object containing two keys: 'sentiment' (which should be 'positive', 'negative', or 'neutral') and 'confidence' (a float between 0 and 1 representing your confidence in the sentiment analysis). Be precise and factual in your analysis."},
        {"role": "user", "content": f"Analyze the sentiment of this news text. Consider the overall tone, context, and implications:\n\n{truncated_text}"}
    ]
    
    print(f"🔍 Analyzing sentiment of text with length: {len(text)} characters")
    result = groq_chat(messages, model="llama-3.1-70b-versatile", temperature=0.1)
    
    if not result:
        return "neutral", 0.5
    
    try:
        # Extract JSON from response if there's additional text
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group(0)
            
        sentiment_data = json.loads(result)
        sentiment = sentiment_data.get("sentiment", "neutral").lower()
        confidence = float(sentiment_data.get("confidence", 0.5))
        
        # Validate sentiment
        if sentiment not in ["positive", "negative", "neutral"]:
            sentiment = "neutral"
            
        return sentiment, confidence
    except json.JSONDecodeError:
        print(f"❌ Failed to parse sentiment JSON: {result}")
        # Fallback: simple keyword analysis
        text_lower = result.lower()
        if any(word in text_lower for word in ["positive", "optimistic", "favorable", "good", "great", "excellent", "bullish"]):
            return "positive", 0.7
        elif any(word in text_lower for word in ["negative", "pessimistic", "unfavorable", "bad", "poor", "terrible", "bearish"]):
            return "negative", 0.7
        else:
            return "neutral", 0.5
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return "neutral", 0.5

# ---------- Enhanced Summarization ----------
def summarize_text(text, title=""):
    """Generate comprehensive summary using Groq API with improved prompting"""
    if not text.strip():
        return "No text to summarize"
    
    truncated_text = text[:8000]  # Increased character limit for better context
    
    # Enhanced prompt for more detailed summaries
    system_prompt = """You are a professional news analyst. Provide comprehensive, detailed summaries that capture:
1. The main story and key events
2. Important context and background information
3. Key facts, figures, and data points
4. Significant quotes from important figures
5. Implications and potential consequences
6. Future outlook or next steps

Aim for 5-7 detailed sentences that provide substantial information. Be factual, objective, and thorough."""

    user_prompt = f"Please provide a detailed, comprehensive summary of the following news article{' titled: ' + title if title else ''}:\n\n{truncated_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print(f"🔍 Summarizing text of length: {len(text)} characters")
    summary = groq_chat(messages, model="llama-3.1-70b-versatile", temperature=0.2, max_tokens=1024)
    
    if not summary:
        # Fallback: create a basic summary from the text
        sentences = re.split(r'(?<=[.!?])\s+', text)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20 and not any(word in s.lower() for word in ['subscribe', 'share', 'comment'])]
        
        if meaningful_sentences:
            fallback = ' '.join(meaningful_sentences[:5])
            return f"⚠️ AI summary unavailable. Key information from the article: {fallback}"
        else:
            return "⚠️ Could not generate summary. The article content may be inaccessible or formatted unusually."
    
    return summary

# ---------- Test Endpoint ----------
@app.route("/test_groq")
def test_groq():
    """Test endpoint to verify Groq API connection"""
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, can you respond with 'API is working'? Please respond with only those words."}
    ]
    
    print("🧪 Testing Groq API connection...")
    result = groq_chat(test_messages, model="llama-3.1-70b-versatile")
    
    if result:
        return jsonify({
            "status": "success", 
            "response": result,
            "message": "Groq API is working correctly!"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Groq API test failed. Check your API key and internet connection."
        })

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_news", methods=["GET"])
def get_news():
    """Fetch news from NewsData API"""
    if not NEWSDATA_API_KEY:
        return jsonify({"error": "NewsData API key not configured"}), 500
    
    try:
        # Try multiple categories to get diverse news
        categories = ["technology", "business", "politics", "health", "science"]
        all_articles = []
        
        for category in categories[:2]:  # Limit to 2 categories to avoid rate limiting
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country=in&language=en&category={category}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            articles = data.get("results", [])
            
            print(f"📰 Found {len(articles)} articles in {category} category")
            
            for a in articles:
                # Avoid duplicates
                if not any(art.get("url") == a.get("link") for art in all_articles):
                    all_articles.append({
                        "title": a.get("title", "No Title"),
                        "description": a.get("description") or a.get("content") or "No description available",
                        "url": a.get("link"),
                        "image": a.get("image_url"),
                        "source": a.get("source_id", "Unknown"),
                        "category": category,
                        "full_content": None
                    })

        print(f"📰 Total articles found: {len(all_articles)}")

        # If no articles found, try a general query
        if not all_articles:
            print("⚠️ No articles from category queries, trying fallback...")
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=india&language=en"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            articles = data.get("results", [])
            
            for a in articles[:10]:
                all_articles.append({
                    "title": a.get("title", "No Title"),
                    "description": a.get("description") or a.get("content") or "No description available",
                    "url": a.get("link"),
                    "image": a.get("image_url"),
                    "source": a.get("source_id", "Unknown"),
                    "category": "general",
                    "full_content": None
                })
            
            print(f"📰 Found {len(articles)} articles from fallback query")

        # Return top 12 articles
        simplified = all_articles[:12]
        print(f"✅ Returning {len(simplified)} articles")
        return jsonify(simplified)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ News API error: {e}")
        return jsonify({"error": "Failed to fetch news"}), 500
    except Exception as e:
        print(f"❌ Unexpected error in get_news: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/summarize", methods=["POST"])
def summarize():
    """Summarize text and analyze sentiment with enhanced functionality"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        article_url = data.get("url", "")
        preview_text = data.get("text", "")
        title = data.get("title", "")
        
        print(f"📝 Received request for URL: {article_url}")
        print(f"📝 Preview text length: {len(preview_text)} characters")
        print(f"📝 Article title: {title}")

        if not article_url:
            return jsonify({"error": "No article URL provided"}), 400

        if not GROQ_API_KEY:
            error_msg = "Groq API key is not configured. Please check your environment variables."
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 500

        full_article_text = fetch_full_article(article_url)
        
        text_to_summarize = full_article_text if full_article_text else preview_text
        
        if not text_to_summarize or not text_to_summarize.strip():
            error_msg = "No text content available to summarize"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), 400

        summary_prefix = ""
        if not full_article_text:
            summary_prefix = "⚠️ Note: Full article content was unavailable. This summary is based on the preview text only.\n\n"
        
        summary = summarize_text(text_to_summarize, title)
        
        if not summary or "⚠️ AI summary unavailable" in summary:
            print("⚠️ AI summarization failed, using enhanced fallback summary")
            # Create a more detailed fallback summary
            sentences = re.split(r'(?<=[.!?])\s+', text_to_summarize)
            meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 30 and 
                                  not any(word in s.lower() for word in ['subscribe', 'share', 'comment', 'read more'])]
            
            if meaningful_sentences and len(meaningful_sentences) >= 3:
                fallback_summary = ' '.join(meaningful_sentences[:5])
                summary = f"Key points from the article: {fallback_summary}"
            else:
                summary = "Comprehensive summary unavailable. The article content may be inaccessible or formatted unusually. Please try another article."

        sentiment, score = analyze_sentiment(text_to_summarize)

        print(f"✅ Summary generated: {len(summary)} characters")
        print(f"✅ Sentiment: {sentiment} (Confidence: {score})")

        return jsonify({
            "summary": summary_prefix + summary, 
            "sentiment": sentiment, 
            "confidence": str(score),
            "used_full_article": bool(full_article_text)
        })
        
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        print(f"❌ Error in summarize endpoint: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "groq_api_configured": bool(GROQ_API_KEY),
        "newsdata_api_configured": bool(NEWSDATA_API_KEY)
    })

if __name__ == "__main__":
    print("Visit http://localhost:5000 to access the application")
    print(" Test Groq API at http://localhost:5000/test_groq")
    print(" Health check at http://localhost:5000/health")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)