import os

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