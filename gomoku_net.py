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

        self.conv1 = nn.Conv2d(2, 20, 5) # 19x19 to 15x15 (2 channels)
        self.conv2 = nn.Conv2d(20, 20, 5) # 15x15 to 11x11
        self.conv3 = nn.Conv2d(20, 50, 5) # 11x11 to 7x7
        
        self.fc1 = nn.Linear(50 * 7 * 7, 362)

        self.policy_activation = nn.Sigmoid()
        self.value_activation = nn.Tanh()

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = x.view(-1, 50 * 7 * 7)
        x = self.fc1(x)
        y = self.policy_activation(x[:, :361])
        z = self.value_activation(x[:, 361].unsqueeze(1))
        x = torch.cat((y, z), 1)
        return x
