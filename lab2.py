import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional

class VFSNode:
    def __init__(self, vfs_name: str, is_directory: bool=False): 
        self.vfs_name = vfs_name
        self.is_directory = is_directory
        self.children: Dict[str, 'VFSRepl'] = {}
    def add_child(self, child: 'VFSRepl'):
        self.children[child.vfs_name] =child
    def get_path(self) -> str:
        path_parts=[]
        current = self
        while(current and current.vfs_name):
            path_parts.append(current.vfs_name)
            current = current.parent
        return '/' + '/'.join(reversed(path_parts))
        
class VFS:
    def __init__(self):
        self.root = VFSNode('', is_directory=True)
        self.loaded = False #загружена ли директория с диска

    def load_from_disk(self, disk_path: str):
        path_obj = Path(disk_path)
        if(not path_obj.exists()):
            print("Путь не найден")
            return False
        if(not path_obj.is_dir()):
            print("Путь не является директорией")
            return False
        try:
            self._build_vfs_tree(self.root, path_obj)
            self.loaded = True
            print(f"VFS успешно загружена из '{disk_path}'")
            return True
        except Exception as error:
            print("Ошибка - "+ error)
            return False
  
    def build_vfs_tree(self, vfs_node: VFSNode, disk_path: Path):
        try:
            for item in disk_path.iterdir():
                if item.is_dir():
                    dir_node = VFSNode(item.name, is_directory=True)
                    vfs_node.add_child(dir_node)
                    self.build_vfs_tree(dir_node, item)
                else:
                    with open(item, "rb") as file:
                        content = file.read()
                    file_node = VFSNode(item.name, is_directory=False)
                    vfs_node.add_child(file_node)
        except Exception as error:
            print("Ошибка - " + error)

class VFSRepl:

    def __init__(self, vfs_name='myVFS', path=None, start_script=None):
        self.vfs_name = vfs_name
        self.path = path
        self.start_script = start_script
        self.running = True
        self.vfs = VFS()
        
        print(f"\nКонфигурация VFS")
        print(f"Имя VFS: {vfs_name}")
        print(f"Физический путь: {path}")
        print(f"Стартовый скрипт: {start_script or 'Не указан'}")

        if path:
            self.vfs.load_from_disk(path)
    
    def print_prompt(self):
        print(f"\n{self.vfs_name} $", end="")
    
    def parse_input(self, user_input):
        input_line = user_input.strip() #убираем лишние знаки табуляции в начале и конце строки
        if not input_line or input_line[0]=="#": return None, []
        parts = input_line.split()
        command = parts[0]
        args = parts[1:] if len(parts)>1 else []
        return command, args
        
    def cmd_ls(self, args):
        print(f"ls: {args}")

    def cmd_cd(self, args):
        print(f"cd: {args}")

    def cmd_exit(self, args):
        print(f"Команда: exit")
        print(f"Аргументы: {args}")
        print("Завершение работы VFS")
        self.running = False
    
    def handle_command(self, command, args):
        if command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command == "exit":
            self.cmd_exit(args)
        else:
            print(f"{command}: команда не найдена")
    
    def run_start_script(self):
        if self.start_script and os.path.exists(self.start_script):
            try:
                with open(self.start_script, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            command, args = self.parse_input(line)
                            if command:
                                self.handle_command(command, args)
            except Exception as e:
                print(f"Ошибка выполнения стартового скрипта: {e}")

    def run(self):
        self.run_start_script()
        while self.running: 
            try:
                self.print_prompt()
                user_input = input()
                command, args = self.parse_input(user_input)
                
                if command:
                    self.handle_command(command, args)
            except Exception as e:
                print(f"Ошибка: {e}. Продолжаем работу")

def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--path', help='Путь к физическому расположению VFS', default=os.getcwd())
        parser.add_argument('--prompt', help='Пользовательское приглашение к вводу', default='myVFS')
        parser.add_argument('--script', help='Путь к стартовому скрипту')
        return parser.parse_args()

def main():
    args = parse_args()
    
    vfs = VFSRepl(vfs_name=args.prompt, 
                 path=args.path,
                 start_script=args.script)
    
    vfs.run()

if __name__ == "__main__":
    main()



