import argparse
import json
import os.path


def unpack(packed_file, output_directory):
    project_title = packed_file.rstrip(".json")

    with open(packed_file, "r") as pf:
        json_data = json.load(pf)

    if "ObjectStates" not in json_data.keys():
        return

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for object_state in json_data["ObjectStates"]:
        if "LuaScript" not in object_state:
            continue

        if object_state["LuaScript"].startswith(" " * 10):
            continue

        unpacked_file = f"{output_directory}/{object_state['Name']}_{object_state['GUID']}.lua"
        with open(unpacked_file, "w") as uf:
            uf.write(object_state["LuaScript"].replace("\r\n", "\n"))
            object_state["LuaScript"] = f"{{{{unpacked_file}}}}"

    json_data['SaveName'] = project_title
    manifest_file = f"{json_data['SaveName']}_manifest"
    with open(f"{output_directory}/{manifest_file}.json", "w") as mf:
        json.dump(json_data, mf, indent=2)


def pack(packed_file, input_directory):
    project_title = packed_file.rstrip(".json")

    manifest_file = f"{input_directory}/{project_title}_manifest.json"
    with open(manifest_file, "r") as mf:
        json_data = json.load(mf)

    lua_files = [f for f in os.listdir(input_directory) if f.endswith(".lua")]
    new_object_states = []
    for object_state in json_data["ObjectStates"]:
        search_file = f"{object_state['Name']}_{object_state['GUID']}.lua"
        if search_file not in lua_files:
            new_object_states.append(object_state)
            continue

        with open(f"{input_directory}/{search_file}", "r") as uf:
            lua_code = "".join(uf.readlines())
            object_state["LuaScript"] = lua_code

        new_object_states.append(object_state)
    json_data["ObjectStates"] = new_object_states

    with open(f"{packed_file}", "w") as of:
        json.dump(json_data, of, indent=2)


if __name__ == "__main__":
    """       
    usage: tts_tools.py [-h] (--unpack UNPACK | --pack PACK) savefile
    
    manage packing and unpacking tts save files
    
    positional arguments:
        savefile         a tts save file
    
    options:
        -h, --help       show this help message and exit
        --unpack UNPACK  unpack tts save file into a directory
        --pack PACK      pack a directory into a tts save file
    """
    argp = argparse.ArgumentParser(prog="tts_tools.py",
                                   description="manage packing and unpacking tts save files")

    argp.add_argument('savefile', help="a tts save file", type=str)

    argp_action_group = argp.add_mutually_exclusive_group(required=True)
    argp_action_group.add_argument("--unpack", help="unpack tts save file into a directory", type=str)
    argp_action_group.add_argument("--pack", help="pack a directory into a tts save file", type=str)

    args = argp.parse_args()

    if args.unpack:
        unpack(args.savefile, args.unpack)

    if args.pack:
        pack(args.savefile, args.pack)
