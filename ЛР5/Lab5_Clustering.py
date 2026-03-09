import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
from mpl_toolkits.mplot3d import Axes3D

# Завантаження датасету Iris
iris = datasets.load_iris()
X = iris.data
y = iris.target
feature_names = iris.feature_names

# ==========================================
# 1 & 2. K-means на нових парах ознак
# ==========================================
# Замість sepal length (0) та sepal width (1), візьмемо:
# - Petal length (2) та Petal width (3)
# - Sepal length (0) та Petal length (2)

plt.figure(figsize=(15, 6))

features_pair1 = X[:, [2, 3]] # Petal length and width
kmeans1 = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans1.fit(features_pair1)

plt.subplot(1, 2, 1)
plt.scatter(features_pair1[:, 0], features_pair1[:, 1], c=kmeans1.labels_, cmap='viridis', edgecolor='k')
plt.scatter(kmeans1.cluster_centers_[:, 0], kmeans1.cluster_centers_[:, 1], s=200, c='red', marker='X', label='Centroids')
plt.title('K-means: Petal length vs Petal width')
plt.xlabel(feature_names[2])
plt.ylabel(feature_names[3])
plt.legend()

features_pair2 = X[:, [0, 2]] # Sepal length vs Petal length
kmeans2 = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans2.fit(features_pair2)

plt.subplot(1, 2, 2)
plt.scatter(features_pair2[:, 0], features_pair2[:, 1], c=kmeans2.labels_, cmap='viridis', edgecolor='k')
plt.scatter(kmeans2.cluster_centers_[:, 0], kmeans2.cluster_centers_[:, 1], s=200, c='red', marker='X', label='Centroids')
plt.title('K-means: Sepal length vs Petal length')
plt.xlabel(feature_names[0])
plt.ylabel(feature_names[2])
plt.legend()

plt.tight_layout()
plt.savefig('Lab5_KMeans_Clusters.png')

# ==========================================
# 3. Ієрархічна кластеризація та Дендрограма
# ==========================================
plt.figure(figsize=(10, 7))
plt.title("Дендрограма Ієрархічної кластеризації (Iris)")

# Використовуємо метод ward для мінімізації дисперсії всередині кластерів
linked = linkage(X, method='ward')
dendrogram(linked, truncate_mode='level', p=5)
plt.xlabel('Індекси точок (або розмір кластера)')
plt.ylabel('Відстань (Ward)')
plt.savefig('Lab5_Dendrogram.png')

# Ієрархічна кластеризація (Агломеративна)
hierarchical = AgglomerativeClustering(n_clusters=3, linkage='ward')
hier_labels = hierarchical.fit_predict(X)

# ==========================================
# 4. Зниження розмірності (t-SNE) - 3D Візуалізація
# ==========================================
tsne = TSNE(n_components=3, random_state=42, perplexity=30)
X_tsne_3d = tsne.fit_transform(X)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
scatter = ax.scatter(X_tsne_3d[:, 0], X_tsne_3d[:, 1], X_tsne_3d[:, 2], 
                     c=y, cmap='viridis', s=50, edgecolor='k')
ax.set_title('t-SNE 3D Кластеризація Iris')
ax.set_xlabel('t-SNE Ознака 1')
ax.set_ylabel('t-SNE Ознака 2')
ax.set_zlabel('t-SNE Ознака 3')
legend1 = ax.legend(*scatter.legend_elements(), title="Справжні класи")
ax.add_artist(legend1)
plt.savefig('Lab5_tSNE_3D.png')

# ==========================================
# 5. DBSCAN та PCA
# ==========================================
# Знижуємо розмірність до 2 для зручної візуалізації DBSCAN
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# Підбір гіперпараметрів DBSCAN
# eps = радіус околу, min_samples = мін. точок для ядра кластера
# Оскільки датасет невеликий, eps треба брати помірним. Стандартний eps=0.5 часто склеює іриси або робить багато шуму.
dbscan = DBSCAN(eps=0.6, min_samples=4) 
dbscan_labels = dbscan.fit_predict(X_pca) # застосовуємо його на PCA ознаках

plt.figure(figsize=(8, 6))
# Шумові точки матимуть label = -1, інші = 0, 1, 2...
unique_labels = set(dbscan_labels)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        col = [0, 0, 0, 1] # Шум буде чорним
        label_name = 'Шум (Outliers)'
    else:
        label_name = f'Кластер {k}'
        
    class_member_mask = (dbscan_labels == k)
    xy = X_pca[class_member_mask]
    
    plt.scatter(xy[:, 0], xy[:, 1], c=[col], edgecolor='k', s=60, label=label_name)

plt.title('DBSCAN з PCA (eps=0.6, min_samples=4)')
plt.xlabel('Головна компонента 1')
plt.ylabel('Головна компонента 2')
plt.legend()
plt.savefig('Lab5_DBSCAN_PCA.png')

print("Виконання скрипту завершено. Усі графіки збережено в поточну директорію.")
