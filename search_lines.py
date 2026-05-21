with open('dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    low = line.lower()
    if any(x in low for x in ['connection', 'dashed', 'connections-layer', 'drawline', 'draw_line', 'stroke-dash']):
        print(str(i) + ': ' + line.rstrip())
