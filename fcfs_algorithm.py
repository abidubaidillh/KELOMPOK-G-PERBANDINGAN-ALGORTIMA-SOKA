from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

def fcfs(tasks: list[Task], vms: list[VM]) -> dict:
    """
    Algoritma First Come First Serve (FCFS).
    Tugas pertama akan dialokasikan ke VM pertama,
    lalu VM berikutnya, berulang secara berurutan.
    """

    vms_dict = {vm.name: vm for vm in vms}
    vm_names = list(vms_dict.keys())
    num_vms = len(vm_names)

    print(f"Menjalankan FCFS Scheduling menggunakan {num_vms} VM...")

    solution = {}
    vm_index = 0

    for task in tasks:  
        chosen_vm = vm_names[vm_index]

        solution[task.id] = chosen_vm

        # geser VM untuk tugas berikutnya, secara berurutan
        vm_index = (vm_index + 1) % num_vms

    print("FCFS selesai. Semua task berhasil dijadwalkan.")
    return solution
