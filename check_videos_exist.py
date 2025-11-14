import os
import sys
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from tqdm import tqdm
except Exception:
    tqdm = None

DEFAULT_JSON = "/home/kemove/Downloads/subtask_test/test.json"

def iter_videos(obj):
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                v = item.get("videos")
                if isinstance(v, str) and v.strip():
                    yield v.strip()
    elif isinstance(obj, dict):
        v = obj.get("videos")
        if isinstance(v, str) and v.strip():
            yield v.strip()

def main():
    parser = argparse.ArgumentParser(description="检查 JSON 中 videos 路径是否存在；不存在则输出对应目录")
    parser.add_argument("-i", "--input", default=DEFAULT_JSON, help="JSON 文件路径，默认指向 test.json")
    parser.add_argument("--print-file", action="store_true", help="不存在时输出文件路径（默认输出其目录）")
    parser.add_argument("--unique", action="store_true", help="去重输出（按文本去重）")
    parser.add_argument("--workers", type=int, default=64, help="并发线程数（默认64，I/O密集建议较大）")
    parser.add_argument("--progress-step", type=int, default=200, help="无 tqdm 时每多少条打印一次进度")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"无法读取 JSON：{e}", file=sys.stderr)
        sys.exit(1)

    # 收集需要检查的路径
    paths = [p for p in iter_videos(data)]
    total = len(paths)

    missing = []

    def _exists(p: str) -> bool:
        try:
            return os.path.exists(p)
        except Exception:
            return False

    # 并发检查 + 进度条
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(_exists, p): p for p in paths}
        if tqdm is not None:
            for fut in tqdm(as_completed(futures), total=total, desc="检查", unit="路径"):
                p = futures[fut]
                if not fut.result():
                    missing.append(p if args.print_file else os.path.dirname(p))
        else:
            processed = 0
            for fut in as_completed(futures):
                processed += 1
                if processed % args.progress_step == 0 or processed == total:
                    print(f"进度: {processed}/{total}", file=sys.stderr)
                p = futures[fut]
                if not fut.result():
                    missing.append(p if args.print_file else os.path.dirname(p))

    if args.unique:
        seen = set()
        uniq = []
        for m in missing:
            if m not in seen:
                uniq.append(m)
                seen.add(m)
        missing = uniq

    if missing:
        for m in missing:
            print(m)
        sys.exit(2)
    else:
        print("全部存在")
        sys.exit(0)

if __name__ == "__main__":
    main()