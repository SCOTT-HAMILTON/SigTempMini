import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, cheby1
import pandas as pd

raw_data = pd.read_csv("arduino_data3.csv")
raw_data.head()

# Convertir la colonne 'timestamp' en type datetime
raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])

# Échantillonner les données pour ne garder qu'un échantillon toutes les 8 secondes
data = raw_data.set_index('timestamp').resample('8s').first().reset_index()

print(raw_data)
print(data)

def plot_original_and_resampled_with_plot_date(signal_name):
    # Vérifier si le signal existe dans les données
    if signal_name not in raw_data.columns or signal_name not in data.columns:
        raise ValueError(f"Le signal '{signal_name}' n'existe pas dans les données.")

    # Extraire les signaux avec les timestamps
    original_signal = raw_data[['timestamp', signal_name]].dropna()
    resampled_signal = data[['timestamp', signal_name]].dropna()

    # Tracer les signaux avec plot_date
    plt.figure(figsize=(12, 6))
    plt.plot_date(original_signal['timestamp'], original_signal[signal_name], label='Signal original', alpha=0.7, linestyle='-')
    plt.plot_date(resampled_signal['timestamp'], resampled_signal[signal_name], label='Signal échantillonné', alpha=0.7, linestyle='--')
    plt.title(f'Comparaison des signaux {signal_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Exemple d'utilisation de la fonction pour le signal 'tempExt'
plot_original_and_resampled_with_plot_date('tempExt')

def filter_signal(signal_name, method='butter', order=2, cutoff=0.1, ripple=5, plot_original=False):
    """
    Filtre un signal donné avec la méthode spécifiée.

    Paramètres:
    - signal_name (str): Nom du signal à filtrer ('tempExt', 'tempInt', 'battVolt').
    - method (str): Méthode de filtrage ('1er ordre', 'butter', 'cheby').
    - order (int): Ordre du filtre (pour butter et cheby).
    - cutoff (float): Fréquence de coupure normalisée (entre 0 et 1).
    - ripple (float): Ondulation en dB pour le filtre Chebyshev.
    """
    # Vérifier si le signal existe dans les données
    if signal_name not in data.columns:
        raise ValueError(f"Le signal '{signal_name}' n'existe pas dans les données.")

    # Extraire le signal
    signal = data[signal_name].dropna()

    # Appliquer le filtre en fonction de la méthode choisie
    if method == '1er ordre':
        # Filtre du premier ordre (passe-bas simple)
        b, a = butter(1, cutoff)
    elif method == 'butter':
        # Filtre Butterworth
        b, a = butter(order, cutoff)
    elif method == 'cheby':
        # Filtre Chebyshev
        b, a = cheby1(order, ripple, cutoff)
    else:
        raise ValueError(f"Méthode de filtrage '{method}' non supportée.")

    # Appliquer le filtre au signal
    filtered_signal = filtfilt(b, a, signal)
    # Tracer le signal original et le signal filtré
    if plot_original:
        plt.plot(signal, label='Signal original', alpha=0.7)
    plt.plot(filtered_signal, label=f'{method}-order={order}', alpha=0.7)

# Exemple d'utilisation de la fonction
plt.figure(figsize=(12, 6))
filter_signal('tempExt', method='butter', order=1, cutoff=0.05, plot_original=True)
# filter_signal('tempExt', method='butter', order=2, cutoff=0.05)
plt.legend()
plt.title("tempExt")
plt.grid(True)

plt.figure(figsize=(12, 6))
filter_signal('tempInt', method='butter', order=1, cutoff=0.05, plot_original=True)
# filter_signal('tempInt', method='butter', order=2, cutoff=0.05)
plt.title("tempInt")
plt.legend()
plt.grid(True)

plt.figure(figsize=(12, 6))
filter_signal('battVolt', method='butter', order=1, cutoff=0.05, plot_original=True)
# filter_signal('battVolt', method='butter', order=2, cutoff=0.05)
plt.title("battVolt")
plt.legend()
plt.grid(True)

plt.show()
