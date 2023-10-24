import io 
import re
import subprocess
from pathlib import Path
from typing import Union 

import numpy as np
import pandas as pd


def run_cmd(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        args = cmd,
        shell=True,
        capture_output=True,
        check=True
    )


def clean_text(txt: Union[str, bytes]) -> str:
    """stdout is captured as bytes, with multiple spaces separating fields."""
    txt_str = txt
    if isinstance(txt, bytes):
        txt_str = txt.decode("utf-8") 

    return re.sub(r" +", "\t", txt_str)


def main() -> None:
    # Gather information on the cluster
    cluster_info = run_cmd("""sinfo -l -N --Format="nodehost,statecompact,partitionname,cpus,memory,gres" -p gpu | tail -n +2""")
    cluster_info_txt = clean_text(cluster_info.stdout)
    cluster = pd.read_csv(io.StringIO(cluster_info_txt), sep="\t")

    # Prepare values
    gpu_names_re = r"gpu:(?P<type>\w+):(?P<count>\d+)"
    cluster[["type", "count"]] = cluster["GRES"].str.extractall(gpu_names_re).reset_index()[["type", "count"]]
    cluster["count"] = cluster["count"].astype(int)
    cluster_pivot = cluster.pivot_table(values="count", columns="type", index=["HOSTNAMES", "CPUS", "MEMORY", "STATE"], fill_value=0, margins=True, margins_name="TotalGPU", aggfunc=np.sum).reset_index()
    cluster_pivot.drop(cluster_pivot[cluster_pivot["HOSTNAMES"] == "TotalGPU"].index, inplace=True)

    # cluster_pivot: HOSTNAMES	CPUS	MEMORY	STATE	a6000	maxwell	p40	pascal	pascalxp	volta	TotalGPU

    # Gather information on running jobs
    usage_info = run_cmd("""squeue -O "UserName:15,JobID:8,State,Name:40,NodeList:12,tres-alloc:60,tres-per-node:" -p gpu""")
    usage_info_txt = clean_text(usage_info.stdout)
    usage = pd.read_csv(io.StringIO(usage_info_txt), sep="\t")
    usage = usage.drop(usage[usage["STATE"] == "PENDING"].index).reset_index(drop=True)

    # Prepare values
    tres_alloc_re = r"(?P<resname>[^=,]+)=(?P<rescount>\d+)"
    usage[["cpu", "gres/gpu", "mem"]] = usage["TRES_ALLOC"].str.extractall(tres_alloc_re).reset_index().pivot_table(values="rescount", columns="resname", index="level_0", fill_value=0).astype(int).reset_index()[["cpu", "gres/gpu", "mem"]]
    total_usage = usage.groupby("NODELIST")[["cpu", "gres/gpu", "mem"]].sum()

    # join both information
    snapshot = total_usage.join(cluster_pivot.set_index("HOSTNAMES"), how="right")
    snapshot = snapshot.fillna(0).astype(int, errors="ignore")
    snapshot["AvailableGPU"] = snapshot["TotalGPU"] - snapshot["gres/gpu"]
    snapshot["AvailableCPU"] = snapshot["CPUS"] - snapshot["cpu"]
    snapshot["AvailableRAM"] = snapshot["MEMORY"] - snapshot["mem"] * 1024

    now = pd.Timestamp.now(tz="Europe/Amsterdam")
    snapshot[["STATE", "AvailableGPU", "AvailableCPU", "AvailableRAM"]].to_csv(f"{now.strftime('%Y%m%d_%H:%M')}.csv")


if __name__ == "__main__":
    main()
