import os
import shutil
import os.path

target_dir = "./data/trec/targets/"
index_dir = "./data/trec/indices/"

t5_data = "./data/trec-raw/trec05p-1/data/"
t5_index_file = "./data/trec-raw/trec05p-1/full/index"

t6_data = "./data/trec-raw/trec06p/data/"
t6_index_file = "./data/trec-raw/trec06p/full/index"

t7_data = "./data/trec-raw/trec07p/data/"
t7_index_file = "./data/trec-raw/trec07p/full/index"

# remove targets if some already exist because
# they will be replaced.
target_count = len(os.listdir(target_dir))
if target_count > 0:
    shutil.rmtree(target_dir)
    target_count = 0

# ---------------------------------------------------- #
# handle copy of data from the trec05p-1 directory     #
# ---------------------------------------------------- #
if True: # namespace
    spam = []
    with open(t5_index_file, mode="r", encoding="latin-1") as ind:
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

    index_new_out = open(f"{index_dir}/index.t5", mode="w")
    for corpi in os.listdir(t5_data):
        for target in os.listdir(f"{t5_data}/{corpi}"):
            name = str(target_count)
            padded_name = "0" * (6 - len(name)) + name
            i_corpi = int(corpi)
            i_target = int(target)
            if spam[i_corpi][i_target]:
                index_new_out.write(f"spam {target_count}\n")
            else:
                index_new_out.write(f"ham {target_count}\n")
            print(target)
            print(f"{target_dir}/{padded_name}")
            shutil.copyfile(f"{t5_data}/{corpi}/{target}", f"{target_dir}/{padded_name}") 
            # os.rename(target, f"{target_dir}/{padded_name}")
            target_count += 1
    index_new_out.close()
