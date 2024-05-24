from modules.open_digraph import *
import inspect
import modules
import importlib.util
import os

file_map = {
    "__init__.py": "modules/__init__.py",
    "adders.py": "modules/adders.py",
    "addition_checkEncode.py": "modules/addition_checkEncode.py",
    "bool_circ.py": "modules/bool_circ.py",
    "bool_circ_gates_mx.py": "modules/bool_circ_gates_mx.py",
    "matrix_operations.py": "modules/matrix_operations.py",
    "node.py": "modules/node.py",
    "open_digraph.py": "modules/open_digraph.py",
    "open_digraph_composition_mx.py": "modules/open_digraph_composition_mx.py",
    "open_digraph_paths_distance_mx.py": "modules/open_digraph_paths_distance_mx.py"
}

# Function to print the contents of a file or a specific method within the file
def print_content(file_name, method_name=None):

    # PS it works for everything except addition_checkEncode.py functions
    # NOT WORKING FOR addition_checkEncode.py functions
    def find_function(module, target_function_name):
        # Get all members of the module
        members = inspect.getmembers(module)
        
        cls = getattr(module, file_name[:-3])
        members = inspect.getmembers(cls)

        # Check if any of the members are methods with the specified name
        for name, member in members:
            print(name)
            if name == method_name:
                return member

        return None

    def load_module_from_file(file_path):
        # Load the module from the file path
        spec = importlib.util.spec_from_file_location("module_name", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
    
    file_path = file_map[file_name]
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    if method_name is None:
        # Print the whole file content
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)
    else:
        files = os.listdir("./modules")
        for f in files:
        # Check if the file is a Python file
            if f.endswith(".py") and f == file_name:
                
                file_path = os.path.join("modules", f)
                m = load_module_from_file(file_path)
                
                func = find_function(m , method_name)
                if func != None:
                    source_lines, _ = inspect.getsourcelines(func)
                    for line in source_lines:
                        print(line)
                else:
                    print("Error")

file_name = 'adders.py'
method_name = None

# NOT WORKING FOR addition_checkEncode.py functions

print_content(file_name, method_name)
