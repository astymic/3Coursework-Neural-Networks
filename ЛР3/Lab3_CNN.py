import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import numpy as np

# 1. Завантаження та підготовка даних
print("Завантаження датасету MNIST...")
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Нормалізація вхідних даних (до діапазону 0-1) та зміна форми для Conv2D (канал 1)
x_train = x_train.reshape((x_train.shape[0], 28, 28, 1)).astype('float32') / 255.0
x_test = x_test.reshape((x_test.shape[0], 28, 28, 1)).astype('float32') / 255.0

# !! ВАЖЛИВО !! Оскільки функція втрат 'mean_squared_error',
# нам необхідно перетворити мітки класів (0-9) у формат One-Hot Encoding (вектори з 10 елементів).
# Якщо цього не зробити, MSE буде рахувати різницю між імовірністю (0-1) та цілим числом класу (0-9), що є помилкою.
y_train_cat = to_categorical(y_train, 10)
y_test_cat = to_categorical(y_test, 10)

def create_model():
    """Створює та повертає згорткову нейромережу відповідно до індивідуального завдання."""
    from tensorflow.keras.optimizers import SGD
    model = Sequential([
        # Базовий згортковий шар (помірний розмір для балансу між навантаженням GPU та швидкістю)
        Conv2D(64, (3, 3), activation='relu', input_shape=(28, 28, 1), padding='same'),
        # ІНДИВІДУАЛЬНЕ ЗАВДАННЯ 1: Додано шар MaxPooling2D
        MaxPooling2D((2, 2)),
        
        Conv2D(128, (3, 3), activation='relu', padding='same'),
        MaxPooling2D((2, 2)),
        
        # Перетворення двовимірного масиву в одновимірний вектор
        Flatten(),
        
        # Повнозв'язний шар оптимального розміру
        Dense(256, activation='relu'),
        # Вихідний шар з 10 нейронами (по одному для кожної цифри) та функцією активації softmax
        Dense(10, activation='softmax')
    ])
    
    # ІНДИВІДУАЛЬНЕ ЗАВДАННЯ 3 та 4: Оптимізатор 'sgd' та функція втрат 'mean_squared_error'
    model.compile(optimizer=SGD(learning_rate=0.05),
                  loss='mean_squared_error',
                  metrics=['accuracy'])
    return model

# ІНДИВІДУАЛЬНЕ ЗАВДАННЯ 2: Експерименти з епохами (10, 50, 100)
epochs_list = [10, 50, 100]
histories = {}
final_metrics = {}

# Оптимізація конвеєра даних для максимального завантаження GPU
# На маленькому датасеті (MNIST) складно використати RTX 3060; 
# Використання великого розміру батчу та tf.data.AUTOTUNE дозволяє агресивно навантажувати відеокарту.
BATCH_SIZE = 1024

train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train_cat))
train_dataset = train_dataset.shuffle(60000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

test_dataset = tf.data.Dataset.from_tensor_slices((x_test, y_test_cat))
test_dataset = test_dataset.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

for epochs in epochs_list:
    print(f"\n[{'='*40}]\nПочаток тренування для {epochs} епох...\n[{'='*40}]")
    model = create_model()
    
    # Тренування
    history = model.fit(train_dataset, 
                        epochs=epochs, 
                        validation_data=test_dataset,
                        verbose=1)
    
    histories[epochs] = history.history
    
    # Оцінка
    print(f"Оцінка моделі для {epochs} епох на тестовій вибірці:")
    test_loss, test_acc = model.evaluate(x_test, y_test_cat, verbose=0)
    final_metrics[epochs] = {'loss': test_loss, 'acc': test_acc}
    print(f"Test Loss (MSE): {test_loss:.4f}, Test Accuracy: {test_acc:.4f}")

# ІНДИВІДУАЛЬНЕ ЗАВДАННЯ 5: Візуалізація результатів
plt.figure(figsize=(15, 10))

for idx, epochs in enumerate(epochs_list):
    # Графік точності (Accuracy)
    plt.subplot(3, 2, idx * 2 + 1)
    plt.plot(histories[epochs]['accuracy'], label='Train Accuracy')
    plt.plot(histories[epochs]['val_accuracy'], label='Test (Val) Accuracy')
    plt.title(f'Accuracy ({epochs} епох)')
    plt.ylabel('Точність')
    plt.xlabel('Епоха')
    plt.legend(loc='lower right')
    plt.grid(True)

    # Графік похибки (Loss - MSE)
    plt.subplot(3, 2, idx * 2 + 2)
    plt.plot(histories[epochs]['loss'], label='Train Loss (MSE)')
    plt.plot(histories[epochs]['val_loss'], label='Test (Val) Loss (MSE)')
    plt.title(f'Loss / MSE ({epochs} епох)')
    plt.ylabel('Похибка (MSE)')
    plt.xlabel('Епоха')
    plt.legend(loc='upper right')
    plt.grid(True)

plt.tight_layout()
plt.savefig('Lab3_CNN_Training_Plots.png')
print("\nГрафіки збережено у файлі 'Lab3_CNN_Training_Plots.png'")

print("\n--- ПІДСУМКОВІ ЗНАЧЕННЯ ---")
for ep, metrics in final_metrics.items():
    print(f"{ep} епох -> Test Acc: {metrics['acc']:.4f} | Test MSE: {metrics['loss']:.4f}")
