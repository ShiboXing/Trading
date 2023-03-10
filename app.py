from rumble.rumble.tech.domains import Domains
from rumble.rumble.datasets.dataset import rumbleset
from sota.computer_vision.models.vgg import VGG

import torch
from datetime import datetime


if __name__ == "__main__":
    rb = rumbleset()
    print(rb[3000])
    vgg = VGG(input_c=1).cuda()
    test = torch.rand((4, 1, 32, 200), dtype=torch.float).cuda()
    res = vgg(test)
    print(res)
