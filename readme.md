# Shell Emulator

### Описание

**Shell Emulator** – это эмулятор командной строки UNIX-подобной операционной системы. Эмулятор работает с виртуальной файловой системой, основанной на ZIP-архиве, и поддерживает выполнение основных команд.

Эмулятор включает графический интерфейс (GUI), который имитирует взаимодействие с оболочкой (shell), и тестовый набор, проверяющий корректность работы всех функций.

---

### Возможности

Поддерживаемые команды:
- `ls` – отображение содержимого текущей директории.
- `cd` – переход между директориями.
- `rmdir` – удаление директорий (пустых и непустых).
- `tac` – вывод содержимого файла в обратном порядке.
- `exit` – завершение работы эмулятора.

---

### Запуск эмулятора
Для запуска эмулятора выполните:
```bash
python shell_emulator.py
```
Примечание: Перед запуском создайте файл config.yaml со следующей структурой:
```yaml
username: your_username
hostname: your_hostname
vfs_path: path_to_zip_file
startup_script: path_to_startup_script (optional)
```
Пример файла config.yaml:
```yaml
username: test_user
hostname: test_shell
vfs_path: test_vfs.zip
startup_script: null
```
Тестирование
Для запуска тестов выполните:
```bash
python test_shell_emulator.py
```
Каждый тест создаёт виртуальный ZIP-архив, использует его для проверки корректности команд (ls, cd, rmdir, tac) и удаляет его после завершения.
Структура проекта
shell_emulator.py – основной файл, реализующий GUI и команды эмулятора.
test_shell_emulator.py – файл с тестами для всех поддерживаемых команд.
config.yaml – конфигурационный файл, задающий параметры эмулятора.
requirements.txt – зависимости для установки.
Пример работы
Запуск команд
```plaintext
test_user@test_shell:/$ ls
dir1
dir2
test_user@test_shell:/$ cd dir1
test_user@test_shell:/dir1$ ls
file1.txt
file2.txt
test_user@test_shell:/dir1$ tac file1.txt
tnetnoC 1 eliF
test_user@test_shell:/dir1$ cd ..
test_user@test_shell:/$ rmdir dir1
Removed directory and its contents: dir1
```
![Скриншот тестов](photo/Снимок%20экрана%202024-11-29%20160216.png)