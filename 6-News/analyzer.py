import os
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter

# Directory containing the top stories
TOP_STORIES_DIR = os.path.join(os.path.dirname(__file__), "top_stories")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "top_stories_sentiment.txt")

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def extract_article_text(filepath):
    """Extract the main article text from the story file."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find the start of the full article text
    start = None
    for i, line in enumerate(lines):
        if "FULL ARTICLE TEXT" in line.strip():
            start = i + 1
            break
    
    if start is None:
        return ""
    
    # Skip separator lines and copyright notices to find actual content
    content_start = start
    for i in range(start, len(lines)):
        line = lines[i].strip()
        # Skip empty lines, separators, and copyright notices
        if (line == "" or 
            line.startswith("=") or 
            "Copyright" in line or 
            "(AP Photo/" in line):
            continue
        else:
            content_start = i
            break
    
    # Collect until next separator or end
    article_lines = []
    for i, line in enumerate(lines[content_start:], content_start):
        if line.strip().startswith("=") or line.strip().startswith("End of Story"):
            break
        article_lines.append(line.strip())
    
    # Join and clean the text
    text = " ".join(article_lines)
    
    # Remove any remaining copyright notices and metadata
    text = re.sub(r'Copyright \d{4} The Associated Press\. All Rights Reserved\.', '', text)
    text = re.sub(r'\(AP Photo/[^)]+\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_dynamic_entities(text):
    """Dynamically extract industries and entities without predefined lists."""
    text_lower = text.lower()
    sentences = sent_tokenize(text)
    
    # Filter out AP News and common news agency mentions
    ap_patterns = [
        r'\bap\b', r'\bassociated press\b', r'\bnews agency\b', r'\breuters\b', 
        r'\bbloomberg\b', r'\bcnn\b', r'\bbbc\b', r'\bnew york times\b'
    ]
    
    # Remove AP News mentions from analysis
    for pattern in ap_patterns:
        text_lower = re.sub(pattern, '', text_lower)
    
    # Extract potential entities using multiple strategies
    entities = {}
    
    # Strategy 1: Find capitalized multi-word phrases (likely organizations/entities)
    for sentence in sentences:
        words = word_tokenize(sentence)
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Look for multi-word entities
                entity_parts = [word]
                j = i + 1
                while j < len(words) and words[j][0].isupper() and len(words[j]) > 2:
                    entity_parts.append(words[j])
                    j += 1
                if len(entity_parts) > 1:
                    entity = ' '.join(entity_parts)
                    if entity not in entities:
                        entities[entity] = {'type': 'organization', 'mentions': 0, 'sentences': []}
                    entities[entity]['mentions'] += 1
                    entities[entity]['sentences'].append(sentence)
    
    # Strategy 2: Find industry-related terms using context clues
    industry_keywords = {
        'healthcare': ['hospital', 'medical', 'doctor', 'patient', 'treatment', 'health', 'medicine'],
        'technology': ['software', 'digital', 'online', 'app', 'platform', 'tech', 'computer'],
        'finance': ['bank', 'financial', 'investment', 'stock', 'market', 'economy', 'business'],
        'media': ['news', 'media', 'press', 'journalist', 'reporter', 'broadcast', 'entertainment'],
        'education': ['school', 'university', 'college', 'education', 'student', 'teacher'],
        'transportation': ['airline', 'transport', 'vehicle', 'car', 'truck', 'shipping'],
        'energy': ['oil', 'gas', 'energy', 'electric', 'power', 'renewable'],
        'retail': ['store', 'shop', 'retail', 'consumer', 'product', 'brand'],
        'agriculture': ['farm', 'agriculture', 'crop', 'food', 'farmer', 'rural'],
        'defense': ['military', 'defense', 'weapon', 'security', 'army', 'navy'],
        'government': ['department', 'agency', 'administration', 'federal', 'state', 'local']
    }
    
    # Find sentences containing industry keywords and analyze context
    for industry, keywords in industry_keywords.items():
        industry_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                # Check if this is actually about the industry (not just a mention)
                if len(sentence.split()) > 5:  # Avoid very short sentences
                    industry_sentences.append(sentence)
        
        if len(industry_sentences) >= 2:  # Only include if mentioned multiple times
            entities[industry.title()] = {
                'type': 'industry',
                'mentions': len(industry_sentences),
                'sentences': industry_sentences,
                'keywords': [k for k in keywords if any(k in s.lower() for s in industry_sentences)]
            }
    
    # Strategy 3: Find location-based entities (cities, countries, regions)
    location_patterns = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Two-word capitalized phrases
        r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b'  # Three-word capitalized phrases
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if match not in entities and len(match.split()) >= 2:
                # Count mentions in sentences
                mention_count = sum(1 for sentence in sentences if match.lower() in sentence.lower())
                if mention_count >= 2:  # Only include if mentioned multiple times
                    entities[match.title()] = {
                        'type': 'location',
                        'mentions': mention_count,
                        'sentences': [s for s in sentences if match.lower() in s.lower()]
                    }
    
    return entities

def analyze_entity_sentiment(entity_name, entity_data):
    """Analyze sentiment for a specific entity."""
    if entity_data['mentions'] < 2:  # Skip entities with too few mentions
        return None
    
    sentences = entity_data['sentences']
    sentiment_scores = []
    
    for sentence in sentences:
        scores = vader_analyzer.polarity_scores(sentence)
        sentiment_scores.append(scores['compound'])
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    if avg_sentiment > 0.1:
        sentiment_category = "positive"
    elif avg_sentiment < -0.1:
        sentiment_category = "negative"
    else:
        sentiment_category = "neutral"
    
    result = {
        'name': entity_name,
        'type': entity_data['type'],
        'sentiment_score': avg_sentiment,
        'sentiment_category': sentiment_category,
        'mentions': entity_data['mentions'],
        'reasoning': f"Entity mentioned {entity_data['mentions']} times with {sentiment_category} sentiment (score: {avg_sentiment:.3f})"
    }
    
    if 'keywords' in entity_data:
        result['indicators'] = entity_data['keywords']
    
    return result

def analyze_dynamic_industry_sentiment(text):
    """Analyze sentiment around dynamically detected industries and entities."""
    entities = extract_dynamic_entities(text)
    analysis_results = []
    
    for entity_name, entity_data in entities.items():
        analysis = analyze_entity_sentiment(entity_name, entity_data)
        if analysis:
            analysis_results.append(analysis)
    
    # Sort by sentiment strength (most extreme first) and then by mention count
    analysis_results.sort(key=lambda x: (abs(x['sentiment_score']), x['mentions']), reverse=True)
    
    return analysis_results[:6]  # Return top 6 most significant entities

def extract_sentiment_phrases(text, positive_keywords=None, negative_keywords=None):
    """Automatically extract sentiment phrases using NLTK and VADER with keyword-based filtering."""
    text_lower = text.lower()
    
    # Tokenize into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text_lower)
    
    # Get stop words to filter out common words
    stop_words = set(stopwords.words('english'))
    
    # Use provided keywords or extract them automatically
    if positive_keywords is None or negative_keywords is None:
        positive_keywords, negative_keywords = extract_sentiment_keywords(text)
    
    # Convert keywords to sets for faster lookup
    positive_sentiment_words = set(positive_keywords)
    negative_sentiment_words = set(negative_keywords)
    
    # Generate n-grams (2-4 word phrases)
    positive_phrases = []
    negative_phrases = []
    
    # Analyze each sentence for sentiment
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Get VADER sentiment for the sentence
        vader_scores = vader_analyzer.polarity_scores(sentence)
        
        # Generate n-grams for this sentence
        sentence_words = word_tokenize(sentence_lower)
        
        # Create 2-4 word phrases
        for n in range(2, 5):
            ngram_list = list(ngrams(sentence_words, n))
            for ngram in ngram_list:
                phrase = ' '.join(ngram)
                
                # Filter out phrases with too many stop words
                stop_word_count = sum(1 for word in ngram if word in stop_words)
                if stop_word_count > len(ngram) * 0.6:  # Stricter: >60% are stop words
                    continue
                
                # Check if phrase contains sentiment words
                phrase_words = set(phrase.split())
                has_positive_words = bool(phrase_words & positive_sentiment_words)
                has_negative_words = bool(phrase_words & negative_sentiment_words)
                
                # Get sentiment for this specific phrase
                phrase_scores = vader_analyzer.polarity_scores(phrase)
                
                # More stringent criteria for phrase selection
                if phrase_scores['compound'] > 0.4 and has_positive_words:  # Higher threshold + sentiment words
                    # Additional filtering for positive phrases
                    if len(phrase.split()) >= 2 and not any(word in phrase for word in ['reported', 'said', 'according', 'stated', 'noted']):
                        positive_phrases.append(phrase)
                elif phrase_scores['compound'] < -0.4 and has_negative_words:  # Higher threshold + sentiment words
                    # Additional filtering for negative phrases
                    if len(phrase.split()) >= 2 and not any(word in phrase for word in ['reported', 'said', 'according', 'stated', 'noted']):
                        negative_phrases.append(phrase)
    
    # Remove duplicates and sort by length (longer phrases first)
    positive_phrases = sorted(list(set(positive_phrases)), key=len, reverse=True)
    negative_phrases = sorted(list(set(negative_phrases)), key=len, reverse=True)
    
    # Limit to top 10 most relevant phrases for readability
    positive_phrases = positive_phrases[:10]
    negative_phrases = negative_phrases[:10]
    
    return positive_phrases, negative_phrases

def analyze_phrases_and_keywords(text):
    """Analyze text for both individual keywords and contextual phrases using automatic detection."""
    text_lower = text.lower()
    
    # First extract keywords to use for phrase filtering
    positive_keywords, negative_keywords = extract_sentiment_keywords(text)
    
    # Use the keywords to help filter phrases
    positive_phrases, negative_phrases = extract_sentiment_phrases(text, positive_keywords, negative_keywords)
    
    return positive_phrases, negative_phrases, positive_keywords, negative_keywords

def extract_sentiment_keywords(text):
    """Automatically extract sentiment keywords using VADER's lexicon and NLTK."""
    text_lower = text.lower()
    
    # Tokenize the text
    words = word_tokenize(text_lower)
    
    # Get stop words
    stop_words = set(stopwords.words('english'))
    
    # Get VADER's lexicon for automatic sentiment word detection
    vader_lexicon = vader_analyzer.lexicon
    
    # Filter words: remove stop words, punctuation, and short words
    filtered_words = []
    for word in words:
        # Remove punctuation and short words
        word_clean = re.sub(r'[^\w\s]', '', word)
        if (len(word_clean) > 2 and 
            word_clean not in stop_words and 
            word_clean.isalpha()):
            filtered_words.append(word_clean)
    
    # Find sentiment words using VADER's lexicon
    positive_keywords = []
    negative_keywords = []
    
    for word in filtered_words:
        if word in vader_lexicon:
            sentiment_score = vader_lexicon[word]
            if sentiment_score > 0.5:  # Positive threshold
                positive_keywords.append(word)
            elif sentiment_score < -0.5:  # Negative threshold
                negative_keywords.append(word)
    
    # Also check for sentiment words using TextBlob's sentiment analysis
    # This helps catch words that might not be in VADER's lexicon
    for word in filtered_words:
        if word not in positive_keywords and word not in negative_keywords:
            # Analyze single word sentiment
            word_scores = vader_analyzer.polarity_scores(word)
            if word_scores['compound'] > 0.3:
                positive_keywords.append(word)
            elif word_scores['compound'] < -0.3:
                negative_keywords.append(word)
    
    # Remove duplicates and sort
    positive_keywords = sorted(list(set(positive_keywords)))
    negative_keywords = sorted(list(set(negative_keywords)))
    
    # Limit to most relevant keywords (top 15 each)
    positive_keywords = positive_keywords[:15]
    negative_keywords = negative_keywords[:15]
    
    return positive_keywords, negative_keywords

