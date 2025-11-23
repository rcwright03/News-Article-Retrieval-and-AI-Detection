import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from torch.optim import Adam
from collections import Counter
from sklearn.metrics import classification_report, accuracy_score

MAX_LEN = 500
BATCH_SIZE = 32

# Training/Validation Dataset
df = pd.read_csv("datasets/kaggle_test.csv")
texts = df["text"].astype(str).tolist()
labels = df["generated"].astype(int).tolist()

# Preprocessing
def remove_tags(text):
    tags = ['\n', '\'']
    for tag in tags:
        text = text.replace(tag, '')
    return text

df['text'] = df['text'].apply(remove_tags)

# Balance to 1:1
sample_df = pd.DataFrame({'text': texts, 'label': labels})

majority_class = sample_df[sample_df['label'] == 0]
minority_class = sample_df[sample_df['label'] == 1]

majority_downsampled = majority_class.sample(n=len(minority_class), random_state=42)

balanced_df = pd.concat([majority_downsampled, minority_class])

balanced_df = balanced_df.sample(frac=1, random_state=42)

X_balanced = balanced_df['text']
y_balanced = balanced_df['label']

print(len(X_balanced))
print(len(y_balanced))

# Train/Validation Split
X_train_text, X_val_text, y_train, y_val = train_test_split(
    X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
)

# Vocabulary
def build_vocab(texts, max_vocab_size=10000):
    counter = Counter()
    for text in texts:
        counter.update(text.split())
    most_common = counter.most_common(max_vocab_size-2)
    vocab = {word: idx+2 for idx, (word, _) in enumerate(most_common)}
    vocab["<PAD>"] = 0
    vocab["<UNK>"] = 1
    return vocab

vocab = build_vocab(X_train_text)

# Sequence
def text_to_sequence(text, vocab):
    return [vocab.get(token, vocab["<UNK>"]) for token in text.split()]

X_train_seq = [torch.tensor(text_to_sequence(t, vocab))[:MAX_LEN] for t in X_train_text]
X_val_seq   = [torch.tensor(text_to_sequence(t, vocab))[:MAX_LEN] for t in X_val_text]

# Pad sequences
def pad_sequences(sequences, max_len=MAX_LEN):
    return torch.stack([torch.cat([seq, torch.zeros(max_len - len(seq), dtype=torch.long)]) if len(seq)<max_len else seq for seq in sequences])

X_train_tensor = pad_sequences(X_train_seq)
X_val_tensor   = pad_sequences(X_val_seq)

y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
y_val_tensor   = torch.tensor(y_val, dtype=torch.float32)

# Dataloader
class Dataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

train_dataset = Dataset(X_train_tensor, y_train_tensor)
val_dataset   = Dataset(X_val_tensor, y_val_tensor)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# CNN Model Setup
class CNNClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=16, num_filters=32, max_len=500, dropout_prob=0.3):
        super(CNNClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.conv1 = nn.Conv1d(in_channels=embed_dim, out_channels=num_filters, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.AdaptiveMaxPool1d(1)
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(num_filters, 1)

    def forward(self, x):
        x = x.long() 
        x = self.embedding(x)
        x = x.permute(0, 2, 1)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x).squeeze(2)
        x = self.dropout(x)
        x = self.fc(x)
        return x

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNNClassifier(vocab_size=len(vocab)).to(device)

# Loss & Optimizer
num_ai = y_train_tensor.sum().item()
num_human = len(y_train_tensor) - num_ai

# Compute weight for AI generated
ai_weight = torch.tensor(num_human / num_ai).to(device)
print("AI class weight:", ai_weight.item())

criterion = nn.BCEWithLogitsLoss(pos_weight=ai_weight)
optimizer = Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

# Training Loop
patience = 2
best_val_loss = np.inf
epochs_no_improve = 0

for epoch in range(20):
    # Training
    model.train()
    train_loss = 0
    correct = 0
    total = 0
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * X_batch.size(0)
        preds = torch.sigmoid(outputs) >= 0.5
        correct += (preds.float() == y_batch).sum().item()
        total += y_batch.size(0)
    train_loss /= len(train_loader.dataset)
    train_acc = correct / total

    # Validation
    model.eval()
    val_loss = 0
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            val_loss += loss.item() * X_batch.size(0)
            preds_val = torch.sigmoid(outputs) >= 0.5
            val_correct += (preds_val.float() == y_batch).sum().item()
            val_total += y_batch.size(0)
    val_loss /= len(val_loader.dataset)
    val_acc = val_correct / val_total

    print(f"Epoch {epoch+1} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

    # Early stopping
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        epochs_no_improve = 0
        torch.save(model.state_dict(), "best_cnn_model.pt")
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= patience:
            print("Early stopping.")
            break

# Evaluation
def evaluate_model(model, dataloader, device):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).unsqueeze(1)
            outputs = model(X_batch)
            preds = (torch.sigmoid(outputs) >= 0.5).cpu().numpy()
            all_preds.extend(preds.flatten())
            all_labels.extend(y_batch.cpu().numpy().flatten())

    acc = accuracy_score(all_labels, all_preds)
    report = classification_report(all_labels, all_preds)
    return acc, report

model.load_state_dict(torch.load("best_cnn_model.pt"))

train_loader_eval = DataLoader(train_dataset, batch_size=BATCH_SIZE)
val_loader_eval   = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# Evaluate training set
train_acc, train_report = evaluate_model(model, train_loader_eval, device)
print("\nTraining Performance")
print("Training Accuracy:", train_acc)
print("Training Classification Report:\n", train_report)

# Evaluate validation set
val_acc, val_report = evaluate_model(model, val_loader_eval, device)
print("\nValidation Performance")
print("Validation Accuracy:", val_acc)
print("Validation Classification Report:\n", val_report)

# Testing Data
df_test = pd.read_csv("datasets/ieee_train.csv")
X_test_text = df_test["processed_text"].astype(str).tolist()
y_test = df_test["label"].astype(int).tolist()

# Pad sequences
X_test_seq = [torch.tensor(text_to_sequence(t, vocab))[:MAX_LEN] for t in X_test_text]
X_test_tensor = pad_sequences(X_test_seq).long()
y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

# Dataloader
test_dataset = Dataset(X_test_tensor, y_test_tensor)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# Evaluate test set
test_acc, test_report = evaluate_model(model, test_loader, device)
print("\nTest Performance")
print("Test Accuracy:", test_acc)
print("Test Classification Report:\n", test_report)