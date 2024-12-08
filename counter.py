import pandas as pd
from collections import Counter
import re
import string

class WordCounter:
    def __init__(self):
        self.df = None
        self.df_plot = None
        self.most_common = None
        self.stop_words = {'the','not', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'that', 
                          'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                          'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'i', 'you', 'he',
                          'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'am', 'im', 'your', 'their', 'his',
                          'her', 'its', 'our', 'their', 'from', 'up', 'down', 'out', 'about', 'into', 'over', 'again', 'as', 'me', 'so',
                          'if', "my", "your", "his", "her", "its", "our", "their", "this", "that", "these", "those"}

    def load_file(self, filename):
        """Load and process a CSV file."""
        # Read CSV and remove duplicate tweets
        self.df = pd.read_csv(filename)
        self.df = self.df.drop_duplicates(subset=['Tweet'])
        self._process_text()
        return self.df_plot, self.most_common

    def _process_text(self):
        """Process the text and compute word frequencies."""
        # Combine all tweets into one string
        text = ' '.join(self.df['Tweet'].astype(str))
        
        # Convert to lowercase
        text = text.lower()

        # Remove URLs, @mentions, and #hashtags
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)  # Remove URLs
        # text = re.sub(r'@\w+', '', text)  # Remove @mentions
        # text = re.sub(r'#\w+', '', text)  # Remove #hashtags

        # Create punctuation string without @ symbol
        punctuation_no_at = string.punctuation.replace('@', '')

        # Remove all punctuation except @
        text = text.translate(str.maketrans('', '', punctuation_no_at))

        # Split into words
        words = text.split()

        # Remove stop words
        words = [word.lower() for word in words if word.lower() not in self.stop_words]
        
        # Count word frequencies
        word_freq = Counter(words)

        # Get the most common words
        self.most_common = word_freq.most_common(100)

        # Create DataFrame for plotting (only top 20)
        self.df_plot = pd.DataFrame(self.most_common[:20], columns=['Word', 'Frequency'])
