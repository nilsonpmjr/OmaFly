#!/usr/bin/env python3
"""Record local build/runtime capabilities without changing desktop configuration."""
import importlib.util
import json
import platform
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    result={"system":platform.platform(),"python":platform.python_version(),
            "modules":{m:importlib.util.find_spec(m) is not None for m in ["PySide6","numpy","torch","brian2"]},
            "commands":{c:shutil.which(c) for c in ["g++","quickshell","hyprctl","hipcc"]}}
    if shutil.which("pacman"):
        result["packages"]=subprocess.run(["pacman","-Q","hyprland","quickshell","qt6-base","pyside6","rocm-hip-runtime"],capture_output=True,text=True).stdout.splitlines()
    if shutil.which("lspci"):
        lines=subprocess.run(["lspci","-nn"],capture_output=True,text=True).stdout.splitlines()
        result["gpu_pci"]=[line for line in lines if "VGA compatible" in line or "3D controller" in line]
    for device in Path("/sys/class/drm").glob("card[0-9]/device"):
        result.setdefault("drm",[]).append({name:(device/name).read_text().strip()
                    for name in ["vendor","device","mem_info_vram_total"] if (device/name).exists()})
    result["scope"]="Inventory only; GUI and GPU execution are documented in separate reports"
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/environment.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
