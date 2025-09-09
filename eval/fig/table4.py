import re
import pandas as pd
from statistics import mean

def parse_log(filename):
    results = {
        "4KB-write-2MB": None,
        "4KB-write-1GB": None,
        "Create 10": [],
        "Create 100": []
    }
    with open(filename, "r") as f:
        for line in f:
            # Throughput 값 추출
            if "Throughput:" in line:
                val = float(re.search(r"([\d.]+)", line).group(1))
                if results["4KB-write-2MB"] is None:
                    results["4KB-write-2MB"] = val
                elif results["4KB-write-1GB"] is None:
                    results["4KB-write-1GB"] = val
            # creat-10 값 추출
            elif "creat-10:" in line:
                # "creat-10: 8.724000 us" 에서 8.724000만 추출
                val = float(re.search(r"creat-10:\s*([\d.]+)\s*us", line).group(1))
                results["Create 10"].append(val)

            # creat-100 값 추출
            elif "creat-100:" in line:
                # "creat-100: 9.757333 us" 에서 9.757333만 추출
                val = float(re.search(r"creat-100:\s*([\d.]+)\s*us", line).group(1))
                results["Create 100"].append(val)

    # 평균 처리
    results["Create 10"] = mean(results["Create 10"])
    results["Create 100"] = mean(results["Create 100"])
    return results

# 로그 파일 읽기
logs = {
    "NOVA": parse_log("../data/sharing-cost/nova.log"),
    "ArckFS+": parse_log("../data/sharing-cost/arckfs-plus.log"),
    "ArckFS+-trust-group": parse_log("../data/sharing-cost/arckfs-plus-tg.log"),
}

# DataFrame 만들기 (행: FS, 열: workload)
df = pd.DataFrame(logs).T
df = df[["4KB-write-2MB", "4KB-write-1GB", "Create 10", "Create 100"]]

# 값 포맷 (단위 붙여서 문자열 변환)
df_fmt = df.copy()
df_fmt["4KB-write-2MB"] = df["4KB-write-2MB"].map(lambda x: f"{x:.2f} GiB/s")
df_fmt["4KB-write-1GB"] = df["4KB-write-1GB"].map(lambda x: f"{x:.2f} GiB/s")
df_fmt["Create 10"] = df["Create 10"].map(lambda x: f"{x:.2f} μs")
df_fmt["Create 100"] = df["Create 100"].map(lambda x: f"{x:.2f} μs")

# Transpose 해서 워크로드가 행, FS가 열
df_transposed = df_fmt.T

# Markdown 표를 파일에 저장
with open("table4.md", "w") as f:
    f.write(df_transposed.to_markdown())
