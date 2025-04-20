import csv
import sys
import os

def is_empty(val):
    return val is None or str(val).strip().lower() in ('', 'n/a', 'na')

def safe_str(val):
    return "''" if is_empty(val) else f"'{str(val).strip().replace('\'', '\'\'')}'"

def generate_sql(csv_file_path, output_dir):
    state_name_en = os.path.splitext(os.path.basename(csv_file_path))[0]
    output_file_name = f"{state_name_en}.sql"
    output_file_path = os.path.join(output_dir, output_file_name)

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
            code = safe_str(row.get('code'))

            value = f"""(
    DEFAULT, NOW(), NOW(), {name_local}, {name_en}, {name_cn}, {code}, {state_id_sql}
)"""
            values.append(value)

    sql = f"""-- {state_name_en}.sql
INSERT INTO public.cities (
    id, created_at, updated_at, name_local, name_en, name_cn, code, state_id
) VALUES
{',\n'.join(values)}
;
"""

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(sql)

    print(f"✅ SQL written to {output_file_path}")
    return sql

def main():
    args = sys.argv[1:]
    if '--out' not in args or len(args) < 3:
        print("Usage: python csv2cities.py <input_dir> --out <output_dir>")
        sys.exit(1)

    input_dir = args[0]
    output_dir = args[args.index('--out') + 1]

    if not os.path.isdir(input_dir):
        print(f"❌ Input directory does not exist: {input_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    all_sql = []

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.csv'):
            full_path = os.path.join(input_dir, filename)
            one_sql = generate_sql(full_path, output_dir)
            all_sql.append(one_sql)

    allinone_path = os.path.join(output_dir, 'allinone.sql')
    with open(allinone_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_sql))

    print(f"\n📦 All-in-one SQL written to {allinone_path}")

if __name__ == '__main__':
    main()