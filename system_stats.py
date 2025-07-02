import os
import platform
import socket
import psutil
import cpuinfo
import time
import csv
from tqdm import tqdm
from datetime import datetime

KB = 1024
MB = KB ** 2
GB = KB ** 3

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def bytes_to_gb(value):
    return round(value / GB, 2)

def get_memory_stats():
    mem = psutil.virtual_memory()
    return {
        'total': bytes_to_gb(mem.total),
        'used': bytes_to_gb(mem.used),
        'free': bytes_to_gb(mem.available),
        'percent': mem.percent
    }

def get_disk_stats():
    disk = psutil.disk_usage('/')
    return {
        'total': bytes_to_gb(disk.total),
        'used': bytes_to_gb(disk.used),
        'free': bytes_to_gb(disk.free),
        'percent': disk.percent
    }

def get_cpu_info():
    return {
        'brand': cpuinfo.get_cpu_info().get('brand_raw', 'Unknown'),
        'cores': os.cpu_count()
    }

def get_active_interface():
    interfaces = psutil.net_if_stats()
    for name, stats in interfaces.items():
        if stats.isup:
            return name
    return "N/A"

def print_service_stats():
    print("\n---------- Services ----------")
    print("Running processes:", len(psutil.pids()))

def print_system_info():
    cpu = get_cpu_info()
    print("\n---------- System Info ----------")
    print("Hostname     :", socket.gethostname())
    print("System       :", platform.system(), platform.machine())
    print("Kernel       :", platform.release())
    print("Compiler     :", platform.python_compiler())
    print("CPU          :", cpu['brand'], f"({cpu['cores']} cores)")
    print("Memory       :", get_memory_stats()['total'], "GiB")
    print("Disk         :", get_disk_stats()['total'], "GiB")
    print("Python       :", platform.python_version())
    print("Python Build :", platform.python_build())            
    print("CPU Info     :", cpuinfo.get_cpu_info().get('arch', 'Unknown'))

def print_load_avg():
    print("\n---------- Load Average ----------")
    if hasattr(os, "getloadavg"):
        load = os.getloadavg()
        print("Load avg (1 min) :", round(load[0], 2))
        print("Load avg (5 min) :", round(load[1], 2))
        print("Load avg (15 min):", round(load[2], 2))
    else:
        print("Load average not supported on this OS.")

def print_memory_disk_usage():
    mem = get_memory_stats()
    disk = get_disk_stats()
    print("\n---------- RAM & Disk Usage ----------")
    print(f"RAM Used         : {mem['used']} GiB / {mem['total']} GiB ({mem['percent']}%)")
    print(f"Disk Used        : {disk['used']} GiB / {disk['total']} GiB ({disk['percent']}%)")

def analyze_system(timeframe, system_name):
    print("\n========== Starting System Analysis ==========")
    print(f"Analyzing usage over {timeframe} minutes...\n")

    seconds = timeframe * 60
    cpu_usages = []
    ram_usages = []

    before_net = psutil.net_io_counters()
    for _ in tqdm(range(seconds), desc="Monitoring", ncols=70):
        cpu_usages.append(psutil.cpu_percent(interval=1))
        ram_usages.append(psutil.virtual_memory().percent)
    after_net = psutil.net_io_counters()

    avg_cpu = round(sum(cpu_usages) / len(cpu_usages), 2)
    avg_ram = round(sum(ram_usages) / len(ram_usages), 2)
    send_rate = round((after_net.bytes_sent - before_net.bytes_sent) / KB / seconds, 2)
    recv_rate = round((after_net.bytes_recv - before_net.bytes_recv) / KB / seconds, 2)

    print("\n========== System Analysis Result ==========")
    print("System Name        :", system_name or "System Stats")
    print(f"Average CPU Usage  : {avg_cpu}%")
    print(f"Average RAM Usage  : {avg_ram}%")
    print(f"Network Send Rate  : {send_rate} KiB/s")
    print(f"Network Recv Rate  : {recv_rate} KiB/s")

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    hostname = socket.gethostname()
    filename = f"system_analysis_{hostname}_{timestamp}.csv"

    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["System Name", "Average CPU Usage (%)", "Average RAM Usage (%)", "Send Rate (KiB/s)", "Receive Rate (KiB/s)"])
        writer.writerow([system_name or hostname, avg_cpu, avg_ram, send_rate, recv_rate])

    print(f"\n✅ Results saved to: {filename}")

def main(timeframe, system_name):
    clear_screen()
    print_service_stats()
    print_system_info()
    print_load_avg()
    print_memory_disk_usage()
    analyze_system(timeframe, system_name)

if __name__ == '__main__':
    try:
        clear_screen()
        system_name = input("Enter the system name (optional): ").strip()
        timeframe_input = input("Enter the timeframe (in minutes, default 30): ").strip()
        timeframe = int(timeframe_input) if timeframe_input else 30
    except ValueError:
        timeframe = 30
    system_name = system_name if system_name else "System Stats"
    main(timeframe, system_name)
