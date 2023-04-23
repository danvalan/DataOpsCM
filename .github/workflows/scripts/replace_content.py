import os
import shutil
import sys
import json

"""
Script finds and replaces metadata content from source path to target path.
Overview of algorithm:
    1. find all json metadata files in source and target path (and subdirectories)
    2. sort found files into categories - common files, removed files and new files
        a. common files are present in both target and source paths
        b. removed files are present in target path and not in source path
        c. new files are present in source path and not in target path
    3. Process common files:
        a. load source and target files as JSONs
        b. replace name, type, title, description, content and ref keys from source to target
        c. save altered target JSON
    4. Process new files:
        a. get directory and name from path (mdType/name.json)
        b. create new destination path
        c. copy to destination    
    5. Process removed files:
        a. print list of removed files
"""

def find_json_files(path):
    json_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json") and file != "dumpMetadata.json":
                json_files.append(os.path.join(root, file))
    return json_files

"""
Sets target value of key to source value.
If source does not have key and target has key deletes the key from target.
"""
def replace_key_from_source(source_content, target_content, key):
    if (source_content.get(key, None) is None):
        if (target_content.get(key , None) is not None):
            del target_content[key]
    else:
        target_content[key] = source_content[key]
 

def replace_json_content(source_content, target_content):
    target_content["name"] = source_content["name"]
    target_content["type"] = source_content["type"]
    replace_key_from_source(source_content, target_content, "title")
    replace_key_from_source(source_content, target_content, "description")
    replace_key_from_source(source_content, target_content, "content")
    replace_key_from_source(source_content, target_content, "ref")


def printListOfFiles(listOfFiles):
    for f in listOfFiles:
        print(f"{os.path.basename(f)}", sep="\n")


def printListOfTuples(listOfTuples):
    for target_file, source_file in listOfTuples:
        print(f"{os.path.basename(source_file)}", sep="\n")


def processCommonFiles(common_files):
    for target_file, source_file in common_files:
        with open(target_file, "r") as f1:
            target_data = json.load(f1)
        with open(source_file, "r") as f2:
            source_data = json.load(f2)
        
        # Check if content is wrapped by looking for dumpTime
        if "dumpTime" in target_data:
            if "dumpTime" in source_data:
                replace_json_content(source_data["content"], target_data["content"])
            else:
                replace_json_content(source_data, target_data["content"])
        else:
            if "dumpTime" in source_data:
                replace_json_content(source_data["content"], target_data)
            else:
                replace_json_content(source_data, target_data)

        # Save processed file
        with open(target_file, "w") as f:
            json.dump(target_data, f, indent=4)
        print(f"Copied content of {os.path.basename(target_file)} to dump", sep="\n")    


def processNewFiles(new_files, metadata_source_path, metadata_target_path):
    for new_file in new_files:
        new_file_path_str = str(new_file)
        type_name_sub_path = new_file_path_str.replace(metadata_source_path, '')[1:]
        destination = ""
        if ("metadata" not in metadata_target_path):
            destination = os.path.join(metadata_target_path, 'metadata' , type_name_sub_path)
        else:
            destination = os.path.join(metadata_target_path, type_name_sub_path)

        shutil.copy(new_file, destination)
        print(f"Copied {new_file} to {destination}", sep="\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python replace_content.py [contentTargerPath] [contentSourcePath]")
        sys.exit(1)

    # Finds and saves all metadata JSON files in target and source paths.

    metadata_target_path_arg = sys.argv[1]
    metadata_source_path_arg = sys.argv[2]

    json_files_target_paths = find_json_files(metadata_target_path_arg)
    json_files_source_paths = find_json_files(metadata_source_path_arg)

    print(f"JSON files in {metadata_target_path_arg}:")
    print(json_files_target_paths)

    print(f"\nJSON files in {metadata_source_path_arg}:")
    print(json_files_source_paths)

    # Sorting files into categories

    common_files = []
    removed_files = []
    new_files = []

    for target_path in json_files_target_paths:
        if os.path.basename(target_path) in [os.path.basename(x) for x in json_files_source_paths]:
            source_path = json_files_source_paths[[os.path.basename(x) for x in json_files_source_paths].index(os.path.basename(target_path))]
            common_files.append((target_path, source_path))
        else:
            removed_files.append(target_path)

    for source_path in json_files_source_paths:
        if os.path.basename(source_path) not in [os.path.basename(x) for x in json_files_target_paths]:
            new_files.append(source_path)

    # Process sorted files
    processCommonFiles(common_files)
    processNewFiles(new_files, metadata_source_path_arg, metadata_target_path_arg)
    
    print("Following metadata files are present in DEV project but were removed in repository:\n")
    printListOfFiles(removed_files)
    print("You can remove them from project using Shell.")
    
    


