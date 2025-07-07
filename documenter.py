from __future__ import annotations
from typing import Tuple, List
import re
import xlsxwriter
from PIL import Image
import os
import json
from profiler import get_keys
import fcntl
import subprocess


def append_json(thing, filename):
    with open(filename, 'a') as file:
        if isinstance(thing, list):
            json.dump(thing, file)
        else:
            json.dump([thing], file)
        file.write('\n')


def write_json(thing, filename):
    with open(filename, 'w') as json_file:
        json.dump(thing, json_file)


def read_json(filename):
    with open(filename, 'r') as file:
        try:
            fcntl.flock(file, fcntl.LOCK_EX)
            data = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)
            return data
        except:
            pass
    with open(filename, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        data = []
        for line in file:
            data += json.loads(line)
        fcntl.flock(file, fcntl.LOCK_UN)
        return data


def ftb(fold_file, ext="", extra=""):
    pwd = get_pwd()
    fold, file = fold_file
    if not file:
        return f"{pwd}/{fold}"
    if not ext:
        return f"{pwd}/{fold}/{file}"
    num = inc(ext, to_inc=False)
    if not extra:
        name = f"{pwd}/{fold}/{file}_{num}.{ext}"
    else:
        name = f"{pwd}/{fold}/{extra}_{file}_{num}.{ext}"
    return name


def inc(name, to_inc=True):
    pwd = get_pwd()
    inc_dir = f'{pwd}/inc'
    os.makedirs(inc_dir, exist_ok=True)
    filename = f'{inc_dir}/{name}_inc.txt'
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write('0')
        return '0'
    else:
        with open(filename, 'r') as file:
            num = int(file.read())
        if to_inc:
            num += 1
        with open(filename, 'w') as file:
            file.write(str(num))
        return str(num)


def get_pwd():
    return subprocess.check_output(['pwd']).decode().strip('\n')


def xlsx_creator(profiles: List[dict],
                 filename: str,
                 img_name: function) -> None:
    """
    precondition: searchable is homogeneous
    creates an xlsx document
    :param profiles: a list of results to go into a document
    :param filename: a name of a created document
    :param img_name: from url returns image name
    """
    if not profiles or not profiles[0]:
        print("Data set is empty, writing nothing")
        return
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(filename)
    wks = workbook.add_worksheet()
    # Start from the first cell
    regs = [r"image", r"price", r"link"]
    prior = [k for r in regs for k in get_keys(r, profiles[0])]
    oth = [k for k in profiles[0] if k not in prior]
    wks.write_row(0, 0, prior + oth)
    # Writing the data into a document
    row = 1
    for pf in profiles:
        col = 0
        for key in get_keys(r"image", pf):
            img = img_name(pf[key])
            add_image(wks, img, row, col)
            col += 1
        for key in get_keys(r"price", pf):
            wks.write(row, col, pf[key])
            col += 1
        for key in get_keys(r"link", pf):
            cell_width = 30
            wks.set_column(col, col, cell_width)
            wks.write(row, col, pf[key])
            col += 1
        for key in oth:
            wks.write(row, col, pf[key])
            col += 1
        row += 1
    workbook.close()


def add_image(wks, img, row, col):
    if not img:
        return
    if not os.path.exists(img):
        print("Could not find image:", img)
        return
    if not re.search(r"(KZ|jpg)$", img):
        print("This is not an image:", img)
        return
    # Resizing technique I got from SO
    im = Image.open(img)
    image_width, image_height = im.size
    cell_width, cell_height = 40, 140
    x = cell_width / image_width
    y = cell_height / image_height
    img_props = {
        'x_scale': x + .10,
        'y_scale': y,
        'x_offset': 100}
    # Inserting a scaled image
    wks.set_row(row, cell_height)
    wks.set_column(col, col, cell_width)
    wks.insert_image(row, col, img, img_props)
