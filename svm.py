"""
After all of the previous scripts are run to prepare
the dataframe, i.e.

    1. sanitize.py
    2. extract.py
    3. gen_df.py

this script takes over, creates the model, trains it,
and evalutes it against the desired dataframe.
"""
import os
import sys
import shutil
from pathlib import Path
from sklearn.svm import LinearSVC


# -----------------------------------
# Setup constants & related state.
# -----------------------------------

feature_count = None
while feature_count is None:
    try:
        feature_count = int(input("Enter feature vector space dimension (>0): "))
        if feature_count <= 0:
            print("Feature count must be > 0")
            feature_count = None
    except ValueError:
        print("Invalid integer")


trec_df_path = Path(f"data/trec-df-{feature_count}")
if not trec_df_path.exists():
    print(f"Requested dataframe does not exist {trec_df_path}")
    sys.exit(1)

# -----------------------------------
# Load in the dataframe manually and
# create training/test sets.
# -----------------------------------

print("Loading dataframe...")
df = []
with trec_df_path.open(mode="r") as handle:
    for line in handle:
        raw_sample = line.split(',')
        sample_size = len(raw_sample)
        parsed_sample = [0] * sample_size
        for i in range(feature_count):
            parsed_sample[i] = int(raw_sample[i])

        numeric_id = int(raw_sample[-2].strip())
        is_spam = int("True" == raw_sample[-1].strip())

        parsed_sample[-2] = numeric_id 
        parsed_sample[-1] = is_spam

        df.append(parsed_sample)


train_ratio = 0.75
train_samples = int(len(df) * train_ratio)
test_samples = len(df) - train_samples

print(f"Creating {train_samples} training samples, {test_samples} testing samples (ratio: {100 * train_ratio}%)")
x_train = []
y_train = []

x_test = []
y_test = []

for i in range(train_samples):
    x_train_sample = df[i][0:feature_count]
    y_train_sample = df[i][-1]

    x_train.append(x_train_sample)
    y_train.append(y_train_sample)

for i in range(test_samples):
    j = train_samples + i
    x_test_sample = df[j][0:feature_count]
    y_test_sample = df[j][-1]

    x_test.append(x_test_sample)
    y_test.append(y_test_sample)


# -----------------------------------
# Create, train, and evaluate the SVM
# model (linear).
# -----------------------------------

clf = LinearSVC()

print("Training...")
clf.fit(x_train, y_train)


print("Evaluating...")
print("Accuracy: %5.1f%%" % (100 * clf.score(x_test, y_test)))


print("Done")
