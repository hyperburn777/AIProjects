# AP News Scraper & Sentiment Analyzer

A comprehensive Python application that scrapes top news stories from [AP News](https://apnews.com/) and performs advanced sentiment analysis on the content.

## Features

### News Scraping (`scraper.py`)
- Scrapes top stories from the AP News homepage
- Extracts headlines, summaries, links, timestamps, and categories
- Fetches full article text for comprehensive analysis
- Saves results to JSON files with timestamps
- Beautiful formatted console output
- Robust error handling and fallback mechanisms
- Duplicate detection to avoid repeated stories
- Respects website structure and implements polite scraping practices

### Sentiment Analysis (`analyzer.py`)
- **Multi-method sentiment analysis**: Uses both VADER and TextBlob for comprehensive sentiment scoring
- **Entity extraction**: Dynamically identifies organizations, industries, and locations mentioned in articles
- **Industry-specific analysis**: Categorizes content by industry (healthcare, technology, finance, media, etc.)
- **Keyword analysis**: Extracts positive and negative keywords that influence sentiment
- **Phrase-level analysis**: Identifies sentiment-bearing phrases within articles
- **Contextual reasoning**: Provides detailed explanations for sentiment classifications

### Data Storage
- **JSON format**: Structured data with timestamps and metadata
- **Individual text files**: Each story saved as a separate text file for detailed analysis
- **Sentiment reports**: Comprehensive analysis results saved to `top_stories_sentiment.txt`

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 lxml textblob vaderSentiment nltk
```

## Usage

### 1. Scraping News Stories

#### Basic Usage
```bash
python scraper.py
```

This will:
- Scrape up to 5 top stories from AP News
- Display them in a formatted way in the console
- Save the results to a JSON file with timestamp
- Create individual text files for each story

#### Programmatic Usage
```python
from scraper import APNewsScraper

# Create scraper instance
scraper = APNewsScraper()

# Scrape top stories
stories = scraper.scrape_top_stories(max_stories=10)

# Print stories
scraper.print_stories(stories)

# Save to JSON
scraper.save_to_json(stories, "my_stories.json")

# Scrape specific section
section_stories = scraper.scrape_section("/politics", max_stories=5)
```

### 2. Sentiment Analysis

#### Basic Usage
```bash
python analyzer.py
```

This will:
- Analyze all stories in the `top_stories/` directory
- Perform comprehensive sentiment analysis
- Generate detailed reports with entity and industry analysis
- Save results to `top_stories_sentiment.txt`

#### Programmatic Usage
```python
from analyzer import analyze_sentiment, extract_dynamic_entities

# Analyze a single text
text = "Your news article text here..."
sentiment_result = analyze_sentiment(text)

# Extract entities and industries
entities = extract_dynamic_entities(text)
```

## Output Examples

### Scraper Output
```
================================================================================
TOP STORIES FROM AP NEWS
Scraped at: 2024-01-15 14:30:25
Total stories: 5
================================================================================

 1. Biden administration announces new climate initiatives
    Category: Politics
    Time: 2 hours ago
    Summary: The White House unveiled a comprehensive plan to address climate change...
    Link: https://apnews.com/article/climate-biden-administration...

 2. Major tech companies report quarterly earnings
    Category: Business
    Time: 4 hours ago
    Summary: Several technology giants exceeded analyst expectations...
    Link: https://apnews.com/article/tech-earnings-quarterly...
```

### Sentiment Analysis Output
```
SENTIMENT ANALYSIS RESULTS
==================================================

01_Charges dropped against Utah doctor accused of throwing away $28,000 in COVID vaccine doses.txt: negative
Reasoning: VADER negative (-0.475), TextBlob polarity: 0.167
Positive phrases: covid-19 vaccines saved millions, courage and his commitment
Negative phrases: being charged with conspiracy, vaccine doses were destroyed
Positive keywords: charitable, commitment, courage, justice, saved
Negative keywords: accused, charged, conspiracy, destroyed, prison

Industry/Entity Analysis:
  Healthcare (Industry): positive sentiment
    Indicators: patient, health
    Entity mentioned 2 times with positive sentiment (score: 0.314)
  Government (Industry): positive sentiment
    Indicators: department, federal
    Entity mentioned 4 times with positive sentiment (score: 0.116)
```

## File Structure

```
6-News/
├── scraper.py                    # Main scraping functionality
├── analyzer.py                   # Sentiment analysis engine
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── top_stories_sentiment.txt     # Sentiment analysis results
└── top_stories/                  # Individual story files
    ├── 01_Story_Title.txt
    ├── 02_Story_Title.txt
    ├── ...
    └── ap_news_stories_YYYYMMDD_HHMMSS.json
```

## Advanced Features

### Entity Recognition
The analyzer automatically identifies:
- **Organizations**: Companies, government agencies, institutions
- **Industries**: Healthcare, technology, finance, media, education, etc.
- **Locations**: Cities, countries, regions mentioned in context

### Sentiment Classification
- **Positive**: Score > 0.1 (optimistic, favorable content)
- **Neutral**: Score between -0.1 and 0.1 (balanced, factual content)
- **Negative**: Score < -0.1 (critical, concerning content)

### Industry Analysis
The system categorizes content into industries based on:
- Keyword presence (e.g., "hospital", "medical" for healthcare)
- Contextual analysis
- Frequency of industry-related terms

## Error Handling

The application includes robust error handling for:
- Network connectivity issues
- Website structure changes
- Missing or malformed content
- Rate limiting (basic)
- NLTK data download failures
- File I/O operations

## Dependencies

- **requests**: HTTP requests for web scraping
- **beautifulsoup4**: HTML parsing and extraction
- **lxml**: XML/HTML parser backend
- **textblob**: Natural language processing and sentiment analysis
- **vaderSentiment**: Valence Aware Dictionary and sEntiment Reasoner
- **nltk**: Natural Language Toolkit for text processing

## Legal Notice

This application is for educational and personal use only. Please respect AP News's terms of service and robots.txt file. Consider implementing appropriate delays between requests for production use.

## Contributing

Feel free to submit issues and enhancement requests. When contributing, please:
1. Test your changes thoroughly
2. Update documentation as needed
3. Follow existing code style
4. Add appropriate error handling 