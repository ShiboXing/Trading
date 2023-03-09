from rumble.rumble.tech.domains import Domains
from rumble.rumble.datasets.dataset import rumbleset
from sota.computer_vision.models.vgg import VGG

from datetime import datetime


if __name__ == "__main__":
    d = Domains()
    d.update_agg_dates(is_industry=True)
    d.update_agg_dates(is_industry=False)

    # agg_rets = d.write_agg_rets("2023-01-10", "Technology", "sector")
    d.update_agg_signals(is_sector=True)
    pass
    # index_rets = d.get_index_rets("2023-01-03", "2023-02-03")

    # rb = rumbleset()
    # print(rb[3000])
    # vgg = VGG(input_c=1).cuda()
    # test = torch.rand((4, 1, 32, 200), dtype=torch.float).cuda()
    # res = vgg(test)
    # print(res)
