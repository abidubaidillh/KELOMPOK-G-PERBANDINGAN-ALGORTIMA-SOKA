import asyncio
import httpx
import time
from datetime import datetime
import csv
import pandas as pd
import sys
import os
from dotenv import load_dotenv
from collections import namedtuple
from sma_algorithm import calculate_estimated_makespan

# --- Import algoritma ---
from sma_algorithm import slime_mould_algorithm
from fcfs_algorithm import fcfs
from rr_algorithm import rr
from shc_algorithm import shc

# ----------------------------
# CONFIG
# ----------------------------

load_dotenv()

VM_SPECS = {
    'vm1': {'ip': os.getenv("VM1_IP"), 'cpu': 1, 'ram_gb': 1},
    'vm2': {'ip': os.getenv("VM2_IP"), 'cpu': 2, 'ram_gb': 2},
    'vm3': {'ip': os.getenv("VM3_IP"), 'cpu': 4, 'ram_gb': 4},
    'vm4': {'ip': os.getenv("VM4_IP"), 'cpu': 8, 'ram_gb': 4},
}

VM_PORT = 5000
DATASET_FOLDER = "Dataset"

DATASET_FILES = {
 
    "Low-High": os.path.join(DATASET_FOLDER, "Low-High")
}

OUTPUT_DIR = "Result"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SMA_ITERATIONS = 5000
MULTI_RUN = 10   # jalankan 10 kali

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])


# ----------------------------
# TASK LOADER
# ----------------------------

def get_task_load(index: int):
    return index * index * 10000


def load_tasks(dataset_path: str) -> list[Task]:
    if not os.path.exists(dataset_path):
        print(f"Dataset '{dataset_path}' tidak ditemukan.")
        sys.exit(1)

    tasks = []
    with open(dataset_path, 'r') as f:
        for i, line in enumerate(f):
            try:
                idx = int(line.strip())
                cpu_load = get_task_load(idx)
                tasks.append(Task(
                    id=i,
                    name=f"task-{idx}-{i}",
                    index=idx,
                    cpu_load=cpu_load
                ))
            except:
                pass
    return tasks


# ----------------------------
# EXECUTOR
# ----------------------------

async def execute_task_on_vm(task: Task, vm: VM, client: httpx.AsyncClient,
                             vm_semaphore: asyncio.Semaphore, results_list: list):

    url = f"http://{vm.ip}:{VM_PORT}/task/{task.index}"

    wait_start = time.monotonic()
    start_dt = None
    finish_dt = None
    exec_time = -1

    try:
        async with vm_semaphore:
            wait_time = time.monotonic() - wait_start
            start_dt = datetime.now()
            t0 = time.monotonic()

            resp = await client.get(url, timeout=300.0)
            resp.raise_for_status()

            exec_time = time.monotonic() - t0
            finish_dt = datetime.now()

    except:
        wait_time = time.monotonic() - wait_start
        finish_dt = datetime.now()

    results_list.append({
        "index": task.id,
        "task_name": task.name,
        "vm_assigned": vm.name,
        "start_time": start_dt,
        "exec_time": exec_time,
        "finish_time": finish_dt,
        "wait_time": wait_time
    })


# ----------------------------
# CSV WRITER
# ----------------------------

def write_results(name: str, run: int, results: list):
    output_file = os.path.join(OUTPUT_DIR, f"{name}_run{run}.csv")

    min_start = min([r["start_time"] for r in results])
    for r in results:
        r["start_time"] = (r["start_time"] - min_start).total_seconds()
        r["finish_time"] = (r["finish_time"] - min_start).total_seconds()

    headers = ["index", "task_name", "vm_assigned", "start_time",
               "exec_time", "finish_time", "wait_time"]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(results)

    print(f"[+] Saved → {output_file}")


# ----------------------------
# METRICS
# ----------------------------

def compute_metrics(results: list, vms: list[VM], total_time: float):
    df = pd.DataFrame(results)
    df = df[df["exec_time"] > 0]

    if df.empty:
        return {"error": True}

    metrics = {}
    metrics["makespan"] = total_time
    metrics["avg_exec"] = df["exec_time"].mean()
    metrics["avg_wait"] = df["wait_time"].mean()
    metrics["throughput"] = len(df) / total_time

    vm_exec = df.groupby("vm_assigned")["exec_time"].sum()
    metrics["imbalance"] = (vm_exec.max() - vm_exec.min()) / vm_exec.mean()

    total_cpu = total_time * sum(vm.cpu_cores for vm in vms)
    metrics["resource_util"] = vm_exec.sum() / total_cpu

    return metrics


# ----------------------------
# RUN ALGORITHM ONCE
# ----------------------------

async def run_one(algo_name: str, assignment: dict,
                  tasks, vms, run_id: int):

    results = []
    sem = {vm.name: asyncio.Semaphore(vm.cpu_cores) for vm in vms}

    async with httpx.AsyncClient() as client:
        coroutines = []

        task_map = {t.id: t for t in tasks}
        vm_map = {vm.name: vm for vm in vms}

        for task_id, vm_name in assignment.items():
            coroutines.append(
                execute_task_on_vm(task_map[task_id],
                                   vm_map[vm_name],
                                   client,
                                   sem[vm_name],
                                   results)
            )

        start = time.monotonic()
        await asyncio.gather(*coroutines)
        end = time.monotonic()

    total_time = end - start
    write_results(algo_name, run_id, results)
    return compute_metrics(results, vms, total_time)


# ----------------------------
# MAIN MULTI RUN 10×
# ----------------------------

async def main():

    vms = [VM(name, spec["ip"], spec["cpu"], spec["ram_gb"])
           for name, spec in VM_SPECS.items()]

    for dataset_name, dataset_path in DATASET_FILES.items():

        print(f"\n==============================")
        print(f"   DATASET: {dataset_name}")
        print(f"==============================")

        tasks = load_tasks(dataset_path)

        averaged = {
            "SMA": [],
            "FCFS": [],
            "RR": [],
            "SHC": []
        }

        for run_id in range(1, MULTI_RUN + 1):
            print(f"\n========== RUN {run_id} ({dataset_name}) ==========")

            assignments = {
                "SMA": slime_mould_algorithm(tasks, vms, SMA_ITERATIONS),
                "FCFS": fcfs(tasks, vms),
                "RR": rr(tasks, vms),
                "SHC": shc(tasks, vms, calculate_estimated_makespan, iterations=500)
            }

            # Jalankan semua algoritma
            for algo, ass in assignments.items():
                print(f"\n>>> Running {algo} (run {run_id}) on {dataset_name}")
                metrics = await run_one(algo + "_" + dataset_name, ass, tasks, vms, run_id)
                averaged[algo].append(metrics)

        # Hitung rata-rata tiap dataset
        final = {}
        for algo, data in averaged.items():
            df = pd.DataFrame([m for m in data if not m.get("error")])
            mean_row = df.mean(numeric_only=True)
            final[algo] = mean_row.to_dict()

        # Print summary dataset ini
        print("\n================================")
        print(f"   AVERAGE METRICS: {dataset_name}")
        print("================================")
        df_final = pd.DataFrame(final).T
        print(df_final)

        output_path = os.path.join(OUTPUT_DIR, f"Summary_{dataset_name}.csv")
        df_final.to_csv(output_path)
        print(f"[+] Summary saved → {output_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)