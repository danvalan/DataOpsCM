import os
import shutil
import sys
import json

"""
Script finds and copies metadata files from dump path to master branch path.
Overview of algorithm:
    1. find all json metadata files in dump path and master branch path (and subdirectories)
    2. sort found files into categories - common files and removed files
        a. common files are present in both dump and master paths
        b. removed files are present in master path and not in dump path
    3. Process common files:
        a. load master and dump file as JSONs
        b. replace dump time from master to dump file 
            (this step is to ensure the workflow is not commiting just changes in dumpTime)
        c. save altered dump JSON
    4. Copy all metadata files from dump to master branch    
    5. Process removed files:
        a. delete files in master branch
"""

def find_json_files(path):
    json_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json") and file != "dumpMetadata.json":
                json_files.append(os.path.join(root, file))
    return json_files

def print_list_of_tuples(list):
    for target_file, source_file in list:
        print(f"{os.path.basename(source_file)}", sep="\n")
    return 

def print_list_of_files(list):
    for f in list:
        print(f"{os.path.basename(f)}", sep="\n")
    return

def synchronize_dump_time(common_files):
    for master_file, dump_file in common_files:
        with open(master_file, "r") as f1:
            master_data = json.load(f1)
        with open(dump_file, "r") as f2:
            dump_data = json.load(f2)
        
        #check if master file is wrapped or not
        if "dumpTime" in master_data:
            dump_data["dumpTime"] = master_data["dumpTime"]

        with open(dump_file, "w") as f:
            json.dump(dump_data, f, indent=4, ensure_ascii=False)
            print(f"Dump time of object {os.path.basename(dump_file)} synchronized with master.")


def copy_dump_files_to_master(dump_files, master_path, dump_path):
     for dump_file in dump_files:
        new_file_path = str(dump_file)
        new_file_path = new_file_path.replace(dump_path, '')[1:]
        destination = os.path.join(master_path, new_file_path)
        
        shutil.copy(dump_file, destination)
        print(f"Copied {dump_file} to {destination}", sep="\n")


def remove_files_from_master(removed_files):
    for file_path in removed_files:
        os.remove(file_path)
        print(f"Removed {file_path} from master", sep="\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_master.py [masterBranchPath] [dumpProjectPath]")
        sys.exit(1)

    master_path_arg = sys.argv[1]
    dump_path_arg = sys.argv[2]

    # Find json files in master path and dump path (and subdirectories)

    json_files_master_paths = find_json_files(master_path_arg)
    json_files_dump_paths = find_json_files(dump_path_arg)
    
    # Sort files

    common_files = []
    removed_files = []

    for master_path in json_files_master_paths:
        if os.path.basename(master_path) in [os.path.basename(x) for x in json_files_dump_paths]:
            dump_path = json_files_dump_paths[[os.path.basename(x) for x in json_files_dump_paths].index(os.path.basename(master_path))]
            common_files.append((master_path, dump_path))
        else:
            removed_files.append(master_path)

    # Process sorted files

    synchronize_dump_time(common_files)
    copy_dump_files_to_master(json_files_dump_paths, master_path_arg, dump_path_arg)
    remove_files_from_master(removed_files)
   
        
    
