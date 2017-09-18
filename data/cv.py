import numpy as np

np.random.seed(8899)

data = {}
for i in range(10):
    data[i] = []

with open('train_data.data.shuffle', 'r') as f:
    for l in f:
        data[np.random.randint(10)].append(l)

for k in data:
    train = open('cv/train.' + str(k), 'w')
    test = open('cv/test.' + str(k), 'w')
    for j in data:
        if k != j:
            for i in data[j]:
                train.write(i)
        else:
            for i in data[j]:
                test.write(i)
    train.close()
    test.close()
