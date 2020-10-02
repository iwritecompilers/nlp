from pathlib import PurePath, Path
from html.parser import HTMLParser

class DataStruct():
    """
    A dummy class definition to serve as a namespace
    for data constants.
    """
    pass


class Trec:
    """
    An abstraction over each unique TREC dataset from
    different years. We do this to make sure we can use
    the existing data out of the box by abstracting how
    we access the data through a common interface.
    """
    def __init__(self, root):
        self.root = Path(root)
    
    def iterate_targets(self, corpus_limit: int = None, target_limit: int = None):
        """
        Iterates over target data files in the dataset. The
        return is in the form
        
            (corpus: Path, target: Path, is_spam: bool)
        
        where the paths are relative to the root specified in
        the constructor.
        
        :param corpus_limit
            The maximum number of corpi to recurse into.
        
        :param target_limit
            The maximum number of targets to iterate over per
            corpus.
        """
        raise NotImplementedError("iterate_targets")


class Trec5_6(Trec):
    """trec05p-1 & trec06p specific implementation of the dataset."""
    def __init__(self, root):
        super().__init__(root)
        
        # The index is structured as a 2D boolean
        # vector space where (corpus: int, target: int)
        # yields true or false depending on if the target
        # within the corpus is a spam email or not.
        self.spam_index = []
        
        # Actually load in the index.
        index_stream = self.root.joinpath("full/index").open(mode="r", encoding="latin-1")
        for line in index_stream:
            
            entry = line.split(' ')
            is_spam = "spam" == entry[0]
            
            identity = entry[1].split('/')
            corpus = int(identity[2])
            target = int(identity[3])
            
            while len(self.spam_index) <= corpus:
                self.spam_index.append([])
            
            corpus_index = self.spam_index[corpus]
            while len(corpus_index) <= target:
                corpus_index.append(False)
            
            corpus_index[target] = is_spam
        index_stream.close()
    
    def iterate_targets(self, corpus_limit: int = None, target_limit: int = None):
        # copy limits to keep a reference.
        # these will be decremented.
        l_corpus_limit = corpus_limit
        l_target_limit = target_limit
        
        data = self.root.joinpath("data")
        
        for corpus in data.iterdir():
            
            if l_corpus_limit is not None:
                if l_corpus_limit <= 0:
                    break
                l_corpus_limit -= 1
                
            l_target_limit = target_limit
            
            for target in corpus.iterdir():
                
                if l_target_limit is not None:
                    if l_target_limit <= 0:
                        break
                    l_target_limit -= 1
                
                corpus_id = int(target.parts[-2])
                target_id = int(target.parts[-1])
                
                yield (corpus, target, self.spam_index[corpus_id][target_id])

class Trec7(Trec):
    """trec07p specific implementation of the dataset. """
    def __init__(self, root):
        super().__init__(root)
        
        # Unlike Trec5_6, this index is single
        # dimensional with boolean values that indicate
        # whether a file with the index of the boolean
        # is spam or not.
        self.spam_index = []

        index_stream = self.root.joinpath("full/index").open(mode="r", encoding="latin-1")
        for line in index_stream:
            
            entry = line.split(' ')
            is_spam = "spam" == entry[0]
            
            target = int(entry[1].split('.')[-1])
            while len(self.spam_index) <= target:
                self.spam_index.append(False)
                
            self.spam_index[target] = is_spam
        index_stream.close()

    def iterate_targets(self, corpus_limit: int = None, target_limit: int = None):
        if corpus_limit is not None and corpus_limit <= 0:
            return
        
        data = self.root.joinpath("data")
        for target in data.iterdir():
            
            if target_limit is not None:
                if target_limit <= 0:
                    break
                target_limit -= 1
            
            target_id = int(target.parts[-1].split('.')[-1])
            
            yield (data, target, self.spam_index[target_id])


# The assumed directory structure is as follows:
#
# data
# -- TREC
# -- -- trec05p-1
# -- -- trec06p
# -- -- trec07p
# Extract.ipynb
#
data = DataStruct()
data.root = Path("data").resolve()

data.trec  = data.root.joinpath("TREC")
data.trec5 = Trec5_6(data.trec.joinpath("trec05p-1"))
data.trec6 = Trec5_6(data.trec.joinpath("trec06p"))
data.trec7 = Trec7(data.trec.joinpath("trec07p"))
data.trec_list = [
    data.trec5,
    data.trec6,
    data.trec7,
]



class MyHTMLParser(HTMLParser):
    def __init__ (self):
        super(MyHTMLParser, self).__init__()
        self.current_email = ""
        
    def handle_starttag(self, tag, attrs):
        pass
    
    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
        self.current_email += data + " "
        
    def error(self, message):
        print('---------------')
        print('ERROR: ' + message)
        print('---------------')


