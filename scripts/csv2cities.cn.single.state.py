import csv
import sys
import os
from datetime import datetime, timezone

def is_empty(val):
    return val is None or str(val).strip().lower() in ('', 'n/a', 'na')

def safe_str(val):
    return "''" if is_empty(val) else f"'{str(val).strip().replace('\'', '\'\'')}'"

def generate_sql(csv_file_path):
    # 用文件名推断 state.name_en
    state_name_en = os.path.splitext(os.path.basename(csv_file_path))[0]
    now = datetime.now(timezone.utc).isoformat()
    output_file_path = os.path.splitext(csv_file_path)[0] + '.sql'

    # 外键级联
    state_id_sql = f"(SELECT id FROM public.states WHERE name_en = '{state_name_en}')"
    country_id_sql = f"(SELECT country_id FROM public.states WHERE name_en = '{state_name_en}')"
    continent_id_sql = f"(SELECT continent_id FROM public.countries WHERE id = {country_id_sql})"

    values = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name_en = safe_str(row.get('name_en'))
            name_cn = safe_str(row.get('name_cn'))
            name_local = name_cn
            code     = safe_str(row.get('code'))

            value = f"""(
    DEFAULT, '{now}', '{now}', {name_local}, {name_en}, {name_cn}, {code}, {state_id_sql}
)"""
            values.append(value)

    sql = f"""INSERT INTO public.cities (
    id, created_at, updated_at, name_local, name_en, name_cn, code, state_id
) VALUES
{',\n'.join(values)}
;
"""

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(sql)

    print(f"✅ SQL written to {output_file_path}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python csv2cities.py <file1.csv> [file2.csv ...]")
        sys.exit(1)

    for csv_file in args:
        if not csv_file.lower().endswith('.csv'):
            print(f"⚠️  Skipped non-csv file: {csv_file}")
            continue
        generate_sql(csv_file)

if __name__ == '__main__':
    main()
