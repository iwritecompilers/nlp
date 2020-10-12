import os
import os.path
import shutil
from pathlib import Path


numeric_id_limit = 9
spam_indicator = "spam"
ham_indicator = "ham"

# The default directories from which to copy
# and move to.
source_dir = Path("data/trec/raw")
target_dir = Path("data/trec/sanitized")

# Maintains a count reference for each file
# added to the targets directory for renaming and
# indexing.
count = 0


def verify():
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist")
        sys.exit(1)
    if not os.path.exists(target_dir):
        target_dir.mkdir(parents=True)
    else:
        is_target_dir_empty = len(os.listdir(target_dir)) == 0
        if not is_target_dir_empty:
            desire = None
            while desire is None or (desire != "y" and desire != "n"):
                desire = input(f"Target directory {target_dir} is not empty, wipe contents? [y/n]: ").lower()
            if desire == "y":
                print("Removing existing target contents...")
                shutil.rmtree(target_dir)
                target_dir.mkdir()
            else:
                print(f"Target directory is not empty and delete request is denied")
                sys.exit(2)


def copy_target_standard(target, is_spam):
    global count
    target_name = str(count)
    padded_name = "0" * (numeric_id_limit - len(target_name)) + target_name

    target_postfix = "spam" if is_spam else "ham"
    target_file = target_dir.joinpath(f"{padded_name}.{target_postfix}")

    shutil.copyfile(target, target_file) 
    count += 1



def copy_trec_standard(trec_dir):
    global count
    data_dir = trec_dir.joinpath("data")
    index_file = trec_dir.joinpath("full/index")

    print(f"Reading index for {str(trec_dir)}")
    spam = []
    with index_file.open(mode="r", encoding="latin-1") as ind:
        for line in ind:
            entry = line.split(' ')
            is_spam = "spam" == entry[0]
            elements = entry[1].split('/')
            corpi = int(elements[-2])
            target = int(elements[-1])
            while len(spam) <= corpi:
                spam.append([])
            target_list = spam[corpi]
            while len(target_list) <= target:
                target_list.append(False)
            target_list[target] = is_spam
    
    print(f"Copying existing targets in {trec_dir}")
    for corpi in data_dir.iterdir():
        for target in corpi.iterdir():
            i_corpus = int(corpi.parts[-1])
            i_target = int(target.parts[-1])
            copy_target_standard(target, spam[i_corpus][i_target])


def copy_trec5():
    copy_trec_standard(source_dir.joinpath("trec05p-1"))
    

def copy_trec6():
    copy_trec_standard(source_dir.joinpath("trec06p"))


def copy_trec7():
    global count
    trec_dir = source_dir.joinpath("trec07p")
    data_dir = trec_dir.joinpath("data") 
    index_file = trec_dir.joinpath("full/index")

    print(f"Reading index for {str(trec_dir)}")
    spam = []
    with index_file.open(mode="r", encoding="latin-1") as ind:
        for line in ind:
            entry = line.split(' ')
            is_spam = "spam" == entry[0]
            target = int(entry[1].split('.')[-1])
            while len(spam) <= target:
                spam.append(False)
            spam[target] = is_spam

    print(f"Copying existing targets in {trec_dir}")
    for target in data_dir.iterdir():
        i_target = int(target.parts[-1].split('.')[-1])
        copy_target_standard(target, spam[i_target])


if __name__ == "__main__": 
    try:
        verify()
        copy_trec5()
        copy_trec6()
        copy_trec7()
        print("Ok")
    except RuntimeError as e:
        print(str(e))

