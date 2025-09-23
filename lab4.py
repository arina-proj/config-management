import argparse
import getpass
import os
from pathlib import Path
from typing import Dict, List, Optional

class VFSNode:
    def __init__(self, vfs_name: str, is_directory: bool=False, parent: Optional["VFSNode"] = None): 
        self.vfs_name = vfs_name
        self.is_directory = is_directory
        self.children: Dict[str, 'VFSNode'] = {}
        self.parent = parent
        self.content : Optional[bytes] = None # либо типа bytes либо None - по умолчанию

    def remove_child(self, child_name: str) -> bool:
        if child_name in self.children:
            del self.children[child_name]
            return True
        return False


    def add_child(self, child: 'VFSNode'):
        self.children[child.vfs_name] =child
        child.parent = self

    def get_path(self) -> str:
        path_parts=[]
        current = self
        while(current and current.vfs_name):
            path_parts.append(current.vfs_name)
            current = current.parent
        return '/' + '/'.join(reversed(path_parts)) if path_parts else '/'
        
class VFS:
    def __init__(self):
        self.root = VFSNode('', is_directory=True)
        self.loaded = False #загружена ли директория с диска
        self.current_dir = self.root

    def find_node(self, path):
        if path.startswith('/'):
            current = self.root
            path_parts = path[1:].split('/')
        else:
            current = self.current_dir
            path_parts = path.split('/')
        
        # Убираем пустые части (если путь заканчивается на /)
        path_parts = [part for part in path_parts if part]
        
        for part in path_parts:
            if part == '..':
                if current.parent:
                    current = current.parent
            elif part == '.':
                continue
            elif part in current.children:
                current = current.children[part]
            else:
                return None
        
        return current

    def load_from_disk(self, disk_path: str):
        path_obj = Path(disk_path)
        if(not path_obj.exists()):
            print("Путь не найден")
            return False
        if(not path_obj.is_dir()):
            print("Путь не является директорией")
            return False
        try:
            self.build_vfs_tree(self.root, path_obj)
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
                    dir_node = VFSNode(item.name, is_directory=True, parent = vfs_node)
                    vfs_node.add_child(dir_node)
                    self.build_vfs_tree(dir_node, item)
                else:
                    with open(item, "rb") as file:
                        content = file.read()
                    file_node = VFSNode(item.name, is_directory=False, parent= vfs_node)
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
        current_path = self.vfs.current_dir.get_path()
        print(f"\n{self.vfs_name}:{current_path}$ ", end="")
    
    def parse_input(self, user_input):
        input_line = user_input.strip() #убираем лишние знаки табуляции в начале и конце строки
        if not input_line or input_line[0]=="#": return None, []
        parts = input_line.split()
        command = parts[0]
        args = parts[1:] if len(parts)>1 else []
        return command, args
        
    def cmd_ls(self, args=None):
        if args:
            # Обработка аргументов (путей к файлам/директориям)
            for arg in args:
                target_node = self.vfs.find_node(arg)
                if not target_node:
                    print(f"ls: {arg}: No such file or directory")
                elif target_node.is_directory:
                    # Показать содержимое директории
                    if not target_node.children:
                        print(f"Директория '{arg}' пуста")
                    else:
                        for name, node in sorted(target_node.children.items()):
                            file_type = "d" if node.is_directory else "f"
                            print(f"{file_type} {name}")
                else:
                    # Показать только этот файл
                    print(f"f {arg}")
        else:
            # Базовый случай - показать текущую директорию
            target_dir = self.vfs.current_dir
            if not target_dir.children:
                print("Директория пуста")
            else:
                for name, node in sorted(target_dir.children.items()):
                    file_type = "d" if node.is_directory else "f"
                    print(f"{file_type} {name}")

    def cmd_cd(self, args):
        if not args:
            self.vfs.current_dir = self.vfs.root
            return
        
        if len(args) > 1:
            print("cd: слишком много аргументов")
            print("использование: cd [директория]")
            return
    
        target_path = args[0]

        if target_path == "..":
            if self.vfs.current_dir.parent:
                self.vfs.current_dir = self.vfs.current_dir.parent
            else:
                print("cd: уже в корневой директории") 
            return
        
        if target_path == "/":
            self.vfs.current_dir = self.vfs.root
            return
        
        if target_path in self.vfs.current_dir.children:
            target_node = self.vfs.current_dir.children[target_path]
            if target_node.is_directory:
                self.vfs.current_dir = target_node
            else:
                print(f"cd: {target_path}: не является директорией")
        else:
            print(f"cd: {target_path}: директория не найдена")

    def cmd_exit(self, args):
        print(f"Команда: exit")
        print(f"Аргументы: {args}")
        print("Завершение работы VFS")
        self.running = False
    
    def cmd_pwd(self):
        print(self.vfs.current_dir.get_path())

    def cmd_whoami(self):
        print(getpass.getuser()) #встроенная функция, возвращает имя текущего пользователя системы

    def cmd_uniq(self, args):
        if not args:
            print("uniq: требуется указать файл")
            return
        filename = args[0]
        if filename in self.vfs.current_dir.children:
            file_node = self.vfs.current_dir.children[filename]
            if not file_node.is_directory and file_node.content:
                try:
                    content = file_node.content.decode('utf-8')  # преобразуем байты в текст
                    lines = content.split('\n') 
                    unique_lines = [] #для хранения уник строк с сохранением порядка
                    seen_lines = set() #для быстрого поиска
                    for line in lines:
                        if line.strip() not in seen_lines:
                            unique_lines.append(line)
                            seen_lines.add(line.strip())
                    for line in unique_lines:
                        print(line)
                except UnicodeDecodeError: #когда файл не является текстовым в кодировке UTF-8
                    print(f"uniq: {filename}: не текстовый файл")
            else:
                print(f"uniq: {filename}: не файл или файл пуст")
        else:
            print(f"uniq: {filename}: файл не найден")

    def cmd_rm(self, args):
        if not args:
            print("rm: требуется указать файл или директорию")
            return
        
        recursive = False 
        targets = []
        
        for arg in args: #проверяем флаги
            if arg == '-r' or arg == '-R':
                recursive = True
            else:
                targets.append(arg)
        
        if not targets:
            print("rm: требуется указать файл или директорию")
            return
        
        for target in targets:
            if self.vfs.find_node(target):
                target_node = self.vfs.find_node(target)
                
                if target_node.is_directory:
                    if not recursive:
                        print(f"rm: {target}: является директорией (используйте -r для рекурсивного удаления)")
                        continue
                    
                    # Рекурсивное удаление директории
                    if not self.remove_directory(target_node):
                        print(f"rm: не удалось удалить директорию '{target}'")
                        continue
                
                # Удаление файла или уже очищенной директории
                parent = target_node.parent
                if parent and parent.remove_child(target_node.vfs_name):
                    print(f"Удалено: {target}")
                else:
                    print(f"rm: не удалось удалить '{target}'")
            else:
                print(f"rm: {target}: файл или директория не найдена")

    def remove_directory(self, dir_node: VFSNode) -> bool:
        try:
            for child_name, child_node in list(dir_node.children.items()):
                if child_node.is_directory:
                    if not self.remove_directory(child_node):
                        return False
                if not dir_node.remove_child(child_name):
                    return False
            return True 
        except Exception as e:
            print(f"Ошибка при удалении директории: {e}")
            return False

    def handle_command(self, command, args):
        if command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command == "pwd":
            self.cmd_pwd()
        elif command == "uniq":
            self.cmd_uniq(args)
        elif command == "whoami":
            self.cmd_whoami()
        elif command == "exit":
            self.cmd_exit(args)
        elif command == "rm":
            self.cmd_rm(args)   
        else:
            print(f"{command}: команда не найдена")
    
    

    def run_start_script(self):
        if self.start_script and os.path.exists(self.start_script):
            try:
                print(f"Выполнение стартового скрипта: {self.start_script}")
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



# python3 lab4.py --path . --prompt myVFS --script test_for_lab4.txt - запуск