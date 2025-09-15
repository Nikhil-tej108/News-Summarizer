📰 AI-Powered News Summarizer :
    
   A sophisticated Flask web application that provides comprehensive summaries of news articles using advanced AI capabilities. The app fetches current news, extracts full article content, generates intelligent summaries, and performs sentiment analysis.

## ✨ Features
 
  - 📊 Real-time News Aggregation: Fetches latest news from multiple categories

  - 🤖 AI-Powered Summarization: Uses Groq's LLaMA model for intelligent article summarization

  - 🎯 Sentiment Analysis: Determines article sentiment (positive/negative/neutral) with confidence scoring

  - 🌐 Smart Content Extraction: Advanced web scraping to extract full article content

  - 📱 Responsive Design: Clean, modern UI built with Tailwind CSS

  - ⚡ Fast Performance: Optimized backend with efficient API calls and caching
  

🚀 Live Demo
  The application is deployed on Render: https://latest-news-summarizer.onrender.com
  

## 🛠️ Technology Stack
  Backend: Python, Flask

  Frontend: HTML, Tailwind CSS, JavaScript

  AI Services: Groq API (LLaMA 3.1 70B model)

  News API: NewsData.io

  Web Scraping: BeautifulSoup4

  Deployment: Render
  

## 📦 Installation
  ``` bash
  # Clone the repository
    git clone https://github.com/Nikhil-tej108/News-Summarizer.git
    cd News-Summarizer

  #Create a virtual environment  
     python -m venv venv
     source venv/bin/activate 
    # On Windows: venv\Scripts\activate

  #Install dependencies
    pip install -r requirements.txt

  #Set up environment variables
    cp .env.example .env
    Edit .env and add your API keys:

  text
  NEWSDATA_API_KEY=your_newsdata_api_key_here
  GROQ_API_KEY=your_groq_api_key_here

  #Run the application
  python app.py
  Visit http://localhost:5000 in your browser
```
  

🔑 API Keys Required
  This application requires the following API keys:

  NewsData.io API Key: https://newsdata.io/

  Groq API Key: https://groq.com/
  
  
  ## 📁 Project Structure

```
News-Summarizer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── render.yaml           # Render deployment configuration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
└── templates/
    └── index.html       # Main frontend template
```
<br>
    
🎯 How It Works
  - News Fetching: The app retrieves current news articles from NewsData.io API across multiple categories

 - Content Extraction: When a user selects an article, the system scrapes the full content from the source website

 - AI Processing: The content is sent to Groq's LLaMA model for summarization and sentiment analysis

 -  Results Display: The generated summary and sentiment analysis are displayed in a clean, user-friendly interface
<br>
🌟 Key Functions

   - Smart Content Extraction
    The application uses advanced scraping techniques with multiple fallback strategies to extract article content from various news websites.

  - Intelligent Summarization
    Leveraging the powerful LLaMA 3.1 70B model, the app creates comprehensive summaries that capture:

   - Main story and key events

   - Important context and background

   - Key facts and figures

   - Significant quotes

   - Implications and consequences

   - Sentiment Analysis
   Each article is analyzed for emotional tone with confidence scoring, categorized as:

    ✅ Positive (green)

    ❌ Negative (red)

    🔷 Neutral (gray)


 ## 🚀 Deployment

  Deploy to Render
  Fork this repository

  Create an account on Render

  Connect your GitHub account

  Create a new Web Service and connect your repository

  Add environment variables in the Render dashboard:

  - NEWSDATA_API_KEY

   - GROQ_API_KEY

  Deploy!

  ## Manual Deployment
  ``` #bash
   # Install gunicorn for production
   pip install gunicorn

  # Run with gunicorn
  gunicorn app:app -b 0.0.0.0:$PORT
```

  
 ## 🤝 Contributing

   Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

   Fork the project

   Create your feature branch (git checkout -b feature/AmazingFeature)

   Commit your changes (git commit -m 'Add some AmazingFeature')

   Push to the branch (git push origin feature/AmazingFeature)

   Open a Pull Request
  

## 📝 License
  This project is licensed under the MIT License - see the LICENSE file for details.
  

## 🙏 Acknowledgments
 
  Groq for providing powerful AI inference capabilities

  NewsData.io for news API services

  Render for deployment platform

  Tailwind CSS for styling framework


## ⭐ Star this repo if you found it helpful!
