import nltk
import pandas as pd
from string import punctuation
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 

df = pd.read_csv('labeled_data.csv', dtype={'message': 'string'}, index_col=0)
ps = PorterStemmer()

eng_stopwords = stopwords.words('english')

def is_stopword (x):
    if x in eng_stopwords or x == '':
        return False
    else:
        return True
    
i = 0

def filter_data (x):
    global i

    try:
        x = x.translate(str.maketrans('','',punctuation+'\t\n\r'))
        tokenized = filter(is_stopword, x.lower().split(' '))
        answer = " ".join(ps.stem(word) for word in tokenized)
    except:
        return x
    # tokenized = filter(is_stopword, word_tokenize(x.lower()))
    # ans = [ps.stem(word) for word in tokenized]
    print(f"{i/df.shape[0] * 100}")
    i += 1
    
    return answer

curr = df['message'].apply(filter_data)
df['message'] = curr

df.to_csv('filtered_data.csv')