class VFSRepl:
    def __init__(self, vfs_name="myVFS"):
        self.vfs_name = vfs_name
        self.current_dir = "/"
        self.running = True #готовность к работе
    
    def print_prompt(self):
        print(f"{self.vfs_name}")
    
    def parse_input(self, user_input):
        input_line = user_input.strip() #убираем лишние знаки табуляции в начале и конце строки
        if not input_line: return None, []
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
    
    def run(self):
        while self.running: 
            try:
                self.print_prompt()
                user_input = input()
                command, args = self.parse_input(user_input)
                
                if command:
                    self.handle_command(command, args)
            except Exception as e:
                print(f"Ошибка: {e}. Продолжаем работу")

def main():
    vfs = VFSRepl("myVFS")
    vfs.run()

if __name__ == "__main__":
    main()




