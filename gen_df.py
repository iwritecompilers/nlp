"""
This script is responsible for taking all of the
extracted data created by extract.py and create
a 'dataframe' with the specified number of features,
which will just be the most common words.

Each sample will consist of the count of each
feature word.
"""
import os
import sys
import shutil
from pathlib import Path

# ----------------------------
# Setup constants & related 
# state.
# ----------------------------

trec_cache = Path("data/trec-cache")
trec_table_path = trec_cache.joinpath("DICT")

if not trec_cache.exists():
    print(f"Please run extract.py to create cache {trec_cache}")
    sys.exit(1)

if not trec_table_path.exists():
    print(f"Please ensure that extract.py created a global TREC table {trec_table_path}")
    sys.exit(2)


feature_count = None
while feature_count is None:
    try:
        feature_count = int(input("Enter feature vector space dimension (>0): "))
        if feature_count <= 0:
            print("Feature count must be > 0")
            feature_count = None
    except ValueError:
        print("Invalid integer")


# ----------------------------
# Generate the dataframe for
# each sample
# ----------------------------

# The samples will be structured as follows:
#
# <#cw1>, <#cw2>, ..., <#cwN>, numeric_id, is_spam
#
# where '#cwX' is the "number of the X'th most
# common word" in the target up to and including
# N which is the feature_count;
#
# where 'numeric_id' identifies the target by
# a single integer;
# 
# and where 'is_spam' is a boolean identifying
# if the target is spam or not.

trec_df_path = Path(f"data/trec-df-{feature_count}")
if trec_df_path.exists():
    desire = None
    while desire is None and (desire != 'y' and desire != 'n'):
        desire = input("A dataframe for the given dimension already exists, override? [y/n]: ")
    if desire == 'n':
        print("Aborting.")
        sys.exit(0)


print("Loading global table...")
trec_table = []
table_size = 0
with trec_table_path.open(mode="r") as handle:
    for line in handle:
        trec_table.append(line.strip())
        table_size += 1
        if table_size == feature_count:
            break


print("Processing targets...")
df = []
target_total = len(os.listdir(trec_cache))
target_count = 0
for target in trec_cache.iterdir():
    name_data = target.name.split('.')
    if len(name_data) != 3: # All valid tables have 3 encoded values in the filename.
        continue

    numeric_id = int(name_data[0])
    is_spam = "spam" == name_data[1]
    is_table = "table" == name_data[2]

    if not is_table:
        continue

    # The entire sample's structure size is all of the
    # features (common words), plus the numeric_id and
    # whether it is spam or not, hence feature_count + 2
    #
    # Also, the values in the sample list are all strings
    # so that we may use str.join to join them together
    # into a csv line.
    sample_size = feature_count + 2
    sample = ['0'] * sample_size
    sample[-2] = str(numeric_id)
    sample[-1] = str(is_spam)

    with target.open(mode="r") as t_handle:
        for line in t_handle:
            table_dat = line.split(' ')
            word = table_dat[0]
            count = int(table_dat[1])
            if word in trec_table:
                index = trec_table.index(word)
                if index < feature_count:
                    sample[index] = str(count)

    df.append(sample)

    target_count += 1
    print("[1/2][%5.1f%%] %s %4s" % (100 * target_count / target_total, name_data[0], name_data[1]))


print("Writing dataframe...")
df_total = len(df)
df_count = 0
with trec_df_path.open(mode="w") as df_handle:
    for sample in sorted(df, key=lambda s: int(s[-2])):
        df_entry = ','.join(sample)
        df_handle.write(f"{df_entry}\n")

        df_count += 1
        print("[2/2][%5.1f%%] %s %4s" % (100 * df_count / df_total, sample[-2], sample[-1]))

