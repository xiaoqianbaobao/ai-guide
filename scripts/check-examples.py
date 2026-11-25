"""Run each independent example's unittest suite in its own working directory."""
from pathlib import Path
import re
import subprocess
import sys


def main():
    examples = Path(__file__).resolve().parents[1] / "examples"
    suites = sorted(path for path in examples.iterdir()
                    if path.is_dir() and any(path.glob("test_*.py")))
    if not suites:
        raise SystemExit("没有找到示例测试")
    failures = []
    for suite in suites:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-v"],
            cwd=suite, text=True, capture_output=True,
        )
        report = result.stdout + result.stderr
        count = re.search(r"Ran (\d+) tests?", report)
        skipped = re.search(r"skipped=(\d+)", report)
        print(f"{suite.name}: {'通过' if result.returncode == 0 else '失败'}，"
              f"{count.group(1) if count else '未知数量'} 项"
              f"{f'，跳过 {skipped.group(1)} 项' if skipped else ''}", flush=True)
        if result.returncode:
            failures.append(suite.name)
            print(report, file=sys.stderr)
    if failures:
        raise SystemExit(f"示例测试失败：{', '.join(failures)}")
    print(f"已检查 {len(suites)} 组示例；跳过项不代表已验证。")


if __name__ == "__main__":
    main()
