import argparse
import os.path
import random
import PIL.Image
import PIL.ImageChops
import shutil

import imageio


def main(in_path, out_path, exported_width, exported_height) -> None:
    if not os.path.exists(in_path):
        return

    if os.path.exists(out_path):
        shutil.rmtree(out_path)

    os.mkdir(out_path)

    index = 0
    train_items = []

    for file_name in os.listdir(in_path):
        file_path = os.path.join(in_path, file_name)

        try:
            gif = imageio.mimread(file_path)
        except RuntimeError as e:
            print('{}: {}'.format(file_name, e))
            continue

        if len(gif) > 2:
            for i, im in enumerate(gif):
                image = PIL.Image.fromarray(im)

                if exported_width == image.width and exported_height == image.height:
                    train_image = image
                elif exported_width < image.width and exported_height < image.height:
                    x = (image.width - exported_width) // 2
                    y = (image.height - exported_height) // 2
                    train_image = image.crop((x, y, x + exported_width, y + exported_height))
                else:
                    assert exported_width > image.width or exported_height > image.height

                    width = get_unit_size(image.width)
                    height = get_unit_size(image.height)
                    box = (0, 0, image.width, image.height)
                    train_image = PIL.Image.new('RGB', (width, height), color=0xFFFFFF)
                    train_image.paste(image, box)

                if train_image.mode != 'RGB':
                    train_image = train_image.convert('RGB')

                gif[i] = train_image

            # image diff
            gif0 = gif[0]
            filtered = [gif0]

            for gif1 in gif[1:]:
                diff = PIL.ImageChops.difference(gif0, gif1)

                if diff.getbbox():
                    filtered.append(gif1)
                    gif0 = gif1

            if len(filtered) > 2:
                folder_name = '{:05d}'.format(index)
                folder_path = os.path.join(out_path, folder_name)
                os.mkdir(folder_path)
                train_items.append(folder_name)
                index += 1

                for i, im in enumerate(filtered):
                    i = str(i)
                    file_path = os.path.join(folder_path, i)
                    file_full_path = file_path + '.png'
                    im.save(file_full_path)

                # ani-gif make
                file_full_path = os.path.join(out_path, 'sample', '{}.gif'.format(folder_name))
                im = PIL.Image.new('RGB', (im.width, im.height), color=0xFFFFFF)
                im.paste(filtered[0])
                im.save(file_full_path, save_all=True, append_images=filtered[1:], duration=1000 // 30, loop=0,
                        dither=None, palette=PIL.Image.ADAPTIVE)

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


def copyGif():
    src_path = '\\\\10.10.53.214\\f\\[07] Monster design'
    path = "D:\\dot\\DAIN.data\\pixel_art_raw"

    for dir_path, dir_names, file_names in os.walk(src_path):
        for file_name in file_names:
            _, ext = os.path.splitext(file_name)

            if ext == '.gif':
                dest_path = os.path.join(path, file_name)

                if os.path.exists(dest_path):
                    continue

                src_path = os.path.join(dir_path, file_name)
                print(src_path)
                os.system("copy \"{}\" \"{}\" /y".format(src_path, dest_path))
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GIF a couple of frame extractor")
    parser.add_argument("-i", dest="in_path", required=False, default="resource", help="directory which ani-gif locate")
    parser.add_argument("-o", dest="out_path", required=False, default="resource_triplet", help="directory which frame save")
    parser.add_argument("--width", dest="width", required=False, default=0, help="image width", type=int)
    parser.add_argument("--height", dest="height", required=False, default=0, help="image height", type=int)
    args = parser.parse_args()

    width = args.width
    height = args.height

    if not width:
        width = height

    if not height:
        height = width

    main(args.in_path, args.out_path, width, height)