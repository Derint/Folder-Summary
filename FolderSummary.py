print("\n  *Importing Libraries.....", end='')

import os, json, argparse, subprocess, warnings
from collections import defaultdict
from HelperFunction import *

warnings.filterwarnings("ignore")


def getKey(dictionary, val):
    for key, values in dictionary.items():
        if val in values:
            return key
    return None

def cleanUp(path):
    print(" *Cleaning....", end='')
    for i, _, k in os.walk(path):
        for file in k:
            fn, ext = os.path.splitext(file)
            if ext=='.wbk' or fn.startswith('~$'):
                os.remove(i+slash+file)

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', dest='path')
    return parser.parse_args()


args = getArgs()
path = args.path

slash = '\\' if os.name in ['dos', 'nt'] else '/'

if path is None:
    path = input("\r  [>]  Enter Folder/Directory Path: ")

if not os.path.isdir(path):
    print("  [!]  Invalid Folder/Directory Path ")
    exit()
    

with open("Settings.json", "r") as Jfile:
    settings_data = json.load(Jfile)

ext_dict = settings_data['ext_dict']
ext_dict['Other'] = []

fmt = settings_data['format']
ext_pgs_dict = {key: eval(func) for key, func in settings_data['pageCntFunc'].items()}

ext_cnt_dict = {i:0 for i in ext_dict}
ext_pgs_cnt = {i:0 for i in ext_dict}

totalFiles = 0
error_paths = []
REF_DICT = defaultdict(set)
cleanUp(path)
print("\r  *Calculating...", end='')
for fol_path, directory, files in os.walk(path):
    for file in files:
        totalFiles+=1
        fn, ext = os.path.splitext(file)
        fp = fol_path+slash+file
        ext = ext[1:].lower()
        key = getKey(ext_dict, ext)
        
        if key is None: 
            key = "Other"
            ext_dict[key].append(ext)
        REF_DICT[key].add(ext)

        pgs=1
        if key in ext_pgs_dict:
            pgs = ext_pgs_dict[key](fp)
        
        if pgs==0:
            error_paths.append(fp)
            continue
        ext_pgs_cnt[key] += pgs
        ext_cnt_dict[key] += 1
        print(f"\r  *Calculating {sum(ext_cnt_dict.values())}...", end='')
print(f"\r  [+]  Found {sum(ext_cnt_dict.values())} files in the directory....", end='\n\n')
cleanUp(path)

print(f"\r  {'File Type'.center(20)}|{'File(s) Found'.center(15)}|{'Number of Pages/Sheet'.center(25)}")
print('  ' + "---"*20)
for fileType in ext_cnt_dict:
    noT, noP = ext_cnt_dict.get(fileType), ext_pgs_cnt.get(fileType)
    if noT:
        fmtStr = fmt.get(fileType) if fileType in fmt.keys() else ""
        print(f"  {fileType.ljust(20)}|{str(noT).center(15)}|{str(noP).rjust(10)} {fmtStr}")
print('  ' + "---"*20)
print(f"  {f'Total Files: {totalFiles}'.ljust(20)}|{str(sum(ext_cnt_dict.values())).center(15)}|{str(sum(ext_pgs_cnt.values())).rjust(10)} \n\n")

if error_paths:
    print(f"  [NOTE]  Some File(s) [{len(error_paths)}] were not able to be Read. Pls open it manually and count.")
    with open(path+slash+"error_paths.txt", "w") as f:
        f.write("\n".join(error_paths))
    if os.name in ['dos', 'nt']:
        os.startfile(path+slash+"error_paths.txt")
        pass
    else:
        subprocess.call(['xdg-open', path+slash+"error_paths.txt"])

print('\n\n')
print("Reference Table".center(50))
print("----"*15)
for col in REF_DICT:
    print('  ' + col.ljust(20), end=' | ')
    print(", ".join(REF_DICT[col]).upper())
