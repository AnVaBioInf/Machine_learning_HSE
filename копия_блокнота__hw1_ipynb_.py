# -*- coding: utf-8 -*-
"""Копия блокнота "HW1.ipynb"

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mi8fDDs9CBwTlWf5zDSc03JdqspA3CT1

# Home Work №1
Вам предстоит поработать с данными, описывающими биомеханические особенности ортопедических больных. Везде, где требуется написать свой код или ответ, помечено %%
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA

# Оставим вывод только двух чисел после запятой
pd.set_option('precision', 2)

"""## Шаг 1: Знакомство с таблицей"""

# Загрузим данные из файла column_2C_weka.csv
data = pd.read_csv("column_2C_weka.csv")

# Какой размер таблицы?
print(data.shape)

# Какие есть признаки в таблице? 
print(data.columns)

# Посмотрим первые несколько строк таблицы
data.head()

#Индивидуальный набор samplов размера 200, над которым будет проводиться дальнейшая работа
sample = data.sample(n=200)

"""## Шаг 2: Изучение на наличие нулевых значений"""

#Посмотрим на содержание данных относительно ненулевых значений
data.info()

# Какой столбец сильно выделяется?
# Ответ: 6:jump_height

#Посмотрим на первые несколько строк, где этот столбец is null
data['jump_height'][data['jump_height'].isnull()].head()

# Является ли он информативным? 
# Ответ: no

# Если нет, то удалите его
data2 = data.drop(labels = ['jump_height'], axis=1)  #### axis??

# Посмотрим на какой-нибудь еще один столбец, где есть нулевые значения
data['pelvic_incidence']

# Имеет ли смысл удалять всю стороку, где есть хотя бы один NaN, при условии, что данных мало?
# Ответ: No

# Если нет, то что можно сделать еще? Учитывая, что признаки являются количественными, что подойдет лучше всего?
# Ответ: to apply K-nearest neighbor model  
# A new sample is imputed by finding the samples in the training set “closest” to it and
# averages these nearby points to fill in the value. 
# or to replace NA with column mean

# Сделайте выбранное преобразование. Используйте fillna с переданным значение value = sample.mean()
sample = data2
value = sample['pelvic_incidence'].fillna(sample['pelvic_incidence'].mean())

# Посмотрим на содержание данных относительно ненулевых значений теперь
value.head()

"""## Шаг 3: сбалансированность классов"""

# Исследуем сбалансированность классов.
sample['class'].value_counts().plot(kind='bar')

# Все в порядке? 
# Ответ: Yes, classes are more or less balanced

"""## Шаг 4: Выбросы"""

# Исследуем данные на выбросы.
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(16, 10))

for idx, feat in  enumerate(sample.columns[:6]):
    sns.boxplot(x='class', y=feat, data=sample, ax=axes[int(idx / 3), idx % 3])
    axes[int(idx / 3), idx % 3].set_xlabel('class')
    axes[int(idx / 3), idx % 3].set_ylabel(feat);

# Имееются ли выбросы?
# Ответ: yes, there are outliers, they are showen as dots

# Посмотрим на смещение данных. 
sample[sample.columns[:6]].hist(figsize=(12,12));

# Какие признаки имеют смещение? Согласуются ли boxplot и histogram для признаков между собой?
# Ответ: pelvic_incidence, pelvic_tilt numeric (?), lumbar_lordosis_angle, degree_spondylolisthesis, sacral_slope (?) - 
# graphs are left skrewed
# Boxplots and histograms are in good agreement mean and data spread wise.

# Удалим выбросы, выступающие за границы 3 сигма
low = 0.01
high = 0.99
quant_data = sample.quantile([low, high])
for name in list(sample.drop(labels=['class'], axis=1).columns):
    sample = sample[(sample[name] > quant_data.loc[low, name]) & (sample[name] < quant_data.loc[high, name])]

# Посмотрим на смещение данных теперь
sample[sample.columns[:6]].hist(figsize=(12,12));

"""## Шаг 5: Scale"""

# Разделим таблицу на X и Y
X = sample.drop(labels=['class'], axis=1)
Y = sample['class']
# и на train и test  отношении 80/20 процентов
X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2, random_state = 42)

Y

X

# Проведем scaling данных
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_array = scaler.fit_transform(X_train)
X_train = pd.DataFrame(X_train_array, index=X_train.index, columns=X_train.columns)

X_test_array = scaler.fit_transform(X_test)
X_test = pd.DataFrame(X_test_array, index=X_test.index, columns=X_test.columns)

# Посмотрим на гистограммы признаков
X_train[X_train.columns[:6]].hist(figsize=(12,12));

# Что изменилось?
# Ответ: data became normalized

"""## Шаг 6: PCA"""

# Создайте класс PCA для шести компонент и обучите на X_train
pca = PCA(n_components=6) 
pca.fit(X_train)

# Проведите трансформацию PCA
X_train_pca = pca.transform(X_train)
X_test_pca = pca.transform(X_test)

# Построим bar plot
plt.bar(range(pca.n_components_), pca.explained_variance_)
plt.xlabel('PCA feature')
plt.ylabel('variance')
plt.show()

# Переведем Y_train в числовые значения
d = dict(zip(set(Y_train), [0,1]))
label = list()
for i in Y_train:
    label.append(d[i])

# И построим на двух компонентах
plt.figure(figsize=(10,7))
plt.scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=label, s=70, cmap='viridis')
plt.show()

# Постойте попарно 1-2, 2-3, 1-3 компоненты

fig, ax=plt.subplots(nrows=2, ncols=2, figsize=(20,20))

# fig.suptitle('')
ax[0,0].scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=label, s=70, cmap='viridis')
ax[0,0].set_title('1 vs 2')

ax[0,1].scatter(X_train_pca[:, 1], X_train_pca[:, 2], c=label, s=70, cmap='viridis')
ax[0,1].set_title('2 vs 3')

ax[1,0].scatter(X_train_pca[:, 0], X_train_pca[:, 2], c=label, s=70, cmap='viridis')
ax[1,0].set_title('1 vs 3')

# Выведите, сколько компонент объясняют >95% variance
for i in range(6):
    print( str(i) + ' parameters managed to capture: ' + 
    str(sum(pca.explained_variance_ratio_[:i]))[:5] + ' of explained variance')