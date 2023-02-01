from sota.computer_vision.models.vgg import VGG

import torch.nn.modules.module

if __name__ == "__main__":
    vgg = VGG(input_c=1).cuda()
    test = torch.rand((4, 1, 40, 200), dtype=torch.float).cuda()
    res = vgg(test)
    print(res)
