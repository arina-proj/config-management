import argparse
import os


class VFSRepl:
    def __init__(self, vfs_name="myVFS", path=None, start_script=None):
        self.vfs_name = vfs_name
        self.path = path
        self.start_script = start_script 
        self.running = True #готовность к работе

        #отладочный вывод всех заданных параметров при запуске эмулятора
        print(f"\nКонфигурация VFS")
        print(f"Имя VFS: {vfs_name}")
        print(f"Физический путь: {path}")
        print(f"Стартовый скрипт: {start_script or 'Не указан'}")
        
    
    def print_prompt(self):
        print(f"\n{self.vfs_name} $", end="")
    
    def parse_input(self, user_input):
        input_line = user_input.strip() #убираем лишние знаки табуляции в начале и конце строки
        if not input_line or input_line[0]=="#": return None, []
        parts = input_line.split()
        command = parts[0]
        args = parts[1:] if len(parts)>1 else []
        return command, args
    
    def run_start_script(self):
        if not self.start_script:
            print("Стартовый скрипт не указан!")
            return
        with open(self.start_script, "r") as start_script:
            lines = start_script.readlines()
            for line in lines:
                command, args = self.parse_input(line)
                if command: 
                    print(f"\n{self.vfs_name}$ {line}", end="")
                    try: self.handle_command(command, args)
                    except Exception as e:
                        print(f"Ошибка в строке: {e}")
                        continue
        
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



