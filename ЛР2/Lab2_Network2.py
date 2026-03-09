import numpy as np
import random
from keras.datasets import fashion_mnist
import matplotlib.pyplot as plt

def relu(z):
    return np.maximum(0, z)

def relu_prime(z):
    return np.where(z > 0, 1.0, 0.0)

def sigmoid(z):
    return 1.0/(1.0+np.exp(-np.clip(z, -500, 500)))

def sigmoid_prime(z):
    return sigmoid(z)*(1-sigmoid(z))

class Network2(object):
    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        # Використання ініціалізації He для ReLU для кращої збіжності
        self.biases = [np.zeros((y, 1)) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) * np.sqrt(2.0/x) for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        for i, (b, w) in enumerate(zip(self.biases, self.weights)):
            z = np.dot(w, a)+b
            if i == len(self.weights) - 1:
                a = sigmoid(z) # Сигмоїда на вихідному шарі
            else:
                a = relu(z)    # ReLU на прихованому шарі
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta, test_data=None):
        if test_data: 
            test_data = list(test_data)
            n_test = len(test_data)
        training_data = list(training_data)
        n = len(training_data)
        
        for j in range(epochs):
            random.shuffle(training_data)
            mini_batches = [training_data[k:k+mini_batch_size] for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)
            if test_data:
                print("Epoch {0}: {1} / {2}".format(j, self.evaluate(test_data), n_test))
            else:
                print("Epoch {0} complete".format(j))

    def update_mini_batch(self, mini_batch, eta):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        activation = x
        activations = [x]
        zs = []
        # Прямий прохід
        for i, (b, w) in enumerate(zip(self.biases, self.weights)):
            z = np.dot(w, activation)+b
            zs.append(z)
            if i == len(self.weights) - 1:
                activation = sigmoid(z)
            else:
                activation = relu(z)
            activations.append(activation)

        # Зворотній прохід - вихідний шар
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())

        # Зворотній прохід - приховані шари
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = relu_prime(z) # Змінено похідну на похідну ReLU!
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, test_data):
        test_results = [(np.argmax(self.feedforward(x)), y) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y):
        return (output_activations - y)

def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

if __name__ == '__main__':
    (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
    # format data
    training_inputs = [np.reshape(x, (784, 1))/255.0 for x in x_train]
    training_results = [vectorized_result(y) for y in y_train]
    training_data = list(zip(training_inputs, training_results))
    
    test_inputs = [np.reshape(x, (784, 1))/255.0 for x in x_test]
    test_data = list(zip(test_inputs, y_test))
    
    print("Network2 initialized... (Fashion MNIST with ReLU)")
    # Для ReLU використовуємо менший Learning Rate, щоб уникнути "взриву" градієнту (eta=0.5)
    net = Network2([784, 30, 10])
    
    net.SGD(training_data, 10, 10, 0.5, test_data=test_data)
    
    # 4. Візуалізація результатів
    class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                   'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
                   
    idx1, idx2 = random.sample(range(len(test_inputs)), 2)
    sample_inputs = [test_inputs[idx1], test_inputs[idx2]]
    sample_labels = [y_test[idx1], y_test[idx2]]
    
    preds = [np.argmax(net.feedforward(x)) for x in sample_inputs]
    
    plt.figure(figsize=(10, 5))
    for i in range(2):
        plt.subplot(1, 2, i+1)
        img = sample_inputs[i].reshape((28, 28))
        plt.imshow(img, cmap='gray')
        plt.title(f'Pred: {class_names[preds[i]]}\nTrue: {class_names[sample_labels[i]]}')
        plt.axis('off')
        
    plt.tight_layout()
    plt.savefig('Network2_Visual_Test.png')
    print('Visual test saved as Network2_Visual_Test.png')
