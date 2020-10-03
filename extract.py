import os
import sys
import shutil
from pathlib import Path
from html.parser import HTMLParser
from udax.httpemail import HttpEmail

# -------------------------------------
# Constant definitions and setup to
# prepare for data extraction.
# -------------------------------------

trec = Path("data/trec")
trec_cache = Path("data/trec-cache")
trec_raw = Path("data/trec-raw")

trec_table_path = Path("data/trec-cache/DICT")


if not trec_raw.exists():
    print(f"Please download the trec05, trec06, and trec07 datasets into {trec_raw}")
    sys.exit(1)

if not trec.exists():
    print(f"Please run sanitize.py before executing extract.py")
    sys.exit(2)

if not trec_cache.exists():
    print(f"{trec_cache} does not exist, creating...")
    trec_cache.mkdir(parents=True)
elif len(os.listdir(trec_cache)) > 0:
    desire = None
    while desire is None or (desire != 'y' and desire != 'n'):
        desire = input(f"{trec_cache} is not empty, do you want to clear it? [y/n]: ").lower()
    if desire == 'n':
        print(f"Refusing to clear {trec_cache}, aborting...")
        sys.exit(0)
    print(f"Clearing {trec_cache}...")
    shutil.rmtree(trec_cache)
    trec_cache.mkdir()


# -------------------------------------
# Generate cache 
# -------------------------------------

# Contains all of the unique words encountered
# in every file of trec5, trec6, and trec7, and
# their occurrances.
trec_table = {}


def print_word_table(global_table, fd=sys.stdout):
    for word, count in global_table.items():
        fd.write(f"{word} {count}\n")


print("Processing targets...")
target_total = len(os.listdir(trec))
target_count = 0
for target in trec.iterdir():
    # The target filename is embossed with
    # a numeric id in the order it was processed
    # by sanitize.py and also a prefix indicating
    # whether it is spam or not
    name_data = target.name.split('.')
    numeric_id = int(name_data[0])
    is_spam = "spam" == name_data[1]

    email = HttpEmail(target)
    with trec_cache.joinpath(f"{target.name}.table").open(mode="w") as handle:
        for word, stat in email.word_table.items():
            # stat[0] - count
            # stat[1] - relative frequency
            handle.write(f"{word} {stat[0]}\n")
            if word not in trec_table:
                trec_table[word] = stat[0]
            else:
                trec_table[word] += stat[0]

    target_count += 1
    print("[%5.1f%%] %s %4s" % (100 * target_count / target_total, name_data[0], name_data[1]))


print(f"Exporting global dictionary {trec_table_path}...")
with trec_table_path.open(mode="w", buffering=(2**16)) as handle:
    # Writes out the dictionary table to DICT
    # in the cache with the most frequent 'word'
    # first in the file, and the least frequent
    # 'word' last in the file.
    for word in sorted(trec_table.items(), key=lambda w: w[1], reverse=True):
        handle.write(f"{word[0]}\n")
print("Done")
