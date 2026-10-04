# TaskMaster CLI - Console To-Do List Manager

**Task 2 – Python Developer Internship (Elevate Labs)**
Key concepts: **File Handling, Lists, String Manipulation**

A persistent, colourful command-line to-do app written in pure Python (no external libraries).
Tasks are stored in a plain text file (`tasks.txt`) using `open()` and the `with` statement, so they survive restarts.

## Features
- Add, view, edit, remove and complete tasks
- Priority (High / Medium / Low), category and due date
- Overdue / due-today highlighting with days remaining
- Search by keyword or category; filter and sort (priority, due date, A-Z)
- Progress bar and statistics dashboard
- Undo last change, clear completed tasks, export to CSV
- Input validation, duplicate warning, graceful handling of a missing file

## Run
```bash
python todo.py
```
Requires Python 3.8+. Works on Windows, macOS and Linux (VS Code terminal or any terminal).
Set `NO_COLOR=1` to disable colours.

## Storage format (`tasks.txt`)
One task per line: `done|priority|due|category|title`
```
0|High|2026-10-10|Study|Complete Python internship Task 2
1|Low||Home|Create a new GitHub repository
```
Plain lines (just a title) are also accepted.

## Concepts used
| Concept | Where |
|---|---|
| Lists | `tasks` list of dictionaries; `append`, `pop`, slicing, list comprehensions |
| File handling | `open()` with `r` / `w` modes, `with`, loop line by line, `FileNotFoundError` |
| String manipulation | `.strip()`, `.split()`, `.join()`, `.replace()`, `.lower()`, f-strings |

## Interview questions - quick answers
1. **Open/write a file:** `with open("f.txt", "w") as f: f.write("text")`
2. **File modes:** `r` read, `w` write (overwrite), `a` append, `r+` read/write, `b` binary
3. **`.strip()`:** removes leading/trailing whitespace (incl. `\n`)
4. **Lists:** ordered, mutable, indexed collections
5. **append vs insert:** `append(x)` adds at the end; `insert(i, x)` adds at index `i`
6. **Remove elements:** `remove(value)`, `pop(index)`, `del lst[i]`, `clear()`
7. **Context manager:** `with` auto-closes the file, even if an error occurs
8. **Loop a file:** `for line in f:`
9. **Data structure:** a way of organising data (list, tuple, dict, set...)
10. **File doesn't exist:** `r` mode raises `FileNotFoundError`; `w`/`a` create it. This app catches the error and starts with an empty list.