def analyze_sentiment(text):
    """Analyze sentiment using multiple approaches with phrase-based analysis and dynamic industry sentiment."""
    if not text:
        return "unknown", "No text extracted", [], [], [], [], []
    
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # VADER sentiment analysis
    vader_scores = vader_analyzer.polarity_scores(text)
    
    # TextBlob sentiment analysis
    blob = TextBlob(text)
    textblob_polarity = blob.sentiment.polarity
    textblob_subjectivity = blob.sentiment.subjectivity
    
    # Phrase and keyword analysis
    positive_phrases, negative_phrases, positive_keywords, negative_keywords = analyze_phrases_and_keywords(text)
    
    # Dynamic industry/entity sentiment analysis
    industry_analysis = analyze_dynamic_industry_sentiment(text)
    
    # Decision logic with reasoning
    if vader_scores['compound'] > 0.1:
        sentiment = "positive"
        reasoning = f"VADER positive ({vader_scores['compound']:.3f}), TextBlob polarity: {textblob_polarity:.3f}"
    elif vader_scores['compound'] < -0.1:
        sentiment = "negative"
        reasoning = f"VADER negative ({vader_scores['compound']:.3f}), TextBlob polarity: {textblob_polarity:.3f}"
    else:
        sentiment = "neutral"
        reasoning = f"VADER neutral ({vader_scores['compound']:.3f}), TextBlob polarity: {textblob_polarity:.3f}"
    
    return sentiment, reasoning, positive_phrases, negative_phrases, positive_keywords, negative_keywords, industry_analysis

