import os.path
from .listdatasets import ListDataset,Pixel_art_loader


def make_dataset(root, list_file):
    raw_im_list = open(os.path.join(root, list_file)).read().splitlines()
    # the last line is invalid in test set.
    # print("The last sample is : " + raw_im_list[-1])
    raw_im_list = raw_im_list[:-1]
    assert len(raw_im_list) > 0

    return  raw_im_list


def Pixel_art_interp(root, split=1.0, single=False, task = 'interp'):
    train_list = make_dataset(root,"train_list.txt")
    test_list = make_dataset(root, "test_list.txt")
    train_dataset = ListDataset(root, train_list, loader=Pixel_art_loader)
    test_dataset = ListDataset(root, test_list, loader=Pixel_art_loader)
    return train_dataset, test_dataset
