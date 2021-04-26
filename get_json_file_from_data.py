

with open("teachers.json", "w", encoding='utf-8') as f:
    json.dump(teachers, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))


with open("goals.json", "w", encoding='utf-8') as f:
    json.dump(goals, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))