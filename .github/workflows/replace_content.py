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

def replace_key_from_source(source_content, target_content, key):
    if (source_content.get(key, None) is None):
        if (target_content.get(key , None) is not None):
            del target_content[key]
    else:
        target_content[key] = source_content[key]
    return

def replace_json_content(source_content, target_content):
    # we need to replace name(mandatory), type(mandatory), title(optional), description(optional) and content/ref keys
    target_content["name"] = source_content["name"]
    target_content["type"] = source_content["type"]
    replace_key_from_source(source_content, target_content, "title")
    replace_key_from_source(source_content, target_content, "description")
    replace_key_from_source(source_content, target_content, "content")
    replace_key_from_source(source_content, target_content, "ref")
    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python replace_content.py [contentTargerPath] [contentSourcePath]")
        sys.exit(1)

    target_path_arg = sys.argv[1]
    source_path_arg = sys.argv[2]

    json_files_target_paths = find_json_files(target_path_arg)
    json_files_source_paths = find_json_files(source_path_arg)

    print(f"JSON files in {target_path_arg}:")
    print(json_files_target_paths)

    print(f"\nJSON files in {source_path_arg}:")
    print(json_files_source_paths)

    common_files = []
    removed_files = []
    new_files = []

    for target_path in json_files_target_paths:
        if os.path.basename(target_path) in [os.path.basename(x) for x in json_files_source_paths]:
            source_path = json_files_source_paths[[os.path.basename(x) for x in json_files_source_paths].index(os.path.basename(target_path))]
            common_files.append((target_path, source_path))
        else:
            removed_files.append(target_path)

    for target_path in json_files_source_paths:
        if os.path.basename(target_path) not in [os.path.basename(x) for x in json_files_target_paths]:
            new_files.append(target_path)

    print(f"\nJSON files in both {target_path_arg} and {source_path_arg}:")
    print(*common_files, sep="\n")

    print(f"\nJSON removed in {source_path_arg}:")
    print(*removed_files, sep="\n")

    print(f"\nJSON files new to {target_path_arg}:")
    print(*new_files, sep="\n")

    for target_file, source_file in common_files:
        with open(target_file, "r") as f1:
            target_data = json.load(f1)
        with open(source_file, "r") as f2:
            source_data = json.load(f2)
        #check if the content is wrapped or not
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

        with open(target_file, "w") as f:
            json.dump(target_data, f, indent=4)
            print(f"JSON object of {os.path.basename(source_file)} copied to {os.path.basename(target_file)}")


    for new_file in new_files:
        # Get the target directory path by replacing the source directory path
        # with the target directory path in the file path
        new_file_path = str(new_file)
        new_file_path = new_file_path.replace(source_path_arg, '')[1:]
        destination = ""
        if ("metadata" not in target_path_arg):
            destination = os.path.join(target_path_arg, 'metadata' , new_file_path)
        else:
            destination = os.path.join(target_path_arg, new_file_path)
        #print(f"Destionation path {destination}")
        
        shutil.copy(new_file, destination)
        #print(f"Copied {new_file} to {destination}")

   


