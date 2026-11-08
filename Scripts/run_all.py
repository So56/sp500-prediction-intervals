from pathlib import Path
import subprocess
import sys


script_dir = Path(__file__).resolve().parent
# システムPythonから起動した場合も、作成済みのプロジェクト環境を使う
venv_python = script_dir.parent / ".venv" / (
    "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
)
python_executable = sys.executable
if sys.prefix == sys.base_prefix and venv_python.is_file():
    python_executable = str(venv_python)

# 同じPython環境で、上から順に実行する
scripts = [
    "01_prepare_data.py",
    "02_fit_models.py",
    "03_build_intervals.py",
    "04_evaluate.py",
    "06_bootstrap.py",
    "05_make_figures.py",
    "07_write_report.py",
]
for script in scripts:
    print(f"\n実行: {script}", flush=True)
    subprocess.run([python_executable, str(script_dir / script)], check=True)
print("\n分析が完了しました。")
