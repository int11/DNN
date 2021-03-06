from INN import Model, transforms
import INN
from INN import layers as L
from INN import functions as F
import cv2 as cv
import numpy as np


class LeNet_5(Model):
    """
    1998, LeCun
    frist typical CNN model
    input (32,32)
    real predict shape (28,28)
    it same current 4 padding algorithm
    use Tanh activation function
    use average Pooling
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
        x = F.max_pooling(x, kernel_size=2)
        x = F.tanh(self.conv2(x))
        x = F.max_pooling(x, kernel_size=2)
        x = F.tanh(self.conv3(x))

        x = F.reshape(x, (x.shape[0], -1))
        x = F.tanh(self.fc4(x))
        x = self.fc5(x)
        return x


class AlexNet(Model):
    """
    2012, Alex Krizhevsky
    use Relu activation function - Shoter Training Time
    use Max Pooling
    GPU use
    """

    def __init__(self):
        super().__init__()
        self.conv1 = L.Conv2d(96, kernel_size=11, stride=4, pad=0)
        self.batchnorm1 = L.BatchNorm()
        self.conv2 = L.Conv2d(256, kernel_size=5, stride=1, pad=2)
        self.batchnorm2 = L.BatchNorm()
        self.conv3 = L.Conv2d(384, kernel_size=3, stride=1, pad=1)
        self.conv4 = L.Conv2d(384, kernel_size=3, stride=1, pad=1)
        self.conv5 = L.Conv2d(256, kernel_size=3, stride=1, pad=1)
        self.fc6 = L.Linear(4096)
        self.fc7 = L.Linear(4096)
        self.fc8 = L.Linear(10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.local_response_normalization(x)
        # x = self.batchnorm1(x)
        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.relu(self.conv2(x))
        x = F.local_response_normalization(x)
        # x = self.batchnorm2(x)
        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))

        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.reshape(x, (x.shape[0], -1))
        x = F.dropout(F.relu(self.fc6(x)))
        x = F.dropout(F.relu(self.fc7(x)))
        x = self.fc8(x)
        return x

class ZFNet(Model):
    """
    2013, Zeiler and Fergus
    AlexNet -> ZFNet
    CONV1 : (11, 11) Kernel size, 4 strid -> (7, 7) Kernel size, 2 strid
    CONV3,4,5 : 384, 384, 256  out channels -> 512, 1024, 512 out channels
    """

    def __init__(self):
        super().__init__()
        self.conv1 = L.Conv2d(96, kernel_size=7, stride=2, pad=0)
        self.batchnorm1 = L.BatchNorm()
        self.conv2 = L.Conv2d(256, kernel_size=5, stride=1, pad=2)
        self.batchnorm2 = L.BatchNorm()
        self.conv3 = L.Conv2d(512, kernel_size=3, stride=1, pad=1)
        self.conv4 = L.Conv2d(1024, kernel_size=3, stride=1, pad=1)
        self.conv5 = L.Conv2d(512, kernel_size=3, stride=1, pad=1)
        self.fc6 = L.Linear(4096)
        self.fc7 = L.Linear(4096)
        self.fc8 = L.Linear(10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.local_response_normalization(x)
        # x = self.batchnorm1(x)
        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.relu(self.conv2(x))
        x = F.local_response_normalization(x)
        # x = self.batchnorm2(x)
        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))

        x = F.max_pooling(x, kernel_size=3, stride=2)

        x = F.reshape(x, (x.shape[0], -1))
        x = F.dropout(F.relu(self.fc6(x)))
        x = F.dropout(F.relu(self.fc7(x)))
        x = self.fc8(x)
        return x

def main_LeNet():
    batch_size = 100
    epoch = 10
    transfrom = transforms.compose(
        [transforms.toOpencv(), transforms.resize((32, 32)), transforms.toArray(), transforms.toFloat()])
    trainset = INN.datasets.MNIST(train=True, x_transform=transfrom)
    testset = INN.datasets.MNIST(train=False, x_transform=transfrom)

    train_loader = INN.iterators.iterator(trainset, batch_size, shuffle=True)
    test_loader = INN.iterators.iterator(testset, batch_size, shuffle=False)

    model = LeNet_5()
    optimizer = INN.optimizers.Adam().setup(model)

    if INN.cuda.gpu_enable:
        model.to_gpu()
        train_loader.to_gpu()
        test_loader.to_gpu()

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
            print(loss.data)
        print(f"epoch {i + 1}")
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


def main_AlexNet():
    batch_size = 100
    epoch = 10
    transfrom = transforms.compose(
        [transforms.toOpencv(), transforms.resize(227), transforms.toArray(), transforms.toFloat(),
         transforms.z_Score_Normalize(0.5, 0.5)])
    trainset = INN.datasets.CIFAR10(train=True, x_transform=transfrom)
    testset = INN.datasets.CIFAR10(train=False, x_transform=transfrom)
    train_loader = INN.iterators.iterator(trainset, batch_size, shuffle=True)
    test_loader = INN.iterators.iterator(testset, batch_size, shuffle=False)

    model = AlexNet()
    optimizer = INN.optimizers.Adam(alpha=0.0001).setup(model)

    if INN.cuda.gpu_enable:
        model.to_gpu()
        train_loader.to_gpu()
        test_loader.to_gpu()

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
            print(f"loss : {loss.data} accuracy {acc.data}")
        print(f"epoch {i + 1}")
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
