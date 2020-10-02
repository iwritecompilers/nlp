import nltk
import pandas as pd

df = pd.read_csv('filtered_data.csv', index_col=0)
df = df.sample(frac=1).reset_index(drop=True)

from collections import Counter

# all_ham_words = df[df['label'] == False]['message'].tolist()
# all_ham_words = " ".join([str(word) for word in all_ham_words])

# ham_word_count = Counter(all_ham_words.split(" ")).most_common()
# fout = open('most_common_ham.txt', 'w+')
# for word, count in ham_word_count:
#     fout.write(f"{word} {count}\n")
# fout.close()

all_spam_words = df[df['label'] == True]['message'].tolist()
all_spam_words = " ".join([str(word) for word in all_spam_words])

spam_word_count = Counter(all_spam_words.split(" ")).most_common()
fout = open('most_common_spam.txt', 'w+')
for word, count in spam_word_count:
    fout.write(f"{word} {count}\n")
fout.close()
