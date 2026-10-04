#!/usr/bin/env python3
"""
TaskMaster CLI - a persistent, colourful console To-Do List Manager.

Task 2 - Python Developer Internship (Elevate Labs)
Key concepts: File Handling, Lists, String Manipulation

Features
--------
* Add / View / Edit / Remove / Complete tasks
* Priority (High / Medium / Low), category and due date
* Overdue + due-today highlighting
* Search, filter and sort
* Progress bar and statistics
* Undo last change, clear completed, export to CSV
* Persistent storage in a plain text file (tasks.txt) using open()
* Safe handling of a missing / corrupted file
"""

import csv
import os
import sys
from datetime import date, datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.txt")
EXPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks_export.csv")
DELIM = "|"
PRIORITIES = {"H": "High", "M": "Medium", "L": "Low"}
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# --------------------------------------------------------------------------
# Terminal styling (ANSI). Falls back to plain text if colours unsupported.
# --------------------------------------------------------------------------
if os.name == "nt":
    os.system("")  # enables ANSI escape codes in Windows terminals

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def c(text, code):
    """Wrap text in an ANSI colour code."""
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else str(text)


def bold(t): return c(t, "1")
def dim(t): return c(t, "2")
def red(t): return c(t, "91")
def green(t): return c(t, "92")
def yellow(t): return c(t, "93")
def blue(t): return c(t, "94")
def magenta(t): return c(t, "95")
def cyan(t): return c(t, "96")


def strip_ansi_len(text):
    """Visible length of a string (ignores colour codes)."""
    out, skip = 0, False
    for ch in str(text):
        if ch == "\033":
            skip = True
        elif skip and ch == "m":
            skip = False
        elif not skip:
            out += 1
    return out


def pad(text, width):
    return str(text) + " " * max(0, width - strip_ansi_len(text))


# --------------------------------------------------------------------------
# Task model + file handling
# --------------------------------------------------------------------------
def clean(text):
    """String manipulation: trim whitespace and remove the delimiter."""
    return " ".join(text.replace(DELIM, "/").split())


def make_task(title, priority="Medium", due="", category="General", done=False):
    return {
        "title": clean(title),
        "priority": priority,
        "due": due,
        "category": clean(category) or "General",
        "done": done,
    }


def parse_line(line):
    """Turn one text-file line into a task dict. Supports plain-text lines too."""
    line = line.strip()
    if not line:
        return None
    parts = line.split(DELIM)
    if len(parts) == 5:
        done, pr, due, cat, title = (p.strip() for p in parts)
        pr = pr if pr in PRIORITY_ORDER else "Medium"
        if due and not valid_date(due):
            due = ""
        return make_task(title, pr, due, cat, done == "1")
    return make_task(line)  # old / simple format: just a title


def load_tasks():
    """Read tasks from the file. Missing file -> empty list (no crash)."""
    tasks = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:  # loop through file line by line
                task = parse_line(line)
                if task and task["title"]:
                    tasks.append(task)
    except FileNotFoundError:
        pass  # first run - file will be created on first save
    except OSError as err:
        print(red(f"Could not read {DATA_FILE}: {err}"))
    return tasks


def save_tasks(tasks):
    """Write all tasks to the file (write to temp file first, then replace)."""
    tmp = DATA_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            for t in tasks:
                f.write(DELIM.join([
                    "1" if t["done"] else "0",
                    t["priority"], t["due"], t["category"], t["title"],
                ]) + "\n")
        os.replace(tmp, DATA_FILE)
    except OSError as err:
        print(red(f"Could not save tasks: {err}"))


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def valid_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def days_left(due):
    if not due:
        return None
    return (datetime.strptime(due, "%Y-%m-%d").date() - date.today()).days


def ask(prompt, default=None):
    """input() wrapper that handles Ctrl+C / Ctrl+D gracefully."""
    try:
        value = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(goodbye())
    return value if value or default is None else default


def ask_priority(default="Medium"):
    while True:
        v = ask(f"  Priority [H]igh / [M]edium / [L]ow (Enter = {default}): ").upper()
        if not v:
            return default
        if v[0] in PRIORITIES:
            return PRIORITIES[v[0]]
        print(red("  Please type H, M or L."))


