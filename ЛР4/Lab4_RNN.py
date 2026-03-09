import numpy as np
import random
import matplotlib.pyplot as plt

# ==========================================
# 1. Формулювання завдання та створення даних
# ==========================================
# Завдання: Класифікація фраз технічного (0) чи ліричного (1) тексту.

vocab = {
    # Технічні слова (Клас 0)
    'алгоритм': 0, 'дані': 1, 'функція': 2, 'масив': 3, 'сервер': 4,
    'база': 5, 'компілятор': 6, 'код': 7, 'змінна': 8, 'інтерфейс': 9,
    # Ліричні слова (Клас 1)
    'любов': 10, 'душа': 11, 'сонце': 12, 'вітер': 13, 'серце': 14,
    'весна': 15, 'сльоза': 16, 'радість': 17, 'небо': 18, 'мрія': 19
}
vocab_size = len(vocab)
word_to_idx = vocab
idx_to_word = {i: w for w, i in vocab.items()}

def generate_dataset(num_samples=1000):
    """Генерує випадкові фрази (технічні або ліричні) довжиною 3 слова."""
    tech_words = list(vocab.keys())[:10]
    lyric_words = list(vocab.keys())[10:]
    
    data = []
    labels = []
    
    for _ in range(num_samples):
        is_lyric = random.choice([True, False])
        if is_lyric:
            phrase = [random.choice(lyric_words) for _ in range(3)]
            labels.append(1)
        else:
            phrase = [random.choice(tech_words) for _ in range(3)]
            labels.append(0)
        data.append(phrase)
        
    return data, labels

def create_inputs_and_targets(data, labels):
    """Перетворює слова у One-Hot вектори."""
    inputs = []
    for phrase in data:
        phrase_vectors = []
        for word in phrase:
            v = np.zeros((vocab_size, 1))
            v[word_to_idx[word]] = 1
            phrase_vectors.append(v)
        inputs.append(phrase_vectors)
    return inputs, labels

# Генерація датасету (1000 тренувальних, 200 тестових)
train_data, train_labels = generate_dataset(1000)
test_data, test_labels = generate_dataset(200)

train_inputs, train_targets = create_inputs_and_targets(train_data, train_labels)
test_inputs, test_targets = create_inputs_and_targets(test_data, test_labels)

# ==========================================
# 2. Архітектура мережі (RNN Vanilla)
# ==========================================
class RNN:
    def __init__(self, input_size, hidden_size, output_size):
        self.hidden_size = hidden_size
        
        # Ініціалізація ваг (ділимо на розмірність для запобігання вибуху градієнтів)
        self.Whx = np.random.randn(hidden_size, input_size) / 1000
        self.Whh = np.random.randn(hidden_size, hidden_size) / 1000
        self.Why = np.random.randn(output_size, hidden_size) / 1000
        
        # Зміщення (biases)
        self.bh = np.zeros((hidden_size, 1))
        self.by = np.zeros((output_size, 1))

    def forward(self, inputs):
        """Прямий прохід для архітектури 'багато-до-одного'"""
        h = np.zeros((self.hidden_size, 1))
        
        # Зберігаємо проміжні стани для Backprop
        self.last_inputs = inputs
        self.last_hs = {0: h}
        
        # Рекурентний прохід через кожен момент часу (кожне слово)
        for i, x in enumerate(inputs):
            h = np.tanh(np.dot(self.Whx, x) + np.dot(self.Whh, h) + self.bh)
            self.last_hs[i + 1] = h
        
        # Вихідний шар (застосовується лише до остннього прихованого стану)
        y = np.dot(self.Why, h) + self.by
        
        # Функція активації Sigmoid для бінарної класифікації (0..1)
        self.last_y = 1 / (1 + np.exp(-y))
        return self.last_y

    def backprop(self, d_y, learn_rate=0.01):
        """Зворотне поширення помилки через час (BPTT)"""
        n = len(self.last_inputs)
        
        # Градієнти для вихідного шару
        # Похідна від сигмоїди вбудована у d_y (Cost: CrossEntropy) для стабільності
        d_Why = np.dot(d_y, self.last_hs[n].T)
        d_by = d_y
        
        # Градієнти для рекурентного шару
        d_Whx = np.zeros_like(self.Whx)
        d_Whh = np.zeros_like(self.Whh)
        d_bh = np.zeros_like(self.bh)
        
        d_h = np.dot(self.Why.T, d_y)
        
        # Зворотний прохід через час
        for t in reversed(range(n)):
            temp = ((1 - self.last_hs[t + 1] ** 2) * d_h) # Похідна tanh
            d_bh += temp
            d_Whh += np.dot(temp, self.last_hs[t].T)
            d_Whx += np.dot(temp, self.last_inputs[t].T)
            
            # Передаємо градієнт попередньому кроку
            d_h = np.dot(self.Whh.T, temp)

        # Оновлення ваг (Градієнтний спуск)
        # Обрізання градієнтів (Gradient Clipping) для стабільності RNN
        for d in [d_Whx, d_Whh, d_Why, d_bh, d_by]:
            np.clip(d, -1, 1, out=d)

        self.Whx -= learn_rate * d_Whx
        self.Whh -= learn_rate * d_Whh
        self.Why -= learn_rate * d_Why
        self.bh -= learn_rate * d_bh
        self.by -= learn_rate * d_by

