import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Concatenate
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.utils import to_categorical


file_path = 'arquivos/resultados/analisado.csv'
metadata = pd.read_csv(file_path)
metadata_features = metadata[['MLv', 'SNR_P', 'Distance', 'Num_Stations']].values
labels = metadata['Label'].values  # Supondo que 'Event Class' seja a coluna com as labels

scaler = StandardScaler()
metadata_features = scaler.fit_transform(metadata_features)

spectrograms = []
for index, row in metadata.iterrows():
    spect_path = f"{row['Path']}".replace('.mseed', '.npy')
    spectrogram = np.load(spect_path)
    spectrograms.append(spectrogram)

spectrograms = np.array(spectrograms)

# Dividir os dados em treinamento e teste
X_spect_train, X_spect_test, X_meta_train, X_meta_test, y_train, y_test = train_test_split(
    spectrograms, metadata_features, labels, test_size=0.2, random_state=42)
num_metadata_features = 4
input_spectrogram = Input(shape=(237, 50, 1), name='spectrogram_input')

# Convoluções e pooling
x = Conv2D(18, (5, 5), activation='relu')(input_spectrogram)
x = MaxPooling2D((2, 2))(x)
x = Conv2D(36, (3, 3), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)
x = Conv2D(68, (3, 3), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)
x = Conv2D(68, (2, 2), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)
x = Flatten()(x)

# Camadas densas
x = Dense(80, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(80, activation='relu')(x)
x = Dropout(0.5)(x)

# Entrada para os metadados
input_metadata = Input(shape=(num_metadata_features,), name='metadata_input')
combined = Concatenate()([x, input_metadata])
final_output = Dense(2, activation='softmax')(combined)

new_model = Model(inputs=[input_spectrogram, input_metadata], outputs=final_output)
new_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
new_model.summary()

y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

# Treinar o modelo
history = new_model.fit(
    [X_spect_train, X_meta_train],
    y_train_cat,
    epochs=10,
    batch_size=32,
    validation_data=([X_spect_test, X_meta_test], y_test_cat)
)

# Salvar o modelo treinado
new_model.save('model_with_metadata.h5')
