import argparse
import os.path
import random
import PIL.Image
import shutil

import imageio


def main(in_path, out_path, width, height) -> None:
    if not os.path.exists(in_path):
        return

    if os.path.exists(out_path):
        shutil.rmtree(out_path)

    os.mkdir(out_path)

    index = 0
    train_items = []

    for file_name in os.listdir(in_path):
        file_path = os.path.join(in_path, file_name)
        gif = imageio.mimread(file_path)

        if len(gif) > 2:
            im0 = gif[0]
            im1 = gif[1]
            im2 = gif[2]

            folder_name = '{:05d}'.format(index)
            folder_path = os.path.join(out_path, folder_name)
            os.mkdir(folder_path)
            train_items.append(folder_name)

            for i, im in enumerate((im0, im1, im2)):
                i = str(i)
                file_path = os.path.join(folder_path, i)
                file_full_path = file_path + '.png'
                image = PIL.Image.fromarray(im)

                if width and height:
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    train_image = image.resize((width, height))
                else:
                    width = get_unit_size(image.width)
                    height = get_unit_size(image.height)
                    box = (0, 0, image.width, image.height)
                    train_image = PIL.Image.new('RGB', (width, height), color=0xFFFFFF)
                    train_image.paste(image, box)

                train_image.save(file_full_path)

            index += 1

            print(folder_path)

    file_path = os.path.join(out_path, 'train_list.txt')
    with open(file_path, 'w') as f:
        text = '\n'.join(train_items)
        f.write(text)

    file_path = os.path.join(out_path, 'test_list.txt')
    with open(file_path, 'w') as f:
        random.shuffle(train_items)
        choice_count = len(train_items) // 5
        test_items = train_items[:choice_count]
        test_items = sorted(test_items)
        text = '\n'.join(test_items)
        f.write(text)


def get_unit_size(value):
    v = 2

    while True:
        if v >= value:
            return v
        else:
            v *= 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GIF a couple of frame extractor")
    parser.add_argument("-i", dest="in_path", required=False, default="resource", help="directory which ani-gif locate")
    parser.add_argument("-o", dest="out_path", required=False, default="resource_triplet", help="directory which frame save")
    parser.add_argument("--width", dest="width", required=False, default='', help="image width", type=int)
    parser.add_argument("--height", dest="height", required=False, default='', help="image height", type=int)
    args = parser.parse_args()

    width = args.width
    height = args.height

    if not width:
        width = height

    if not height:
        height = width

    main(args.in_path, args.out_path, width, height)