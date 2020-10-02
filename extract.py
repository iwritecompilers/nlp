import os
import sys
import shutil
import time
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
spam_table_path = trec_cache.joinpath("TABLE.spam")
ham_table_path = trec_cache.joinpath("TABLE.ham")

if not trec_raw.exists():
    raise RuntimeError(f"Please download the trec05, trec06, and trec07 datasets into {trec_raw}")

if not trec.exists():
    raise RuntimeError(f"Please run sanitize.py before executing extract.py")

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

# Unlike in the HttpEmail class, these 
# tables are simplified to word -> count
# instead of word -> (count, relative-freq)
spam_table = {}
ham_table = {}


def merge_word_table(global_table, httpemail_table):
    gt = global_table
    ht = httpemail_table

    for word, statistic in ht.items():
        if word in gt:
            gt[word] = gt[word] + statistic[0]
        else:
            gt[word] = statistic[0]


def print_word_table(global_table, fd=sys.stdout):
    for word, count in global_table.items():
        fd.write(f"{word} {count}\n")


print("Processing targets...")
target_total = len(os.listdir(trec))
target_count = 0
begin = time.monotonic_ns()

for target in trec.iterdir():
    t_begin = time.monotonic_ns()
    # The target filename is embossed with
    # a numeric id in the order it was processed
    # by sanitize.py and also a prefix indicating
    # whether it is spam or not
    name_data = target.name.split('.')
    numeric_id = int(name_data[0])
    is_spam = "spam" == name_data[1]

    email = HttpEmail(target)
    word_table = email.word_table

    with trec_cache.joinpath(f"{target.name}.table").open(mode="w") as handle:
        email.print_word_table(handle)

    if is_spam:
        merge_word_table(spam_table, word_table)
    else:
        merge_word_table(ham_table, word_table)

    target_count += 1
    t_end = time.monotonic_ns()
    print("%4s %s elapsed: %6.2fms (%.1f%%)" % \
            (name_data[1],                     \
             name_data[0],                     \
             (t_end - t_begin) * 1e-6,         \
             100 * target_count / target_total))

end = time.monotonic_ns()
sec = int((end - begin) * 1e-9)
print("Processing targets elapsed: %dm %ds" % (sec // 60, sec % 60))

print("Exporting global word tables...")
with spam_table_path.open(mode="w") as handle:
    print_word_table(spam_table, handle)

with ham_table_path.open(mode="w") as handle:
    print_word_table(ham_table, handle)
print("Done")