def ask_due(default=""):
    while True:
        v = ask("  Due date YYYY-MM-DD (Enter = none, 't' = today, '+3' = in 3 days): ")
        if not v:
            return default
        if v.lower() == "t":
            return date.today().isoformat()
        if v.startswith("+") and v[1:].isdigit():
            return date.fromordinal(date.today().toordinal() + int(v[1:])).isoformat()
        if valid_date(v):
            return v
        print(red("  Invalid date. Example: 2026-12-31"))


def ask_index(tasks, action):
    """Ask for a task number (1-based) and validate it."""
    if not tasks:
        print(yellow("  No tasks yet."))
        return None
    raw = ask(f"  Task number to {action} (Enter to cancel): ")
    if not raw:
        return None
    if not raw.isdigit() or not 1 <= int(raw) <= len(tasks):
        print(red(f"  Enter a number between 1 and {len(tasks)}."))
        return None
    return int(raw) - 1


def pause():
    ask(dim("\n  Press Enter to continue..."))


# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------
def banner():
    line = "═" * 62
    print(cyan(f"╔{line}╗"))
    print(cyan("║") + bold(magenta(pad("   ✔  TASKMASTER CLI  -  Persistent To-Do List Manager", 62))) + cyan("║"))
    print(cyan(f"╚{line}╝"))


def progress_bar(done, total, width=30):
    ratio = done / total if total else 0
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    color = green if ratio >= 0.7 else yellow if ratio >= 0.4 else red
    return f"{color(bar)} {int(ratio * 100)}%  ({done}/{total} done)"


def due_label(t):
    if not t["due"]:
        return dim("—")
    left = days_left(t["due"])
    if t["done"]:
        return dim(t["due"])
    if left < 0:
        return red(f"{t['due']} (overdue {-left}d)")
    if left == 0:
        return yellow(f"{t['due']} (today!)")
    if left <= 2:
        return yellow(f"{t['due']} ({left}d)")
    return f"{t['due']} ({left}d)"


def priority_label(p):
    return {"High": red("▲ High"), "Medium": yellow("■ Medium"), "Low": green("▼ Low")}[p]


def show_tasks(tasks, rows=None, title="YOUR TASKS"):
    """Print a formatted table. `rows` is a list of (original_index, task)."""
    if rows is None:
        rows = list(enumerate(tasks))
    print()
    print(bold(f"  {title}"))
    if not rows:
        print(yellow("\n  📭 Nothing to show. Add a task with option 2!\n"))
        return
    w = (4, 5, 32, 14, 10, 28)
    head = ["#", "Done", "Task", "Category", "Priority", "Due"]
    sep = "  +" + "+".join("-" * (x + 2) for x in w) + "+"
    print(sep)
    print("  | " + " | ".join(pad(bold(h), x) for h, x in zip(head, w)) + " |")
    print(sep)
    for idx, t in rows:
        short = t["title"] if len(t["title"]) <= w[2] else t["title"][: w[2] - 1] + "…"
        title_txt = c(short, "9;2") if t["done"] else short
        mark = green("[✔]") if t["done"] else "[ ]"
        cells = [str(idx + 1), mark, title_txt, cyan(t["category"][: w[3]]),
                 priority_label(t["priority"]), due_label(t)]
        print("  | " + " | ".join(pad(cell, x) for cell, x in zip(cells, w)) + " |")
    print(sep)
    done = sum(1 for _, t in rows if t["done"])
    print("  Progress: " + progress_bar(done, len(rows)) + "\n")


