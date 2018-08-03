import torch
import torch.nn as nn
import torch.nn.functional as F

class SmallNet(nn.Module): # for 13x13

    def __init__(self):
        super(SmallNet, self).__init__()

        self.conv1 = nn.Conv2d(2, 6, 5) # 13x13 to 9x9
        self.conv2 = nn.Conv2d(6, 16, 3) # 9x9 to 7x7
        
        self.fc1 = nn.Linear(16 * 7 * 7, 169)

        self.activation = nn.Sigmoid()

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 16 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.activation(x)
        return x

class Net(nn.Module): # for 19x19

    def __init__(self):
        super(Net, self).__init__()

        self.conv1 = nn.Conv2d(2, 6, 7) # 19x19 to 13x13 (2 channels)
        self.conv2 = nn.Conv2d(6, 16, 5) # 13x13 to 9x9
        self.conv3 = nn.Conv2d(16, 96, 3) # 9x9 to 7x7
        
        self.fc1 = nn.Linear(96 * 7 * 7, 361)

        self.activation = nn.Sigmoid()

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = x.view(-1, 96 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.activation(x)
        return x