def filter_message_headers(encoded_message):
    new_encoded_message = []
    i = 0
    while i < len(encoded_message):
        sline = encoded_message[i].decode("latin-1")
        if "-----Original Message-----" in sline:
            while i < len(encoded_message) and len(encoded_message[i].decode("latin-1").strip()) != 0:
                i += 1
        if i < len(encoded_message):
            new_encoded_message.append(encoded_message[i])
        i += 1
    return new_encoded_message


def extract_metadata(encoded_message):
    sender = ""
    content_type = ""
    boundary = None
    body_index = None
    
    # [0] = body start
    # [-1] = file end
    split_indices = []
    
    for i, line in enumerate(encoded_message):
        sline = line.decode('latin-1')
        if str.encode("From: ") in line:
            sender = sline[6:].strip()
        if content_type == '' and str.encode("Content-Type: ") in line:
            content_type = sline[14:sline.find(';')]
        if 'boundary' in sline and sline.find('=') != -1:
            boundary = sline[sline.find('=')+1:][1:-2]
            continue
        if boundary and boundary in sline:
            split_indices.append(i)
        if not body_index and sline.strip() == "":
            body_index = i
    if len(split_indices) == 0:
        split_indices.append(body_index)
    split_indices.append(len(encoded_message)-1)
    return (sender, content_type, boundary, split_indices)

spam_senders = []
spam_bodies = []

ham_senders = []
ham_bodies = []

for trec in data.trec_list:
    for corpus, target, is_spam in trec.iterate_targets():
        with target.open(mode="rb") as handle:
            encoded_message = filter_message_headers(handle.readlines())
            sender, content_type, boundary, split_indices = extract_metadata(encoded_message)
            charset = "latin-1"
            body = ""

            if len(split_indices) > 2:
                for i in range(len(split_indices) - 1):
                    x = split_indices[i]
                    y = split_indices[i + 1]
                    j = x + 1
                    while j < y:
                        line = encoded_message[j].decode(charset).strip()
                        if len(line) == 0:
                            break
                        j += 1
                    print("--- EMAIL: --- ", target, is_spam)
                    parser = MyHTMLParser()
                    parser.feed(b"".join(encoded_message[j+1:y]).decode(charset))
                    body = parser.current_email
            else:
                try:
                    print("--- EMAIL: --- ", target, is_spam)
                    parser = MyHTMLParser()   
                    parser.feed(b"".join(encoded_message[split_indices[0]:split_indices[1]]).decode(charset))
                    body = parser.current_email
                except:
                    body = ""
                
            
            if len(body) <= 1:
                continue

            if is_spam:
                spam_bodies.append(body)
                spam_senders.append(sender)
            else:
                ham_bodies.append(body)
                ham_senders.append(sender)
            
# displaying most common ham and spam words

# from collections import Counter
# import string

# extraneous = string.punctuation + "\t\n\r1234567890"

# import nltk
# from nltk.corpus import stopwords
# eng_stopwords = stopwords.words('english')

# def is_stopword (x):
#     if x in eng_stopwords or x == '':
#         return False
#     else:
#         return True

# # Most common words for ham emails
# all_ham = " ".join(ham_bodies).lower()
# filtered_ham = " ".join(list(filter(is_stopword, all_ham.translate(str.maketrans('', '', extraneous)).split(" "))))
# most_common_ham = Counter(filtered_ham.translate(str.maketrans('', '', extraneous)).split(" ")).most_common()

# all_spam = " ".join(spam_bodies).lower()
# filtered_spam = " ".join(list(filter(is_stopword, all_spam.translate(str.maketrans('', '', extraneous)).split(" "))))
# most_common_spam = Counter(filtered_spam.translate(str.maketrans('', '', extraneous)).split(" ")).most_common()

# print("Most common ham words")
# fout = open('most_common_ham.txt', "w+")
# for word, count in most_common_ham:
#     fout.write(f"{word} {count}\n")
# fout.close()

# print("Most common spam words")
# fout = open('most_common_spam.txt', "w+")
# for word, count in most_common_spam:
#     fout.write(f"{word} {count}\n")
# fout.close()

# Saving all data into one csv file using pandas
from pandas import DataFrame

true_list = [True for i in range(len(spam_bodies))]
false_list = [False for i in range(len(ham_bodies))]

zipped_list = list(zip(ham_bodies + spam_bodies, ham_senders + spam_senders, false_list + true_list))

print(len(ham_bodies + spam_bodies), len(ham_senders + spam_senders), len(false_list + true_list))
df = DataFrame(zipped_list, columns=['message', 'sender', 'label'])
df.to_csv('labeled_data.csv')