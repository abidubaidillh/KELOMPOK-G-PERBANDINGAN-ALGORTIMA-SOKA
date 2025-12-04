from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

def rr(tasks: list[Task], vms: list[VM]) -> dict:
    """
    Algoritma Round Robin untuk penjadwalan tugas ke VM.
    Menghasilkan mapping {task_id: vm_name} dengan pembagian merata.
    """

    vms_dict = {vm.name: vm for vm in vms}
    vm_names = list(vms_dict.keys())
    num_vms = len(vm_names)

    solution = {}
    vm_index = 0  # pointer untuk RR

    print(f"Menjalankan Round Robin Scheduling menggunakan {num_vms} VM...")

    for task in tasks:
        chosen_vm = vm_names[vm_index]

        solution[task.id] = chosen_vm

        # pointernya maju (RR)
        vm_index = (vm_index + 1) % num_vms

    print("Round Robin selesai. Semua task berhasil dijadwalkan.")
    return solution
