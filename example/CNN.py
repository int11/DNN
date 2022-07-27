from INN import Model, transforms
import INN
from INN import layers as L
from INN import functions as F
import cv2 as cv
import numpy as np


def main_LeNet_5():
    class LeNet_5(Model):
        """
        frist typical CNN model
        input (32,32)
        real predict shape (28,28)
        it same current 4 padding algorithm
        """

        def __init__(self):
            super().__init__()
            self.conv1 = L.Conv2d(6, 5)
            self.conv2 = L.Conv2d(16, 5)
            self.conv3 = L.Conv2d(120, 5)
            self.fc4 = L.Linear(84)
            self.fc5 = L.Linear(10)

        def forward(self, x):
            x = F.tanh(self.conv1(x))
            x = F.average_pooling(x, kernel_size=2)
            x = F.tanh(self.conv2(x))
            x = F.average_pooling(x, kernel_size=2)
            x = F.tanh(self.conv3(x))

            x = F.reshape(x, (x.shape[0], -1))
            x = F.tanh(self.fc4(x))
            x = self.fc5(x)
            return x

    batch_size = 100
    epoch = 10
    transfrom = transforms.Compose(
        [transforms.ToOpencv(), transforms.Resize((32, 32)), transforms.ToArray(), transforms.ToFloat()])
    trainset = INN.datasets.MNIST(train=True, x_transform=transfrom)
    testset = INN.datasets.MNIST(train=False, x_transform=transfrom)

    train_loader = INN.dataloaders.DataLoader(trainset, batch_size, shuffle=True)
    test_loader = INN.dataloaders.DataLoader(testset, batch_size, shuffle=False)

    model = LeNet_5()
    optimizer = INN.optimizers.Adam().setup(model)

    for i in range(epoch):
        sum_loss, sum_acc = 0, 0

        for x, t in train_loader:
            y = model(x)
            loss = INN.functions.softmax_cross_entropy(y, t)
            acc = INN.functions.accuracy(y, t)
            model.cleargrads()
            loss.backward()
            optimizer.update()
            sum_loss += loss.data
            sum_acc += acc.data
        print(f'train loss {sum_loss / train_loader.max_iter} accuracy {sum_acc / train_loader.max_iter}')
        sum_loss, sum_acc = 0, 0

        with INN.no_grad():
            for x, t in test_loader:
                y = model(x)
                loss = INN.functions.softmax_cross_entropy(y, t)
                acc = INN.functions.accuracy(y, t)
                sum_loss += loss.data
                sum_acc += acc.data
        print(f'test loss {sum_loss / test_loader.max_iter} accuracy {sum_acc / test_loader.max_iter}')


class AlaxNet(Model):
    """
    first use Relu function
    """

    def __init__(self):
        super().__init__()
        self.conv1 = L.Conv2d(96, kernel_size=11, stride=4, pad=0)
        self.conv2 = L.Conv2d(256, kernel_size=5, stride=1, pad=2)
        self.conv3 = L.Conv2d(384, kernel_size=3, stride=1, pad=1)
        self.conv4 = L.Conv2d(384, kernel_size=3, stride=1, pad=1)
        self.conv5 = L.Conv2d(256, kernel_size=3, stride=1, pad=1)
        self.fc6 = L.Linear(4096)
        self.fc7 = L.Linear(4096)
        self.fc8 = L.Linear(1000)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.maxpooling(x, kernel_size=3, stride=2)
        x = F.batch_nrom(x)
        x = F.relu(self.conv2(x))
        x = F.maxpooling(x, kernel_size=3, stride=2)
        x = F.batch_nrom(x)
        x = self.conv5(self.conv4(self.conv3(x)))
        x = F.maxpooling(x, kernel_size=3, stride=2)

        x = F.reshape(x, (x.shape[0], -1))
        x = self.fc8(self.fc7(self.fc6(x)))
        return x
