import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import Callback
import pickle  # For saving the tokenizers

# Step 1: Load the dataset
def load_data(file_path):
    print("Loading dataset...")
    df = pd.read_csv(file_path, header=None, names=['English', 'Marathi'])
    print(f"Dataset loaded with {len(df)} pairs.")
    return df

# Step 2: Preprocess the data
def preprocess_data(df):
    print("Preprocessing data...")
    english_tokenizer = Tokenizer()
    marathi_tokenizer = Tokenizer()

    # Fit on texts
    english_tokenizer.fit_on_texts(df['English'])
    marathi_tokenizer.fit_on_texts(df['Marathi'])

    # Convert to sequences
    english_sequences = english_tokenizer.texts_to_sequences(df['English'])
    marathi_sequences = marathi_tokenizer.texts_to_sequences(df['Marathi'])

    # Padding sequences
    max_len = max(len(seq) for seq in english_sequences + marathi_sequences)
    english_sequences = pad_sequences(english_sequences, maxlen=max_len, padding='post')
    marathi_sequences = pad_sequences(marathi_sequences, maxlen=max_len, padding='post')

    print(f"Data tokenized and padded to a maximum length of {max_len}.")
    return english_sequences, marathi_sequences, english_tokenizer, marathi_tokenizer, max_len

# Step 3: Build the translation model
def build_model(vocab_size_en, vocab_size_mr, embedding_dim, latent_dim):
    print("Building the model...")
    # Encoder
    encoder_inputs = Input(shape=(None,))
    encoder_embedding = Embedding(vocab_size_en, embedding_dim)(encoder_inputs)
    encoder_lstm = LSTM(latent_dim, return_state=True)
    encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
    encoder_states = [state_h, state_c]

    # Decoder
    decoder_inputs = Input(shape=(None,))
    decoder_embedding = Embedding(vocab_size_mr, embedding_dim)(decoder_inputs)
    decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
    decoder_dense = Dense(vocab_size_mr, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    # Model
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    print("Model built successfully.")
    return model

# Step 4: Train the model with accuracy updates
class AccuracyCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"Epoch {epoch + 1}, Loss: {logs['loss']:.4f}, Accuracy: {logs['accuracy']:.4f}")

def train_model(model, english_sequences, marathi_sequences):
    # Split data into train and validation sets
    english_train, english_val, marathi_train, marathi_val = train_test_split(english_sequences, marathi_sequences, test_size=0.2)
    
    print("Training the model...")
    model.fit(
        [english_train, marathi_train[:, :-1]], 
        marathi_train.reshape(marathi_train.shape[0], marathi_train.shape[1], 1)[:, 1:], 
        validation_data=([english_val, marathi_val[:, :-1]], marathi_val.reshape(marathi_val.shape[0], marathi_val.shape[1], 1)[:, 1:]),
        epochs=20, 
        batch_size=64,
        callbacks=[AccuracyCallback()]
    )

# Step 5: Save the tokenizers
def save_tokenizers(english_tokenizer, marathi_tokenizer):
    with open('english_tokenizer.pkl', 'wb') as file:
        pickle.dump(english_tokenizer, file)
    with open('marathi_tokenizer.pkl', 'wb') as file:
        pickle.dump(marathi_tokenizer, file)
    print("Tokenizers saved.")

# Main function
if __name__ == "__main__":
    # Load and preprocess the data
    df = load_data('data.csv')  # Update the path if necessary
    english_sequences, marathi_sequences, english_tokenizer, marathi_tokenizer, max_len = preprocess_data(df)

    # Prepare vocab sizes and model parameters
    vocab_size_en = len(english_tokenizer.word_index) + 1
    vocab_size_mr = len(marathi_tokenizer.word_index) + 1
    embedding_dim = 256
    latent_dim = 256

    # Build and train the model
    model = build_model(vocab_size_en, vocab_size_mr, embedding_dim, latent_dim)
    train_model(model, english_sequences, marathi_sequences)

    # Save the model and tokenizers
    model.save('translation_model.h5')
    save_tokenizers(english_tokenizer, marathi_tokenizer)

    print("Model and tokenizers saved.")
