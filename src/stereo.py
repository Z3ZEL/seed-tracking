import matplotlib.pyplot as plt
import glob
import re
def extract_timestamp(filename):

    # Expression régulière pour extraire le timestamp
    pattern = r"[a-zA-Z]+_img_(\d+)_\d+\.jpg"

    # Utiliser re.search pour trouver la correspondance
    match = re.search(pattern, filename)
    # Vérifier si une correspondance a été trouvée et extraire le timestamp
    if match:
        timestamp = match.group(1)
        return int(timestamp)
    else:
        return None


start_1 = 1721266904571440725
start_2 =1721266921437772947
start_3=1721266945800131713
path_1 = sorted(glob.glob(f"output/m_img_*_{start_1}.jpg"))
path_2 = sorted(glob.glob(f"output/m_img_*_{start_2}.jpg"))
path_3 = sorted(glob.glob(f"output/m_img_*_{start_3}.jpg"))



# Extraire les timestamps
timestamps_1 = [extract_timestamp(path.split("/")[-1]) for path in path_1]
timestamps_2 = [extract_timestamp(path.split("/")[-1]) for path in path_2]
timestamps_3 = [extract_timestamp(path.split("/")[-1]) for path in path_3]

# Créer les listes de numéros d'image
image_numbers_1 = list(range(len(timestamps_1)))
image_numbers_2 = list(range(len(timestamps_2)))
image_numbers_3 = list(range(len(timestamps_3)))

# Tracer les timestamps
plt.figure(figsize=(10, 6))
plt.plot(image_numbers_1, timestamps_1, 'o-', label='Path 1')
plt.plot(image_numbers_2, timestamps_2, 'x-', label='Path 2')
plt.plot(image_numbers_3, timestamps_3, 's-', label='Path 3')
# Ajouter des lignes horizontales pour les valeurs maximales
# plt.axhline(y=1721266145000000000, color='blue', linestyle='--', label=f'Camera started at')
plt.axhline(y=start_1, color='orange', linestyle='--', label=f'First')
plt.axhline(y=start_2, color='orange', linestyle='--', label=f'Second')
plt.axhline(y=start_3, color='orange', linestyle='--', label=f'Third')

# Formater le plot
plt.xlabel('Image Number')
plt.ylabel('Timestamp')
plt.title('Timestamps of Images in Different Paths')
plt.legend()

# Afficher le plot
plt.show()