def show_stats(tasks):
    total = len(tasks)
    done = sum(t["done"] for t in tasks)
    pending = total - done
    overdue = sum(1 for t in tasks if not t["done"] and t["due"] and days_left(t["due"]) < 0)
    today = sum(1 for t in tasks if not t["done"] and t["due"] and days_left(t["due"]) == 0)
    print("\n" + bold("  📊 STATISTICS"))
    print("  " + "─" * 40)
    print(f"  Total tasks     : {total}")
    print(f"  Completed       : {green(done)}")
    print(f"  Pending         : {yellow(pending)}")
    print(f"  Overdue         : {red(overdue)}")
    print(f"  Due today       : {yellow(today)}")
    print("  " + "─" * 40)
    for p in ("High", "Medium", "Low"):
        n = sum(1 for t in tasks if t["priority"] == p and not t["done"])
        print(f"  Pending {p:<7}: {n}")
    cats = {}
    for t in tasks:
        cats[t["category"]] = cats.get(t["category"], 0) + 1
    if cats:
        print("  " + "─" * 40)
        print("  By category     : " + ", ".join(f"{k} ({v})" for k, v in sorted(cats.items())))
    print("\n  Overall: " + progress_bar(done, total) + "\n")


# --------------------------------------------------------------------------
# Actions
# --------------------------------------------------------------------------
def add_task(tasks, history):
    print(bold("\n  ➕ ADD NEW TASK"))
    title = ask("  Task title: ")
    if not title:
        print(yellow("  Cancelled - title cannot be empty."))
        return
    if any(t["title"].lower() == clean(title).lower() for t in tasks):
        print(yellow("  ⚠ A task with this title already exists."))
        if ask("  Add anyway? (y/N): ").lower() != "y":
            return
    category = ask("  Category (Enter = General): ", "General")
    priority = ask_priority()
    due = ask_due()
    history.append(list(map(dict, tasks)))
    tasks.append(make_task(title, priority, due, category))
    save_tasks(tasks)
    print(green("  ✔ Task added!"))


def edit_task(tasks, history):
    show_tasks(tasks)
    i = ask_index(tasks, "edit")
    if i is None:
        return
    t = tasks[i]
    print(dim("  Press Enter to keep the current value."))
    new_title = ask(f"  Title [{t['title']}]: ", t["title"])
    new_cat = ask(f"  Category [{t['category']}]: ", t["category"])
    new_pr = ask_priority(t["priority"])
    new_due = ask_due(t["due"])
    history.append(list(map(dict, tasks)))
    tasks[i] = make_task(new_title, new_pr, new_due, new_cat, t["done"])
    save_tasks(tasks)
    print(green("  ✔ Task updated!"))


def toggle_task(tasks, history):
    show_tasks(tasks)
    i = ask_index(tasks, "mark done / undone")
    if i is None:
        return
    history.append(list(map(dict, tasks)))
    tasks[i]["done"] = not tasks[i]["done"]
    save_tasks(tasks)
    state = "completed 🎉" if tasks[i]["done"] else "marked as pending"
    print(green(f"  ✔ '{tasks[i]['title']}' {state}."))


def remove_task(tasks, history):
    show_tasks(tasks)
    i = ask_index(tasks, "remove")
    if i is None:
        return
    if ask(f"  Delete '{tasks[i]['title']}'? (y/N): ").lower() != "y":
        print(yellow("  Cancelled."))
        return
    history.append(list(map(dict, tasks)))
    removed = tasks.pop(i)  # list.pop() removes by index
    save_tasks(tasks)
    print(green(f"  🗑 Removed '{removed['title']}'. (Use option 9 to undo)"))


def search_tasks(tasks):
    q = ask("\n  🔍 Search keyword: ").lower()
    if not q:
        return
    rows = [(i, t) for i, t in enumerate(tasks)
            if q in t["title"].lower() or q in t["category"].lower()]
    show_tasks(tasks, rows, f"SEARCH RESULTS for '{q}'")


