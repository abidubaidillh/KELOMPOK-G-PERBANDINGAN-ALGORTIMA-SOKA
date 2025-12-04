import random
from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

def shc(tasks: list[Task], vms: list[VM], calculate_estimated_makespan, iterations: int = 500) -> dict:
    """
    Stochastic Hill Climbing (SHC) untuk penjadwalan.
    - Mulai dari solusi acak.
    - Setiap iterasi memindahkan 1 task → VM lain.
    - Diterima jika solusi lebih baik.
    """

    print(f"Menjalankan Stochastic Hill Climbing ({iterations} iterasi)...")

    # Setup
    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())

    # --- Solusi awal (acak) ---
    current_solution = {
        task.id: random.choice(vm_names) for task in tasks
    }

    current_cost = calculate_estimated_makespan(current_solution, tasks_dict, vms_dict)
    best_solution = current_solution.copy()
    best_cost = current_cost

    # --- Iterasi utama SHC ---
    for step in range(iterations):

        # Neighbor: pindahkan 1 task secara acak
        new_solution = current_solution.copy()

        random_task_id = random.choice(list(new_solution.keys()))
        new_vm = random.choice(vm_names)
        new_solution[random_task_id] = new_vm

        # Hitung makespan solusi baru
        new_cost = calculate_estimated_makespan(new_solution, tasks_dict, vms_dict)

        # Jika lebih baik → diterima
        if new_cost < current_cost:
            current_solution = new_solution
            current_cost = new_cost

            # Simpan sebagai best
            if new_cost < best_cost:
                best_cost = new_cost
                best_solution = new_solution.copy()
                print(f"Iterasi {step}: Makespan membaik → {best_cost:.2f}")

    print(f"SHC Selesai. Makespan Terbaik: {best_cost:.2f}")
    return best_solution
