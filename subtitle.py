def get_unfinished_srt(filename):
    with open(f'{filename}.srt', 'r') as srt:
        sub_lines = srt.readlines()
    return sub_lines


def write_finished_srt(filename, lines):
    with open(f'{filename}.srt', 'w') as srt:
        srt.writelines(lines)


def format_time(sec):
    h = str(0)
    m = str(int(sec//60))
    us = str(sec % 60)
    p = us.find('.')
    s = us[:p]
    ms = us[p+1: p+4]
    return f'{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)},{ms}'


def finish_subs(filename):
    lines = get_unfinished_srt(filename)

    for n, line in enumerate(lines):
        if line.startswith("START"):
            start_time = float(line.strip("START"))
            if n + 4 < len(lines):
                end_time = float(lines[n + 4].strip("START"))
            else:
                end_time = start_time + 1
            lines[n] = f'{format_time(start_time)} --> {format_time(end_time)}\n'
    write_finished_srt(filename, lines)


if __name__ == "__main__":
    filename = "/home/pi/Videos/test"
    finish_subs(filename)
    