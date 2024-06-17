stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 
'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 
'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
 "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 
'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

from porter_stemmer import PorterStemmer


p = PorterStemmer()
class tagging_algoritm:
    def __init__(self, raw_text):
        self.text = raw_text

    @staticmethod
    def preprocess_text(self):
        lowercased = self.text
        cleaned = lowercased.replace("."," ")
        array = list(cleaned.split(" "))
        tokenized = [sub.split() for sub in array]
        return tokenized
    
    @classmethod
    def remove_stop_words(cls,tokenized_text):
        global stopwords
        stop_words = stopwords
        filtered = []
        for word in tokenized_text:
            for j in word:
                if j in stop_words:
                    continue
                elif word not in stop_words:
                    filtered.append(word)
        return filtered
    
    @classmethod
    def stemming(cls,filtered_text):
        stemmed_text = []
        for word in filtered_text:
            for j in word:
                stemmed_word = p.stem(j,0,len(j)-1)
                stemmed_text.append(stemmed_word)
        return stemmed_text
    
    @classmethod
    def function_analyze_frequency(cls,processed_text):
        frequency_dict = {}
        for words in processed_text:
            for word in words:
                if word in frequency_dict:
                    frequency_dict[word] += 1
                else:
                    frequency_dict[word] = 1
        return frequency_dict
    
    @classmethod
    def frequency_counter(cls,words):
        mapped = {}
        for i in words:
            for j in i:
                if j not in mapped:
                    mapped[j] = 1    
                else:
                    mapped[j] += 1
        return mapped
    
    @classmethod
    def select_top_words(cls,frequency_dict,num_tags): #Num tags is arbitrary, but for example, we can choose how many tags we want  
        sorted_words = tagging_algoritm.frequency_counter(frequency_dict)
        top_words = sorted_words[:num_tags]
        return top_words
    
    def generate_tags(self,nums_tags):
        tokenized_text = tagging_algoritm.preprocess_text(self=self)
        filtered_text = tagging_algoritm.remove_stop_words(tokenized_text=tokenized_text)
        processed_text = tagging_algoritm.stemming(filtered_text=filtered_text)
        frequency_dict = tagging_algoritm.function_analyze_frequency(processed_text=processed_text)
        top_tags = tagging_algoritm.select_top_words(frequency_dict=frequency_dict,num_tags=nums_tags)
        return top_tags





#Example way of using
"""long_string = (
    "This is a very long string. This string is designed to be long and contains some comprehensible text. "
    "The purpose of this long string is to repeat certain words. Words like 'long', 'string', and 'text' are "
    "repeated many times to demonstrate the length and repetition. In this string, you will find that the word "
    "'string' appears frequently. This repetition is intentional. The goal is to make the string long and filled "
    "with repeated words. When working with long strings, it's common to encounter repetition. This string is a "
    "good example of that. As you read through this string, you will notice that certain words are repeated. "
    "These words include 'long', 'string', and 'repeated'. This is a very long string. This long string serves "
    "as an example of how to create a long string with repeated words. The string is not only long but also "
    "demonstrates repetition. This repetition makes the string longer and emphasizes certain words. When you see "
    "a long string like this, you can understand how repetition works in a text. This is the end of the long string."
)
"""

#time_to_tag = tagging_algoritm(long_string)

#print(time_to_tag.generate_tags(nums_tags=4))


