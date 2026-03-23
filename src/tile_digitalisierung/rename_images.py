import os
from pathlib import Path

# Ordner mit den Bildern
folder = Path("./gimp_aligned/10+")  # z.B. "C:/Users/Name/Bilder"

# unterstützte Bildformate
extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")

# Bilder laden und nach Erstellungszeit sortieren
images = [f for f in folder.iterdir() if f.suffix.lower() in extensions]
images.sort(key=lambda x: x.stat().st_mtime)

# Umbenennen ab 10
start_number = 10

for i, img in enumerate(images, start=start_number):
    new_name = f"{i}{img.suffix}"
    new_path = folder / new_name
    img.rename(new_path)
    print(f"{img.name} -> {new_name}")

print("Fertig.")