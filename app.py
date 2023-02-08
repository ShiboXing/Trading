from rumble.rumble.tech.domains import Domains
from sota.computer_vision.models.vgg import VGG

from datetime import datetime
import torch.nn.modules.module


if __name__ == "__main__":
    d = Domains()
    rets = d.get_agg_rets("2023-01-10", "Technology", "sector")
    rets = d.get_index_rets("2023-01-03", "2023-02-03")

    vgg = VGG(input_c=1).cuda()
    test = torch.rand((4, 1, 32, 200), dtype=torch.float).cuda()
    res = vgg(test)
    print(res)
