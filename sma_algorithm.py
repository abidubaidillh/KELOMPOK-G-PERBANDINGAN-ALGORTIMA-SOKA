import random
import numpy as np
import math 
from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load', 'ram_mb'])

# --- 1. FUNGSI BIAYA (COST FUNCTION) ---

def calculate_estimated_makespan(solution: dict, tasks_dict: dict, vms_dict: dict) -> float:
    """
    Fungsi Biaya (Cost Function).
    Memperkirakan makespan (waktu selesai maks) untuk solusi tertentu.
    """
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}
    
    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        
        estimated_time = task.cpu_load / vm.cpu_cores # Memastikan bahwa waktu eksekusi dihitung secara deterministik (tidak acak) berdasarkan rasio beban CPU tugas dan core VM.
        vm_loads[vm_name] += estimated_time
        
    return max(vm_loads.values()) # Makespan selalu diukur sebagai waktu selesai maksimum dari semua VM. Ini adalah definisi Makespan standar dalam penjadwalan.

# --- 2. ALGORITMA SLIME MOULD (SMA) ---

def slime_mould_algorithm(tasks: list[Task], vms: list[VM], iterations: int) -> dict:
    """Menjalankan algoritma Slime Mould (SMA) untuk penjadwalan."""
    
    POPULATION_SIZE = 50
    
    print(f"Memulai Slime Mould Algorithm ({iterations} iterasi) dengan Populasi {POPULATION_SIZE} (Optimasi Konsistensi)...")
    
    # --- 1. SETUP & ENCODING ---
    
    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())
    num_tasks = len(tasks)
    num_vms = len(vms)
    
    population = np.random.randint(0, num_vms, size=(POPULATION_SIZE, num_tasks))
    fitness = np.zeros(POPULATION_SIZE)
    
    def decode_solution(vector: np.ndarray) -> dict:
        assignment = {}
        for task_id in range(num_tasks):
            vm_index = vector[task_id]
            vm_name = vm_names[vm_index] 
            assignment[task_id] = vm_name
        return assignment
    
    # Evaluasi Fitness Awal
    for i in range(POPULATION_SIZE):
        assignment_dict = decode_solution(population[i, :])
        fitness[i] = calculate_estimated_makespan(assignment_dict, tasks_dict, vms_dict)
        
    best_fitness_index = np.argmin(fitness)
    best_fitness = fitness[best_fitness_index]
    best_solution_vector = population[best_fitness_index, :].copy()
    
    print(f"Estimasi Makespan Awal (Acak): {best_fitness:.2f}")

    # ----------------------------------------------
    # 2. LOOP UTAMA SMA
    # ----------------------------------------------
    for t in range(iterations):
        # 2a. Update Best Solution (Jika ada perbaikan)
        current_best_idx = np.argmin(fitness)
        if fitness[current_best_idx] < best_fitness:
            best_fitness = fitness[current_best_idx]
            best_solution_vector = population[current_best_idx, :].copy()
            print(f"Iterasi {t}: Estimasi Makespan Baru: {best_fitness:.2f}")

        # Parameter SMA
        s_min = np.min(fitness)
        s_max = np.max(fitness)
        if s_max == s_min: 
            s_max = 1.0 
        
        X_b = best_solution_vector
        
        # 1. Hitung faktor waktu b (decay factor): b: 1.0 -> 0.0
        b = 1 - (t / iterations) 
        
        # 2. Klamp b sedikit di bawah 1.0 (0.99999) agar arctanh aman.
        b_clamped = min(0.99999, b) 
        
        # 3. Hitung Koefisien Eksplorasi A: A: Besar Positif -> Kecil Positif
        A = 2.0 * np.arctanh(b_clamped) 
        
        # 4. Koefisien V untuk Eksplorasi: Range [-A, A]
        v = np.random.uniform(-A, A)
        
        # Hitung Faktor Bobot W (Weight Factor)
        W = np.zeros(POPULATION_SIZE)
        for i in range(POPULATION_SIZE):
            if fitness[i] <= s_min:
                W[i] = 1 + np.random.rand()
            else:
                W[i] = 1 - ((fitness[i] - s_min) / (s_max - s_min))
            W[i] = np.tanh(np.abs(W[i]))
        
        # 2b. Update Posisi (Inti SMA)
        new_population = population.copy()
        
        for i in range(POPULATION_SIZE):
            i1, i2 = random.sample(range(POPULATION_SIZE), 2)
            
            # Komponen acak untuk logika eksplorasi/eksploitasi
            R = np.random.rand() 
            
            for j in range(num_tasks):
                
                # Komponen Eksploitasi (menuju X_b)
                Exploit = W[i] * (X_b[j] - population[i, j]) 
                
                # --- LOGIKA KONSISTENSI/ESCAPE LOCAL OPTIMA ---
                if R < 0.5:
                    # Pergerakan SMA Normal (Eksplorasi/Eksploitasi)
                    Explore = v * (population[i1, j] - population[i2, j])
                    new_val = population[i, j] + Exploit + Explore
                else:
                    # Pergerakan acak eksplosif (Escape local optima)
                    # Menggunakan v, random, dan num_vms * 2 untuk amplitudo besar
                    new_val = X_b[j] + v * (np.random.rand() - 0.5) * num_vms * 2 
                # --- END LOGIKA KONSISTENSI ---
                
                # Pastikan nilai tetap diskrit (0, 1, 2, 3)
                new_population[i, j] = int(np.round(new_val))
                new_population[i, j] = max(0, min(new_population[i, j], num_vms - 1))
            
            # Evaluasi fitness baru
            assignment_dict = decode_solution(new_population[i, :])
            fitness[i] = calculate_estimated_makespan(assignment_dict, tasks_dict, vms_dict)
            
        population = new_population

    print(f"SMA Selesai. Estimasi Makespan Terbaik: {best_fitness:.2f}")
    
    # ----------------------------------------------
    # 3. DECODING FINAL
    # ----------------------------------------------
    best_assignment_dict = decode_solution(best_solution_vector)
    return best_assignment_dict