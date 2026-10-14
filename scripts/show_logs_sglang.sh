LOG_FILE="/var/log/sglang.log"
python - "$LOG_FILE" <<'PY'
import os
import re
import sys
import time
from collections import deque

path = sys.argv[1]
prefills = deque(maxlen=5)
decodes = deque(maxlen=5)

line_pattern = re.compile(r"\[([^\]]+)\]\s+(Prefill batch|Decode batch),\s*(.*)")

PREFILL_COLUMNS = [
    ("Heure", "time"),
    ("Nouv.seq", "#new-seq"),
    ("Nouv.tok", "#new-token"),
    ("Cache.tok", "#cached-token"),
    ("Usage", "full token usage"),
    ("Mamba", "mamba usage"),
    ("Running", "#running-req"),
    ("Queue", "#queue-req"),
    ("Pending", "#pending-token"),
    ("CUDA graph", "cuda graph"),
    ("In tok/s", "input throughput (token/s)"),
]

DECODE_COLUMNS = [
    ("Heure", "time"),
    ("Running", "#running-req"),
    ("Full tok", "#full token"),
    ("Usage", "full token usage"),
    ("Mamba n", "mamba num"),
    ("Mamba", "mamba usage"),
    ("CUDA graph", "cuda graph"),
    ("Gen tok/s", "gen throughput (token/s)"),
    ("Queue", "#queue-req"),
]


def parse_line(line):
    match = line_pattern.search(line)
    if not match:
        return False

    timestamp, kind, fields = match.groups()
    row = {"time": timestamp.rsplit(" ", 1)[-1]}

    for field in fields.split(","):
        if ":" in field:
            key, value = field.split(":", 1)
            row[key.strip()] = value.strip()

    (prefills if kind == "Prefill batch" else decodes).append(row)
    return True


def draw_table(title, columns, rows):
    headers = [header for header, _ in columns]
    data = [[row.get(key, "-") for _, key in columns] for row in rows]
    widths = [
        max(len(headers[i]), *(len(line[i]) for line in data))
        for i in range(len(headers))
    ]

    def print_row(values):
        print("| " + " | ".join(
            str(value).ljust(widths[i]) for i, value in enumerate(values)
        ) + " |")

    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(title)
    print(border)
    print_row(headers)
    print(border)
    for values in data:
        print_row(values)
    if not data:
        print_row(["-" for _ in headers])
    print(border)
    print()


def refresh():
    sys.stdout.write("\033[2J\033[H")
    print(f"SGLang log suivi : {path}  (Ctrl+C pour arrêter)\n")
    draw_table("PREFILL — 5 dernières lignes", PREFILL_COLUMNS, list(prefills))
    draw_table("DECODE — 5 dernières lignes", DECODE_COLUMNS, list(decodes))
    sys.stdout.flush()


def load_existing(file, clear=False):
    if clear:
        prefills.clear()
        decodes.clear()
    file.seek(0)
    for line in file:
        parse_line(line)
    file.seek(0, os.SEEK_END)


try:
    log = open(path, "r", encoding="utf-8", errors="replace")
    inode = os.fstat(log.fileno()).st_ino
    load_existing(log)
    refresh()

    while True:
        line = log.readline()
        if line:
            if parse_line(line):
                refresh()
            continue

        try:
            current = os.stat(path)
            if current.st_ino != inode:
                log.close()
                log = open(path, "r", encoding="utf-8", errors="replace")
                inode = os.fstat(log.fileno()).st_ino
                load_existing(log, clear=True)
                refresh()
            elif current.st_size < log.tell():
                load_existing(log, clear=True)
                refresh()
        except FileNotFoundError:
            pass

        time.sleep(0.25)

except KeyboardInterrupt:
    print("\nSuivi arrêté.")
PY