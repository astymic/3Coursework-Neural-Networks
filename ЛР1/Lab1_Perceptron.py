import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Підготовка даних та нормалізація
np.random.seed(42)

def generate_data(num_samples):
    # Генеруємо дані для гіпотетичного кредитного скорингу
    # Значення вже в нормалізованому вигляді (від 0 до 1)
    income = np.random.rand(num_samples)
    credit_score = np.random.rand(num_samples)
    dti_ratio = np.random.rand(num_samples)
    
    # Власна функція класифікації: видаємо кредит (1), якщо дохід і кредитна історія переважають борги
    output = np.where((income + credit_score - dti_ratio) > 0.6, 1, 0)
    
    df = pd.DataFrame({
        'Income_Norm': income,
        'CreditScore_Norm': credit_score,
        'DTI_Ratio_Norm': dti_ratio,
        'output': output
    })
    return df

# Створення навчальної та тестової (перевірочної) вибірки
train_data = generate_data(500)
test_data = generate_data(100)

train_data.to_excel('train_data.xlsx', index=False)
test_data.to_excel('test_data.xlsx', index=False)

# 2. Визначення функцій активації та моделі
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

class SingleLayerPerceptron:
    def __init__(self, input_dim, learning_rate=0.01):
        # Ініціалізація випадковими вагами в інтервалі [0, 1]
        self.weights = np.random.rand(input_dim)
        self.learning_rate = learning_rate
        
    def train(self, X, y, epochs):
        history = []
        for epoch in range(epochs):
            total_error = 0
            for i in range(len(X)):
                # Обчислюємо вихід через сигмоїду
                output_sum = np.dot(X[i], self.weights)
                output_val = sigmoid(output_sum)
                
                # Обчислення помилки
                error = y[i] - output_val
                total_error += abs(error)
                
                # Оновлення ваг (Дельта-правило)
                # ΔW = learning_rate * error * input * Grad(output)
                grad = sigmoid_derivative(output_val)
                for j in range(len(self.weights)):
                    self.weights[j] += self.learning_rate * error * X[i, j] * grad
            
            avg_error = total_error / len(X)
            history.append(avg_error)
            
        return history
        
    def test(self, X, y):
        correct = 0
        for i in range(len(X)):
            output_sum = np.dot(X[i], self.weights)
            output_val = sigmoid(output_sum)
            # Якщо значення більше 0.5 - відносимо до класу 1
            pred = 1 if output_val >= 0.5 else 0
            if pred == y[i]:
                correct += 1
        accuracy = correct / len(X)
        return accuracy

if __name__ == '__main__':
    # Зчитуємо дані
    train_df = pd.read_excel('train_data.xlsx')
    test_df = pd.read_excel('test_data.xlsx')
    
    X_train = train_df[['Income_Norm', 'CreditScore_Norm', 'DTI_Ratio_Norm']].values
    y_train = train_df['output'].values
    
    X_test = test_df[['Income_Norm', 'CreditScore_Norm', 'DTI_Ratio_Norm']].values
    y_test = test_df['output'].values
    
    # 3. Експерименти з різною кількістю епох
    epochs_list = [10, 50, 100, 1000]
    
    plt.figure(figsize=(10, 6))
    
    for epochs in epochs_list:
        p = SingleLayerPerceptron(input_dim=3, learning_rate=0.05)
        hist = p.train(X_train, y_train, epochs=epochs)
        test_acc = p.test(X_test, y_test)
        
        plt.plot(hist, label=f'{epochs} епох')
        
        print(f'Кількість епох: {epochs:<4} | Мін. помилка навчання: {min(hist):.4f} | Точність на тесті: {test_acc:.4f}')
        print(f'Підсумкові ваги: {p.weights}\n')
        
    plt.title('Графік помилки під час навчання')
    plt.xlabel('Епоха')
    plt.ylabel('Середня абсолютна помилка')
    plt.legend()
    plt.grid(True)
    plt.savefig('training_result.png')
    print('Графіки збережені у файлі training_result.png')