# ==========================================
# 3. Навчання (Training) та Оцінка
# ==========================================
print("Ініціалізація RNN (розмір словника: 20, прихований шар: 64)...")
# Вхід: 20 (словник), Прихований: 64, Вихід: 1 (Sigmoid 0-1)
rnn = RNN(vocab_size, 64, 1)

epochs = 100
learning_rate = 0.05
history_loss = []
history_acc = []

for epoch in range(epochs):
    loss = 0
    correct = 0
    
    # Перешикуємо дані для кожної епохи
    combined = list(zip(train_inputs, train_targets))
    random.shuffle(combined)
    train_inputs[:], train_targets[:] = zip(*combined)
    
    for x, y_true in zip(train_inputs, train_targets):
        # Forward pass
        y_pred = rnn.forward(x)
        
        # Binary Cross Entropy Loss
        loss -= np.log(y_pred[0, 0] if y_true == 1 else 1 - y_pred[0, 0])
        
        # Точність
        if (y_pred[0, 0] > 0.5 and y_true == 1) or (y_pred[0, 0] <= 0.5 and y_true == 0):
            correct += 1
            
        # Backward pass
        # Градієнт Binary Cross Entropy з Sigmoid спрощується до (y_pred - y_true)
        d_y = y_pred - y_true
        rnn.backprop(d_y, learn_rate=learning_rate)
        
    avg_loss = loss / len(train_inputs)
    accuracy = correct / len(train_inputs)
    history_loss.append(avg_loss)
    history_acc.append(accuracy)
    
    if epoch % 10 == 0 or epoch == epochs - 1:
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f} | Accuracy: {accuracy*100:.2f}%")

# Тестування
test_correct = 0
for x, y_true in zip(test_inputs, test_targets):
    y_pred = rnn.forward(x)
    if (y_pred[0, 0] > 0.5 and y_true == 1) or (y_pred[0, 0] <= 0.5 and y_true == 0):
        test_correct += 1
print(f"\nТочність на тестовій вибірці (200 фраз): {(test_correct / len(test_inputs))*100:.2f}%")

# ==========================================
# 4. Демонстрація класифікації вибраних прикладів
# ==========================================
print("\n--- Демонстрація роботи мережі ---")
samples_to_test = [
    (['функція', 'алгоритм', 'код'], "Технічний"),
    (['небо', 'серце', 'любов'], "Ліричний"),
    (['сервер', 'база', 'дані'], "Технічний"),
    (['радість', 'весна', 'душа'], "Ліричний"),
]

for phrase_words, expected_type in samples_to_test:
    # Конвертуємо слова в тензори
    phrase_vectors = []
    for word in phrase_words:
        v = np.zeros((vocab_size, 1))
        v[word_to_idx[word]] = 1
        phrase_vectors.append(v)
        
    pred = rnn.forward(phrase_vectors)[0, 0]
    pred_class_name = "Ліричний" if pred > 0.5 else "Технічний"
    print(f"Фраза: {' '.join(phrase_words)} -> Передбачення: {pred_class_name} (Впевненість: {pred if pred>0.5 else 1-pred:.2f}), Очікувалося: {expected_type}")

# Візуалізація
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history_loss, color='red')
plt.title('Loss (Binary Cross-Entropy)')
plt.xlabel('Епоха')

plt.subplot(1, 2, 2)
plt.plot(history_acc, color='blue')
plt.title('Accuracy')
plt.xlabel('Епоха')

plt.tight_layout()
plt.savefig('Lab4_RNN_Metrics.png')
print("\nГрафік метрик результатів збережено в `Lab4_RNN_Metrics.png`")
