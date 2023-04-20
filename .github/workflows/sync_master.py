import os
import shutil
import sys
import json

def find_json_files(path):
    json_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json") and file != "dumpMetadata.json":
                json_files.append(os.path.join(root, file))
    return json_files

def printListOfTuples(listOfTuples):
    for target_file, source_file in listOfTuples:
        print(f"{os.path.basename(source_file)}", sep="\n")
    return 

def printListOfFiles(listOfFiles):
    for f in listOfFiles:
        print(f"{os.path.basename(f)}", sep="\n")
    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_master.py [masterBranchPath] [dumpProjectPath]")
        sys.exit(1)

    master_path_arg = sys.argv[1]
    dump_path_arg = sys.argv[2]

    json_files_master_paths = find_json_files(master_path_arg)
    json_files_dump_paths = find_json_files(dump_path_arg)

    #print(f"JSON files in {master_path_arg}:")
    #print(json_files_master_paths)

    #print(f"\nJSON files in {dump_path_arg}:")
    #print(json_files_dump_paths)

    common_files = []
    removed_files = []

    for master_path in json_files_master_paths:
        if os.path.basename(master_path) in [os.path.basename(x) for x in json_files_dump_paths]:
            dump_path = json_files_dump_paths[[os.path.basename(x) for x in json_files_dump_paths].index(os.path.basename(master_path))]
            common_files.append((master_path, dump_path))
        else:
            removed_files.append(master_path)

    print(f"\nJSON files in both {master_path_arg} and {dump_path_arg}:")
    printListOfTuples(common_files)
    
    print(f"\nJSON files removed in {dump_path_arg}:")
    printListOfFiles(removed_files)

    for master_file, dump_file in common_files:
        with open(master_file, "r") as f1:
            master_data = json.load(f1)
        with open(dump_file, "r") as f2:
            dump_data = json.load(f2)
        #check if master file is wrapped or not
        if "dumpTime" in master_data:
            dump_data["dumpTime"] = master_data["dumpTime"]

        with open(dump_file, "w") as f:
            json.dump(dump_data, f, indent=4)
            print(f"Dump time of object {os.path.basename(dump_file)} synchronized with master.")


    for dump_file in json_files_dump_paths:
        new_file_path = str(dump_file)
        new_file_path = new_file_path.replace(dump_path_arg, '')[1:]
        print(f"New file path {new_file_path}")
        destination = ""
        if ("metadata" not in master_path_arg):
            destination = os.path.join(master_path_arg, 'metadata' , new_file_path)
        else:
            destination = os.path.join(master_path_arg, new_file_path)
        print(f"Destionation path {destination}")
        
        shutil.copy(dump_file, destination)
        print(f"Copied {dump_file} to {destination}", sep="\n")
        
    for file_path in removed_files:
        os.remove(file_path)
        print(f"Removed {file_path} from master", sep="\n")
