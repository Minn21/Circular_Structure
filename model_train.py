import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load and preprocess the dataset
data = pd.read_csv('structural_dataset.csv')
features = data.iloc[:, :-1].values
labels = data.iloc[:, -1].values

# Check for NaN or inf in data
print("NaN in features:", np.isnan(features).sum())
print("Inf in features:", np.isinf(features).sum())
print("NaN in labels:", np.isnan(labels).sum())
print("Inf in labels:", np.isinf(labels).sum())

# Handle NaN/inf values
features = np.nan_to_num(features, nan=0.0, posinf=1e5, neginf=-1e5)
labels = np.nan_to_num(labels, nan=0.0, posinf=1e5, neginf=-1e5)

# Normalize features and labels
scaler = StandardScaler()
features = scaler.fit_transform(features)
labels = scaler.fit_transform(labels.reshape(-1, 1)).flatten()

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Define and compile the model
def create_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01), input_shape=(input_shape,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
        tf.keras.layers.Dense(1)  # Output: predicted stress
    ])
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001, clipvalue=1.0)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    return model

model = create_model(input_shape=X_train.shape[1])

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), callbacks=[tf.keras.callbacks.EarlyStopping(patience=5)])

# Evaluate the model
loss, mae = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}, Test MAE: {mae}")

# Save the trained model
model.save('stress_prediction_model.h5')