import os
import sys
import json

"""
Script finds and replaces metadata content from dump to dev branch.
Overview of algorithm:
    1. find all json metadata files in dump path and dev branch path (and subdirectories)
    2. sort found files into categories - common files, removed files and new files
        a. common files are present in both dump and dev paths
        b. removed files are present in dev path and not in source path
        c. new files are present in dump path and not in dev path
    3. Process common files:
        a. load dump and dev files as JSONs
        b. replace name, type, title, description, content and ref keys from dump file to dev file
        c. save altered target JSON file in dev
    4. Process new files:
        a. load dump file as JSON
        b. copy ["content"] key to new variable
        c. remove id, links and accessInfo from the copy
        d. get directory and name from path (mdType/name.json)
        e. create new destination path
        f. save JSON copy in destination path (now in unwrapped form)    
    5. Process removed files:
        a. remove files from dev branch
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


def print_list_of_files(list):
    for f in list:
        print(f"{os.path.basename(f)}", sep="\n")


def print_list_of_tuples(list):
    for target_file, source_file in list:
        print(f"{os.path.basename(source_file)}", sep="\n")


def remove_keys_from_content(json_file):
    del json_file["id"]
    del json_file["accessInfo"]
    del json_file["links"]


def remove_JSON_wrapper(file):
    with open(file, "r") as f:
        file_data = json.load(f)
        unwrapped_file_data = file_data["content"]
        remove_keys_from_content(unwrapped_file_data)
    return unwrapped_file_data


def process_common_files(common_files):
    for dev_file, dump_file in common_files:
        with open(dev_file, "r") as f1:
            dev_file_data = json.load(f1)
        with open(dump_file, "r") as f2:
            dump_file_data = json.load(f2)
        
        # Check if content is wrapped by looking for dumpTime
        if "dumpTime" in dev_file_data:
            if "dumpTime" in dump_file_data:
                replace_json_content(dump_file_data["content"], dev_file_data["content"])
            else:
                replace_json_content(dump_file_data, dev_file_data["content"])
        else:
            if "dumpTime" in dump_file_data:
                replace_json_content(dump_file_data["content"], dev_file_data)
            else:
                replace_json_content(dump_file_data, dev_file_data)

        # Save processed file
        with open(dev_file, "w") as f:
            json.dump(dev_file_data, f, indent=4, ensure_ascii=False)
        print(f"Copied content of {os.path.basename(dev_file)} to dump", sep="\n")    


def process_new_files(new_files, metadata_source_path, metadata_target_path):
    for new_file in new_files:
        unwrapped_file_data = remove_JSON_wrapper(new_file)
        new_file_path_str = str(new_file)
        type_name_sub_path = new_file_path_str.replace(metadata_source_path, '')[1:]
        destination = ""
        if ("metadata" not in metadata_target_path):
            destination = os.path.join(metadata_target_path, 'metadata' , type_name_sub_path)
        else:
            destination = os.path.join(metadata_target_path, type_name_sub_path)

        with open(destination, "w") as f:
            json.dump(unwrapped_file_data, f, indent=4, ensure_ascii=False)

        print(f"Unwrapped and copied {os.path.basename(new_file)} to {destination}", sep="\n")


def process_removed_files(removed_files):
    for file_path in removed_files:
        os.remove(file_path)
        print(f"Removed {file_path} from branch", sep="\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_dev.py [devBranchPath] [dumpPath]")
        sys.exit(1)

    # Finds and saves all metadata JSON files in target and source paths.

    metadata_dev_branch_path_arg = sys.argv[1]
    metadata_dump_path_arg = sys.argv[2]

    json_files_dev_paths = find_json_files(metadata_dev_branch_path_arg)
    json_files_dump_paths = find_json_files(metadata_dump_path_arg)

    print(f"JSON files in {metadata_dev_branch_path_arg}:")
    print(json_files_dev_paths)

    print(f"\nJSON files in {metadata_dump_path_arg}:")
    print(json_files_dump_paths)

    # Sorting files into categories

    common_files = []
    removed_files = []
    new_files = []

    for dev_file_path in json_files_dev_paths:
        if os.path.basename(dev_file_path) in [os.path.basename(x) for x in json_files_dump_paths]:
            dump_file_path = json_files_dump_paths[[os.path.basename(x) for x in json_files_dump_paths].index(os.path.basename(dev_file_path))]
            common_files.append((dev_file_path, dump_file_path))
        else:
            removed_files.append(dev_file_path)

    for dump_file_path in json_files_dump_paths:
        if os.path.basename(dump_file_path) not in [os.path.basename(x) for x in json_files_dev_paths]:
            new_files.append(dump_file_path)

    # Process sorted files
    process_common_files(common_files)
    process_new_files(new_files, metadata_dump_path_arg, metadata_dev_branch_path_arg)
    process_removed_files(removed_files)
    
    