def filter_sort(tasks):
    print(bold("\n  🎛  FILTER / SORT"))
    print("   1. Pending only        5. Sort by priority")
    print("   2. Completed only      6. Sort by due date")
    print("   3. Overdue only        7. Sort A → Z")
    print("   4. Filter by category  8. High priority pending")
    ch = ask("  Choose (1-8): ")
    rows = list(enumerate(tasks))
    title = "FILTERED TASKS"
    if ch == "1":
        rows = [r for r in rows if not r[1]["done"]]; title = "PENDING TASKS"
    elif ch == "2":
        rows = [r for r in rows if r[1]["done"]]; title = "COMPLETED TASKS"
    elif ch == "3":
        rows = [r for r in rows if not r[1]["done"] and r[1]["due"] and days_left(r[1]["due"]) < 0]
        title = "OVERDUE TASKS"
    elif ch == "4":
        cat = ask("  Category name: ").lower()
        rows = [r for r in rows if r[1]["category"].lower() == cat]; title = f"CATEGORY: {cat}"
    elif ch == "5":
        rows.sort(key=lambda r: PRIORITY_ORDER[r[1]["priority"]]); title = "SORTED BY PRIORITY"
    elif ch == "6":
        rows.sort(key=lambda r: (r[1]["due"] == "", r[1]["due"])); title = "SORTED BY DUE DATE"
    elif ch == "7":
        rows.sort(key=lambda r: r[1]["title"].lower()); title = "SORTED A → Z"
    elif ch == "8":
        rows = [r for r in rows if not r[1]["done"] and r[1]["priority"] == "High"]; title = "HIGH PRIORITY"
    else:
        print(red("  Invalid choice."))
        return
    show_tasks(tasks, rows, title)


def clear_completed(tasks, history):
    n = sum(t["done"] for t in tasks)
    if n == 0:
        print(yellow("  No completed tasks to clear."))
        return
    if ask(f"  Remove {n} completed task(s)? (y/N): ").lower() != "y":
        return
    history.append(list(map(dict, tasks)))
    tasks[:] = [t for t in tasks if not t["done"]]
    save_tasks(tasks)
    print(green(f"  ✔ Cleared {n} completed task(s)."))


def undo(tasks, history):
    if not history:
        print(yellow("  Nothing to undo."))
        return
    tasks[:] = history.pop()
    save_tasks(tasks)
    print(green("  ↩ Last change undone."))


def export_csv(tasks):
    try:
        with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["No", "Done", "Title", "Category", "Priority", "Due"])
            for i, t in enumerate(tasks, 1):
                w.writerow([i, "Yes" if t["done"] else "No", t["title"],
                            t["category"], t["priority"], t["due"]])
        print(green(f"  ✔ Exported to {EXPORT_FILE}"))
    except OSError as err:
        print(red(f"  Export failed: {err}"))


def goodbye():
    return green("\n  👋 Tasks saved. See you next time!\n")


# --------------------------------------------------------------------------
# Main menu
# --------------------------------------------------------------------------
MENU = """
  +----------------------- MAIN MENU -----------------------+
  |   1. View all tasks        7. Filter / Sort              |
  |   2. Add task              8. Statistics                 |
  |   3. Edit task             9. Undo last change           |
  |   4. Mark done / undone   10. Clear completed            |
  |   5. Remove task          11. Export to CSV              |
  |   6. Search tasks          0. Exit                       |
  +---------------------------------------------------------+"""


def main():
    tasks = load_tasks()
    history = []
    clear = lambda: os.system("cls" if os.name == "nt" else "clear") if USE_COLOR else None
    while True:
        clear()
        banner()
        pending = sum(1 for t in tasks if not t["done"])
        overdue = sum(1 for t in tasks if not t["done"] and t["due"] and days_left(t["due"]) < 0)
        print(f"  Today: {date.today():%A, %d %B %Y}   |   Pending: {yellow(pending)}   Overdue: {red(overdue)}")
        print(MENU)
        choice = ask("\n  Enter choice: ")
        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks, history)
        elif choice == "3":
            edit_task(tasks, history)
        elif choice == "4":
            toggle_task(tasks, history)
        elif choice == "5":
            remove_task(tasks, history)
        elif choice == "6":
            search_tasks(tasks)
        elif choice == "7":
            filter_sort(tasks)
        elif choice == "8":
            show_stats(tasks)
        elif choice == "9":
            undo(tasks, history)
        elif choice == "10":
            clear_completed(tasks, history)
        elif choice == "11":
            export_csv(tasks)
        elif choice == "0":
            save_tasks(tasks)
            print(goodbye())
            break
        else:
            print(red("  ❌ Invalid choice. Pick a number from the menu."))
        pause()


if __name__ == "__main__":
    main()
