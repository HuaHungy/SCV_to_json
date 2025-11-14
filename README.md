# subtask_test

小工具集合：将标注 CSV 转为按 `episode_id` 聚合的 JSON，并批量检查 JSON 中 `videos` 路径的存在性。

## 环境要求
- Python 3.8+
- 可选：`tqdm`（用于进度条）

安装可选依赖：
```bash
pip install tqdm
```

## 快速开始
- 生成 JSON（全量）：
```bash
python3 /home/kemove/Downloads/subtask_test/csv_to_json.py
```
- 生成 JSON（指定行范围）：
```bash
python3 /home/kemove/Downloads/subtask_test/csv_to_json.py --start-line 1 --end-line 50
```
- 检查 `videos` 路径是否存在：
```bash
python3 /home/kemove/Downloads/subtask_test/check_videos_exist.py -i /home/kemove/Downloads/subtask_test/test.json --workers 64 --unique
```

## 脚本说明
### csv_to_json.py
- 输入/输出：默认在 `csv_to_json.py:12-13` 配置（`INPUT_CSV`、`OUTPUT_JSON`）。
- 必需列：`原始数据路径`、`startframe`、`endframe`、`episode_id`、`action_text`。
- 路径规范化：
  - 包含 `\\docker2\\` 时映射为 `/mnt/nas/synnas/docker2/{tail}/camera/0/head_color.jpg`。
  - 否则仅统一斜杠为 `/`（实现见 `csv_to_json.py:21-31`）。
- CLI 选项：`--start-line`、`--end-line`（定义见 `csv_to_json.py:72-85`）。
- 输出结构示例：
```json
[
  {
    "videos": "/mnt/nas/synnas/docker2/project/camera/0/head_color.jpg",
    "id": 123,
    "videoLabels": [
      { "ranges": [{ "start": 10, "end": 20 }], "timelinelabels": ["挥手"] }
    ]
  }
]
```

### check_videos_exist.py
- 输入文件：默认指向 `check_videos_exist.py:11` 的 `test.json`，使用 `-i/--input` 自定义。
- 并发与进度：`--workers` 默认 64；如安装了 `tqdm` 将显示进度条（见 `check_videos_exist.py:6-9,54-69`）。
- 选项：`--print-file` 输出缺失的文件路径；默认输出其目录。`--unique` 去重，`--progress-step` 设置无进度条时的打印频率（定义见 `check_videos_exist.py:26-32`）。
- 退出码：读取错误 1；存在缺失 2；全部存在 0。

## 修改配置
- 更改输入/输出路径：编辑 `csv_to_json.py:12-13` 的 `INPUT_CSV` 与 `OUTPUT_JSON`。
- 更改检查输入：运行时传入 `check_videos_exist.py` 的 `-i` 参数。

