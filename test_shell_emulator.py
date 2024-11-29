import zipfile
import os
from PyQt5.QtWidgets import QApplication
import sys
from shell_emulator import ShellEmulator

# Создаём тестовый ZIP-файл
def setup_test_zip():
    test_zip_path = "test_vfs.zip"
    with zipfile.ZipFile(test_zip_path, 'w') as zipf:
        zipf.writestr("dir1/file1.txt", "File 1 content")
        zipf.writestr("dir1/file2.txt", "File 2 content")
        zipf.writestr("dir2/file3.txt", "File 3 content")
        zipf.writestr("dir2/subdir1/file4.txt", "File 4 content")
    return test_zip_path

# Удаляем тестовый ZIP-файл
def cleanup_test_zip(zip_path):
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except PermissionError:
            print(f"Failed to delete {zip_path}. File might be open.")

# Инициализация эмулятора
def init_emulator(zip_path):
    config = {
        'username': 'test_user',
        'hostname': 'test_shell',
        'vfs_path': zip_path,
        'startup_script': None
    }
    return ShellEmulator(config)

# Тесты для команды ls
def test_ls():
    zip_path = setup_test_zip()  # Создаём свежий архив
    shell = init_emulator(zip_path)
    print("\nRunning test_ls...")

    try:
        # Тест 1: ls в корневом каталоге
        result = shell.ls()
        assert "dir1" in result and "dir2" in result, "Test 1 failed: ls in root"

        # Тест 2: ls в подкаталоге
        shell.current_dir = "dir1"
        result = shell.ls()
        assert "file1.txt" in result and "file2.txt" in result, "Test 2 failed: ls in dir1"

        print("test_ls passed!")
    finally:
        shell.zip_file.close()
        cleanup_test_zip(zip_path)

# Тесты для команды cd
def test_cd():
    zip_path = setup_test_zip()  # Создаём свежий архив
    shell = init_emulator(zip_path)
    print("\nRunning test_cd...")

    try:
        # Тест 1: cd в существующую директорию
        result = shell.cd("dir1")
        assert shell.current_dir == "dir1", "Test 1 failed: cd into dir1"

        # Тест 2: cd в несуществующую директорию
        result = shell.cd("nonexistent_dir")
        assert "cd: no such file or directory" in result, "Test 2 failed: cd into nonexistent_dir"

        print("test_cd passed!")
    finally:
        shell.zip_file.close()
        cleanup_test_zip(zip_path)

# Тесты для команды rmdir
def test_rmdir():
    zip_path = setup_test_zip()  # Создаём свежий архив
    shell = init_emulator(zip_path)
    print("\nRunning test_rmdir...")

    try:
        # Тест 1: rmdir пустой директории
        shell.empty_dirs.append("empty_dir/")  # Добавляем пустую директорию в эмулятор
        print(f"Empty directories: {shell.empty_dirs}")  # Отладочный вывод
        result = shell.rmdir("empty_dir")
        print(f"Result of rmdir: {result}")  # Отладочный вывод
        assert "Removed directory and its contents" in result, f"Test 1 failed: rmdir empty directory, got {result}"

        # Тест 2: rmdir непустой директории
        result = shell.rmdir("dir1")
        print(f"Result of rmdir for dir1: {result}")  # Отладочный вывод
        assert "Removed directory and its contents" in result, f"Test 2 failed: rmdir non-empty directory, got {result}"

        print("test_rmdir passed!")
    finally:
        shell.zip_file.close()
        cleanup_test_zip(zip_path)

# Тесты для команды tac
def test_tac():
    zip_path = setup_test_zip()  # Создаём свежий архив
    shell = init_emulator(zip_path)
    print("\nRunning test_tac...")

    try:
        print(f"Files in ZIP: {shell.zip_file.namelist()}")  # Отладочный вывод
        result = shell.tac("dir1/file1.txt")
        expected = "File 1 content"[::-1]  # Перевёрнутое содержимое файла
        assert result == expected, f"Test 1 failed: tac for dir1/file1.txt, expected {expected}, got {result}"

        # Тест 2: tac для несуществующего файла
        result = shell.tac("nonexistent.txt")
        assert "tac: no such file" in result, "Test 2 failed: tac for nonexistent.txt"

        print("test_tac passed!")
    finally:
        shell.zip_file.close()
        cleanup_test_zip(zip_path)

# Запуск тестов
if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        test_ls()
        test_cd()
        test_rmdir()
        test_tac()
    finally:
        print("\nAll tests completed!")
        app.quit()
