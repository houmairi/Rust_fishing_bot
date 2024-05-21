import psutil
import time
import GPUtil
from datetime import datetime

def measure_resource_usage():
    # Initialisiere Variablen zur Speicherung der Messwerte
    cpu_usage_sum = 0
    cpu_usage_count = 0
    memory_usage_max = 0
    gpu_usage_max = 0

    # Starte die Messung
    print("Ressourcennutzung wird überwacht...")
    start_time = time.time()

    try:
        while True:
            # Messe die CPU-Auslastung
            cpu_usage = psutil.cpu_percent()
            cpu_usage_sum += cpu_usage
            cpu_usage_count += 1

            # Messe die Speichernutzung
            memory_info = psutil.Process().memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # In MB
            memory_usage_max = max(memory_usage_max, memory_usage)

            # Messe die GPU-Auslastung (falls vorhanden)
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
                gpu_usage_max = max(gpu_usage_max, gpu_usage)

            # Warte eine Sekunde bis zur nächsten Messung
            time.sleep(1)

    except KeyboardInterrupt:
        # Beende die Messung bei Tastaturunterbrechung (Strg+C)
        end_time = time.time()
        duration = end_time - start_time

        # Berechne die durchschnittliche CPU-Auslastung
        avg_cpu_usage = cpu_usage_sum / cpu_usage_count

        # Gib die Messergebnisse aus
        print("\nRessourcennutzung:")
        print(f"Dauer: {duration:.2f} Sekunden")
        print(f"Durchschnittliche CPU-Auslastung: {avg_cpu_usage:.2f}%")
        print(f"Maximale Speichernutzung: {memory_usage_max:.2f} MB")
        if gpus:
            print(f"Maximale GPU-Auslastung: {gpu_usage_max:.2f}%")

        # Speichere die Messergebnisse in einer Datei
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_usage_{timestamp}.txt"
        with open(filename, "w") as file:
            file.write("Ressourcennutzung:\n")
            file.write(f"Dauer: {duration:.2f} Sekunden\n")
            file.write(f"Durchschnittliche CPU-Auslastung: {avg_cpu_usage:.2f}%\n")
            file.write(f"Maximale Speichernutzung: {memory_usage_max:.2f} MB\n")
            if gpus:
                file.write(f"Maximale GPU-Auslastung: {gpu_usage_max:.2f}%\n")
        print(f"Messergebnisse wurden in {filename} gespeichert.")

if __name__ == "__main__":
    measure_resource_usage()