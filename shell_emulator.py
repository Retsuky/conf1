import zipfile
import yaml
import tempfile
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget

class ShellEmulator(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.username = config['username']
        self.hostname = config['hostname']
        self.vfs_path = config['vfs_path']
        self.startup_script = config['startup_script']

        # Current working directory in the virtual filesystem
        self.current_dir = ""
        self.zip_file = zipfile.ZipFile(self.vfs_path, 'r')
        self.empty_dirs = []  # Список для пустых директорий

        # GUI setup
        self.initUI()

        # Execute startup script
        self.run_startup_script()

    def initUI(self):
        self.setWindowTitle("Shell Emulator")
        self.setGeometry(100, 100, 800, 600)

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        self.input_line = QLineEdit(self)
        self.input_line.returnPressed.connect(self.process_command)

        layout = QVBoxLayout()
        layout.addWidget(self.output_area)
        layout.addWidget(self.input_line)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_startup_script(self):
        if self.startup_script:
            try:
                with open(self.startup_script, 'r') as f:
                    commands = f.readlines()
                    for command in commands:
                        self.execute_command(command.strip())
            except FileNotFoundError:
                self.output_area.append(f"Startup script '{self.startup_script}' not found.")

    def process_command(self):
        command = self.input_line.text().strip()
        self.input_line.clear()
        self.execute_command(command)

    def execute_command(self, command):
        # Отображаем строку приглашения и команду
        prompt = f"{self.username}@{self.hostname}:/{self.current_dir}$ {command}"
        self.output_area.append(prompt)

        # Проверяем и выполняем команду
        if command.startswith("ls"):
            result = self.ls()
            self.output_area.append(result)
        elif command.startswith("cd"):
            path = command.split(" ", 1)[1] if " " in command else ""
            result = self.cd(path)
            self.output_area.append(result)
        elif command.startswith("exit"):
            self.close()
        elif command.startswith("rmdir"):
            path = command.split(" ", 1)[1] if " " in command else ""
            result = self.rmdir(path)
            self.output_area.append(result)
        elif command.startswith("tac"):
            path = command.split(" ", 1)[1] if " " in command else ""
            result = self.tac(path)
            self.output_area.append(result)
        else:
            self.output_area.append(f"Command not found: {command}")

    def ls(self):
        directory = self.current_dir.strip("/")
        if directory:
            directory += "/"

        items = set()

        # Добавляем содержимое ZIP-файла
        for name in self.zip_file.namelist():
            if name.startswith(directory) and name != directory:
                relative_path = name[len(directory):].split('/')[0]
                if relative_path:
                    items.add(relative_path)

        # Добавляем пустые директории
        for empty_dir in self.empty_dirs:
            if empty_dir.startswith(directory) and empty_dir != directory:
                relative_path = empty_dir[len(directory):].split('/')[0]
                if relative_path:
                    items.add(relative_path)

        if items:
            return "\n".join(sorted(items))
        else:
            return "ls: no such file or directory"

    def cd(self, path):
        if path == "..":
            self.current_dir = "/".join(self.current_dir.split("/")[:-1])
            return f"Moved to directory: {self.current_dir}"
        elif path == "." or not path:
            return "cd: no operation"
        else:
            potential_dir = f"{self.current_dir}/{path}".strip("/")
            if any(name.startswith(potential_dir + "/") for name in self.zip_file.namelist()) or potential_dir + "/" in self.empty_dirs:
                self.current_dir = potential_dir
                return f"Changed directory to {self.current_dir}"
            else:
                return f"cd: no such file or directory: {path}"

    def rmdir(self, path):
        target_dir = f"{self.current_dir}/{path}".strip("/") + "/"

        # Проверяем, существует ли директория
        if not any(name.startswith(target_dir) for name in self.zip_file.namelist()) and target_dir not in self.empty_dirs:
            return f"rmdir: no such directory: {path}"

        try:
            # Создаём временный ZIP-файл
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_zip_path = temp_file.name

            # Создаём новый архив без файлов из удаляемой директории
            with zipfile.ZipFile(temp_zip_path, 'w') as new_zip:
                for name in self.zip_file.namelist():
                    if not name.startswith(target_dir):  # Исключаем содержимое удаляемой директории
                        with self.zip_file.open(name) as file:
                            new_zip.writestr(name, file.read())

            # Удаляем пустую директорию, если она есть в списке empty_dirs
            if target_dir in self.empty_dirs:
                self.empty_dirs.remove(target_dir)

            # Заменяем старый ZIP новым
            self.zip_file.close()
            shutil.move(temp_zip_path, self.vfs_path)
            self.zip_file = zipfile.ZipFile(self.vfs_path, 'r')

            return f"Removed directory and its contents: {path}"
        except Exception as e:
            return f"rmdir: failed to remove '{path}': {e}"

    def tac(self, path):
        target_file = f"{self.current_dir}/{path}".strip("/")
        try:
            with self.zip_file.open(target_file) as file:
                content = file.read()
                reversed_content = content[::-1].decode('utf-8')
                return reversed_content
        except KeyError:
            return f"tac: no such file: {target_file}"
        except UnicodeDecodeError:
            return f"tac: error decoding file {path}: invalid UTF-8 content"
        except Exception as e:
            return f"tac: error reading file {path}: {e}"

if __name__ == "__main__":
    import sys
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    app = QApplication(sys.argv)
    shell = ShellEmulator(config)
    shell.show()
    sys.exit(app.exec_())