def main():
    results = []
    for filename in sorted(os.listdir(TOP_STORIES_DIR)):
        if filename.endswith(".txt") and filename[0].isdigit():
            filepath = os.path.join(TOP_STORIES_DIR, filename)
            article_text = extract_article_text(filepath)
            
            sentiment, reasoning, positive_phrases, negative_phrases, positive_keywords, negative_keywords, industry_analysis = analyze_sentiment(article_text)
            results.append((filename, sentiment, reasoning, positive_phrases, negative_phrases, positive_keywords, negative_keywords, industry_analysis))
            
            print(f"\n{filename}:")
            print(f"Sentiment: {sentiment}")
            print(f"Reasoning: {reasoning}")
            print(f"Positive phrases: {positive_phrases[:5]}...")  # Show first 5
            print(f"Negative phrases: {negative_phrases[:5]}...")  # Show first 5
            print(f"Positive keywords: {positive_keywords}")
            print(f"Negative keywords: {negative_keywords}")
            
            # Print industry analysis
            if industry_analysis:
                print(f"\nIndustry/Entity Analysis:")
                for entity in industry_analysis:
                    entity_type = entity['type'].title()
                    if entity_type == 'Industry' and 'indicators' in entity:
                        print(f"  {entity['name']} ({entity_type}): {entity['sentiment_category']} sentiment")
                        print(f"    Indicators: {', '.join(entity['indicators'])}")
                    else:
                        print(f"  {entity['name']} ({entity_type}): {entity['sentiment_category']} sentiment")
                    print(f"    {entity['reasoning']}")
    
    # Write results to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("SENTIMENT ANALYSIS RESULTS\n")
        f.write("=" * 50 + "\n\n")
        for filename, sentiment, reasoning, positive_phrases, negative_phrases, positive_keywords, negative_keywords, industry_analysis in results:
            f.write(f"{filename}: {sentiment}\n")
            f.write(f"Reasoning: {reasoning}\n")
            f.write(f"Positive phrases: {', '.join(positive_phrases) if positive_phrases else 'None'}\n")
            f.write(f"Negative phrases: {', '.join(negative_phrases) if negative_phrases else 'None'}\n")
            f.write(f"Positive keywords: {', '.join(positive_keywords) if positive_keywords else 'None'}\n")
            f.write(f"Negative keywords: {', '.join(negative_keywords) if negative_keywords else 'None'}\n")
            
            # Write industry analysis
            if industry_analysis:
                f.write(f"\nIndustry/Entity Analysis:\n")
                for entity in industry_analysis:
                    entity_type = entity['type'].title()
                    if entity_type == 'Industry' and 'indicators' in entity:
                        f.write(f"  {entity['name']} ({entity_type}): {entity['sentiment_category']} sentiment\n")
                        f.write(f"    Indicators: {', '.join(entity['indicators'])}\n")
                    else:
                        f.write(f"  {entity['name']} ({entity_type}): {entity['sentiment_category']} sentiment\n")
                    f.write(f"    {entity['reasoning']}\n")
            f.write("\n")
    
    print(f"\nSentiment analysis complete. Results written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
