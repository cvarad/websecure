#!/usr/bin/env python

import os
import argparse
import requests
import time

URL = 'https://unsplash.it/'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('width', type=int, help='Width of the image')
    parser.add_argument('height', type=int, help='Height of the image')
    parser.add_argument('-r', '--random', dest='random', action='store_true', help='Get a random image')
    parser.add_argument('-g', '--grey', dest='grey', action='store_true', help='Get a greyscale image')
    parser.add_argument('-n', '--number', type=int, dest='number', help='Set the number of images to download. Default = 5')
    parser.add_argument('-t', '--time', type=int, dest='time', help='Time between image downloads (in milliseconds). Default = 100')
    parser.add_argument('-d', '--dir', type=str, dest='path', help='Directory where the images should be saved. Default: Current Dir')

    parser.set_defaults(random=False, grey=False, number=5, time=100, path=os.getcwd())
    return parser.parse_args()


def set_url(args):
    global URL
    if args.grey:
        URL += 'g/'

    if args.width == args.height:
        URL += str(args.width) + '/'
    else:
        URL += str(args.width) + '/' + str(args.height) + '/'

    if args.random:
        URL += '?random'


def dl_image(args, image_num):
    image = requests.get(URL)
    save_image(image, args.path, image_num)


def save_image(image, path, image_num):
    filename = os.path.join(path, 'unsplash' + image_num)
    with open(filename, 'wb') as f:
        f.write(image.content)
        f.close()


if __name__ == '__main__':
    args = get_args()
    set_url(args)

    path = args.path
    if not os.path.isdir(path):
        raise Exception

    s = len(os.listdir(path))
    e = s + args.number
    for i in range(s, e):
        dl_image(args, str(i))
        time.sleep(args.time/1000.0)
