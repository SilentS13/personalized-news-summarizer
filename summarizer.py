import re
import logging
import os
import json
from collections import Counter
from openai import OpenAI

# Initialize OpenAI client with API key
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def clean_text(text):
    """Clean and preprocess the text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    return text

def extract_article_from_url(url):
    """Extract article content from a URL using trafilatura."""
    try:
        # Using trafilatura to extract content from URL
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return None, "Failed to download content from URL"
        
        # Extract main text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            return None, "No content extracted from URL"
        
        # Get a title from the URL (remove protocol and domain)
        import re
        title = url
        # Remove protocol
        title = re.sub(r'^https?://', '', title)
        # Remove domain
        title = re.sub(r'^[^/]+/', '', title)
        # Replace dashes with spaces and capitalize
        title = ' '.join(word.capitalize() for word in title.replace('-', ' ').split())
        
        return {
            'title': title[:100],  # Limit title length
            'text': text,
            'url': url
        }, None
    except Exception as e:
        logging.error(f"Error extracting article: {str(e)}")
        return None, f"Error processing URL: {str(e)}"

def extract_key_topics_with_ai(text, n=5):
    """Extract key topics using OpenAI."""
    try:
        # Truncate text if too long
        max_text_length = 5000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        prompt = f"""
        Extract exactly {n} key topics or concepts from the following text. 
        Return them as a JSON array of strings.
        Each topic should be a single word or short phrase (1-3 words max).
        
        TEXT:
        {text}
        
        KEY TOPICS (JSON array of strings):
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        # Extract and parse JSON from response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure the result contains a key_topics field and is a list
        if isinstance(result, dict) and "topics" in result:
            return result["topics"]
        elif isinstance(result, list):
            return result
        else:
            # Try to find any array in the result
            for key, value in result.items():
                if isinstance(value, list):
                    return value
            
            # Fallback to basic extraction if AI returned unexpected format
            return extract_key_topics_basic(text, n)
    except Exception as e:
        logging.error(f"AI key topics extraction failed: {str(e)}")
        # Fallback to basic extraction on error
        return extract_key_topics_basic(text, n)

def extract_key_topics_basic(text, n=5):
    """Extract key topics using basic word frequency (fallback method)."""
    words = text.lower().split()
    # Filter short words and common stopwords
    filtered_words = [word for word in words if len(word) > 4 and word not in (
        'about', 'after', 'again', 'their', 'there', 'these', 'thing', 
        'think', 'those', 'would', 'which', 'with', 'have', 'this', 'that'
    )]
    
    # Count occurrences
    counter = Counter(filtered_words)
    # Get the most common words
    most_common = counter.most_common(n)
    return [word for word, count in most_common] if most_common else ["Topic"]

def generate_ai_summary(text, length="medium", reading_level="medium", interests=None):
    """Generate a summary using OpenAI."""
    try:
        # Determine desired summary length
        if length == "brief":
            word_count = "100-150"
        elif length == "detailed":
            word_count = "300-400"
        else:  # medium
            word_count = "200-250"
        
        # Determine desired reading level
        if reading_level == "basic":
            level_desc = "simple language, short sentences, easy to understand by elementary school students"
        elif reading_level == "advanced":
            level_desc = "sophisticated language, specialized terminology, suitable for experts in the field"
        else:  # medium
            level_desc = "balanced language complexity, suitable for general adult audience"
        
        # Construct interest focus if provided
        interest_focus = ""
        if interests and isinstance(interests, list) and len(interests) > 0:
            interest_focus = f"Focus on aspects related to: {', '.join(interests)}. "
        
        # Prepare prompt for OpenAI
        prompt = f"""
        Please create a concise summary of the following text in {word_count} words.
        Use {level_desc}.
        {interest_focus}
        Maintain factual accuracy and include the most important information.
        
        TEXT TO SUMMARIZE:
        {text}
        """
        
        # Limit prompt size for token constraints
        max_prompt_length = 11000
        if len(prompt) > max_prompt_length:
            truncated_text = text[:max_prompt_length - 1000] + "..."
            prompt = prompt.replace(text, truncated_text)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        # Extract summary text
        summary_text = response.choices[0].message.content.strip()
        
        # Highlight interests in the summary if provided
        if interests:
            for interest in interests:
                # Create pattern that matches whole words only
                pattern = r'\b' + re.escape(interest) + r'\b'
                # Replace with highlighted version using a span with a class
                summary_text = re.sub(
                    pattern, 
                    f'<span class="interest-highlight">{interest}</span>', 
                    summary_text, 
                    flags=re.IGNORECASE
                )
        
        return summary_text
    except Exception as e:
        logging.error(f"AI summary generation failed: {str(e)}")
        # Fallback to basic summary on error
        return generate_basic_summary(text, length, reading_level, interests)

def generate_basic_summary(text, length="medium", reading_level="medium", interests=None):
    """Generate a basic summary without AI (fallback method)."""
    # Clean the text
    text = clean_text(text)
    
    # Create a simple summary based on the first few sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if length == "brief":
        num_sentences = min(3, len(sentences))
    elif length == "detailed":
        num_sentences = min(8, len(sentences))
    else:  # medium
        num_sentences = min(5, len(sentences))
    
    summary_text = " ".join(sentences[:num_sentences])
    
    # Adjust for reading level
    if reading_level == "basic":
        # For basic level, try to use simpler words and shorter sentences
        summary_text = re.sub(r'(\.|;)\s+', '. ', summary_text)  # Convert semicolons to periods
        summary_text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\2', summary_text)  # Add newlines after periods
    
    # If user interests are provided, highlight relevant sections
    if interests:
        for interest in interests:
            # Simple highlighting: add emphasis to sentences containing the interest
            pattern = r'\b' + re.escape(interest) + r'\b'
            summary_text = re.sub(
                pattern, 
                f'<span class="interest-highlight">{interest}</span>', 
                summary_text, 
                flags=re.IGNORECASE
            )
    
    return summary_text

def generate_summary(text, length="medium", reading_level="medium", interests=None):
    """Generate a summary of the text based on user preferences."""
    # Clean the text
    text = clean_text(text)
    
    # Try to generate summary with AI
    try:
        # Extract key topics with AI
        key_topics = extract_key_topics_with_ai(text)
        
        # Generate summary using OpenAI
        summary_text = generate_ai_summary(text, length, reading_level, interests)
        
        return {
            'summary': summary_text,
            'key_topics': key_topics
        }
    except Exception as e:
        logging.error(f"Error in AI summary generation: {str(e)}")
        
        # Fallback to basic summary method
        summary_text = generate_basic_summary(text, length, reading_level, interests)
        key_topics = extract_key_topics_basic(text)
        
        return {
            'summary': summary_text,
            'key_topics': key_topics
        }