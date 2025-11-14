'''
python3 /home/kemove/Downloads/subtask_test/csv_to_json.py \
--start-line 1 \
--end-line 50
'''
import argparse
import csv
import json
from collections import defaultdict
import re

INPUT_CSV = "/home/kemove/Downloads/subtask_test/标注数据映射表.csv"
OUTPUT_JSON = "/home/kemove/Downloads/subtask_test/test.json"

def to_int(s):
    try:
        return int(str(s).strip())
    except Exception:
        return None

def transform_b_path_to_url(b_val):
    s = (b_val or "").strip()
    if not s:
        return s
    s = s.replace("/", "\\")
    m = re.search(r'\\docker2\\', s, flags=re.IGNORECASE)
    if not m:
        return s.replace("\\", "/")
    tail = s[m.end():].replace("\\", "/")
    return f"/mnt/nas/synnas/docker2/{tail}/camera/0/head_color.jpg"

def main(start_line=None, end_line=None):
    by_id = defaultdict(lambda: {"videos": "", "id": None, "videoLabels": []})

    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader, start=1):
            if start_line is not None and row_idx < start_line:
                continue
            if end_line is not None and row_idx > end_line:
                break

            b_val = (row.get("原始数据路径") or "").strip()          # B
            start = to_int(row.get("startframe"))                    # D
            end = to_int(row.get("endframe"))                        # E
            f_id = to_int(row.get("episode_id"))                     # F
            label = (row.get("action_text") or "").strip()           # G

            if not b_val or f_id is None or start is None or end is None or not label:
                continue

            b_url = transform_b_path_to_url(b_val)

            entry = by_id[f_id]
            if entry["id"] is None:
                entry["id"] = f_id

            if not entry["videos"]:
                entry["videos"] = b_url

            entry["videoLabels"].append({
                "ranges": [{ "end": end , "start": start }],
                "timelinelabels": [label]
            })

    # 仅输出已聚合并且有至少一个 videoLabel 的条目
    output_list = [v for v in by_id.values() if v["id"] is not None and v["videoLabels"]]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(output_list, out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV -> JSON（支持行范围与缺失列过滤）")
    parser.add_argument("--start-line", type=int, default=None, help="数据起始行（不含表头，从1开始）")
    parser.add_argument("--end-line", type=int, default=None, help="数据结束行（不含表头，从1开始，含该行）")
    args = parser.parse_args()

    if args.start_line is not None and args.start_line <= 0:
        raise ValueError("start-line 必须为正整数")
    if args.end_line is not None and args.end_line <= 0:
        raise ValueError("end-line 必须为正整数")
    if args.start_line is not None and args.end_line is not None and args.end_line < args.start_line:
        raise ValueError("end-line 不能小于 start-line")

    main(args.start_line, args.end_line)