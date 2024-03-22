import csv

def save_annotations(annotations, output_path):
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['frame', 'fish_x', 'fish_y', 'rod_shake', 'key_input'])
        writer.writerows(annotations)