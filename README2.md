1. Общее описание 
VFSRepl теперь включает полноценную виртуальную файловую систему, которая загружает структуру директорий с физического диска в память. Система поддерживает работу с реальной файловой структурой без модификации исходных данных.

Новые возможности третьего этапа:
    Загрузка структуры директорий с диска в оперативную память
    Рекурсивное построение дерева VFS
    Обработка ошибок загрузки VFS
    Поддержка файлов и папок любого уровня вложенности

2. Описание всех функций и настроек 

Новый класс VFSNode - представляет узел в виртуальной файловой системе:
    Конструктор __init__(self, vfs_name: str, is_directory: bool=False):
        vfs_name - имя узла (файла или директории)
        is_directory - флаг, указывающий является ли узел директорией
        children - словарь дочерних узлов
        parent - ссылка на родительский узел
Методы VFSNode:
    add_child(self, child: 'VFSRepl') - добавляет дочерний узел
    get_path(self) -> str - возвращает полный путь к узлу   


Новый класс VFS - управляет всей виртуальной файловой системой:
    Конструктор __init__(self):
        Создает корневой узел с пустым именем
        Устанавливает флаг loaded в False
Методы VFS:
    load_from_disk(self, disk_path: str) -> bool - загружает VFS с диска:
        Проверяет существование пути
        Проверяет, что путь является директорией
        Вызывает построение дерева VFS
        Устанавливает флаг loaded при успешной загрузке
    build_vfs_tree(self, vfs_node: VFSNode, disk_path: Path) - рекурсивно строит дерево VFS:
        Обходит все элементы в директории
        Для директорий: создает узлы и рекурсивно обрабатывает содержимое
        Для файлов: читает содержимое и создает файловые узлы
        Обрабатывает исключения при доступе к файловой системе


Обновленный класс VFSRepl
Изменения в конструкторе:
    Обновлен экземпляр класса VFS
    Автоматическая загрузка VFS при указании пути
Улучшенный метод run_start_script(self):
    Добавлена проверка существования файла скрипта
Улучшена обработка ошибок выполнения скрипта

3. Описание команд для сборки проекта и запуска тестов 
Тестовые структуры директорий
Создание тестовых структур для VFS:
    Минимальная структура (1 уровень):
        mkdir -p test_vfs_minimal
        echo "file1 content" > test_vfs_minimal/file1.txt
        echo "file2 content" > test_vfs_minimal/file2.txt
    Структура с несколькими файлами (2 уровня):
        mkdir -p test_vfs_medium/{dir1,dir2}
        echo "content1" > test_vfs_medium/dir1/file1.txt
        echo "content2" > test_vfs_medium/dir1/file2.txt
        echo "content3" > test_vfs_medium/dir2/file3.txt
    Сложная структура (3+ уровня):
        mkdir -p test_vfs_complex/{home/{user/documents,admin/config},var/log/{apache,mysql}}
        echo "doc1" > test_vfs_complex/home/user/documents/doc1.txt
        echo "doc2" > test_vfs_complex/home/user/documents/doc2.txt
        echo "config" > test_vfs_complex/home/admin/config/settings.conf
        echo "log1" > test_vfs_complex/var/log/apache/access.log
        echo "log2" > test_vfs_complex/var/log/mysql/error.log

Тестовые скрипты
Скрипт 1(тестирование загрузки VFS)
    text
    # Тестирование базовой функциональности VFS
    ls
    cd home
    ls
    cd user
    ls
    cd /var/log
    ls
    cd /nonexistent
    ls
Скрипт 2(тестирование обработки ошибок)
    text
    # Тестирование ошибок загрузки VFS
    ls -la
    cd invalid_path
    ls /nonexistent
    cd /home/user/documents
    ls -l
Скрипт 3(комплексное тестирование)
    text
    # Комплексный тест всех функций
    ls
    cd home
    ls -la
    cd user/documents
    ls
    cd ../..
    cd /var
    ls
    cd log/apache
    ls
    cd /
    exit

Команды для запуска тестов
Тестирование с минимальной VFS:
    python vfs_repl.py --path test_vfs_minimal --script test_vfs_basic.txt
Тестирование со сложной структурой:
    python vfs_repl.py --path test_vfs_complex --prompt "ComplexVFS" --script test_comprehensive.txt
Тестирование с реальной директорией:
    python vfs_repl.py --path /tmp --prompt "TempVFS" --script test_vfs_basic.txt

4. Примеры использования 
![alt text](image-3.png)