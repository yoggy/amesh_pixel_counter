import sys
import os
from io import BytesIO
import numpy as np
import cv2
from PIL import Image
import requests
import datetime
import json

if len(sys.argv) == 1:
    print("usage : amesh_pixel_counter.py mask.png");
    print()
    exit(1)

mask_filepath = sys.argv[1]

map_url        = "https://tokyo-ame.jwa.or.jp/map/map000.jpg"
overlay_url    = "https://tokyo-ame.jwa.or.jp/map/msk000.png"
lader_base_url = "https://tokyo-ame.jwa.or.jp/mesh/000/"
lader_ext      = ".gif"

def download_img(url):
    file, ext = os.path.splitext(url)
    ext = ext.lower()

    buf = requests.get(url).content

    if ext == ".jpg" or ext == ".jpeg" or ext == ".png":
        a = np.asarray(bytearray(buf), dtype=np.uint8)
        return cv2.imdecode(a, cv2.IMREAD_UNCHANGED)
    elif ext == ".gif":
        pil_img = Image.open(BytesIO(buf)).convert("RGBA")

        cv2_img = np.array(pil_img, dtype=np.uint8)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGBA2BGRA)
        return cv2_img
    else:
        raise "unknown image format..."

w = 770
h = 480 
channels = 4
shape = (h, w, channels)

# get map_img (JPG -> BGRA)
#map_img = download_img(map_url)
#map_img_b, map_img_g, map_img_r = cv2.split(map_img[:,:,:3])
#map_img_a = np.full((h, w, 1), 255, dtype=np.uint8)
#map_img = cv2.merge((map_img_b, map_img_g, map_img_r, map_img_a))

# get overlay_img (PNG, BGRA)
#overlay_img = download_img(overlay_url)

# get lader_img (GIF -> BGRA)
dt = datetime.datetime.now()
dt_1 = dt + datetime.timedelta(minutes=-1)
m = int((dt_1.minute)/5)*5 # Quantize every 5 minutes
lader_url = lader_base_url + dt.strftime("%Y%m%d%H") + ("%02d" % m) + lader_ext 
lader_img   = download_img(lader_url)
#print(lader_img.shape)

# alpha blending (for debug...)
#result_img = np.zeros(shape, dtype=np.uint8)
#result_img[0:h, 0:w] = map_img[0:h, 0:w] * (1 - lader_img[:, :, 3:]/255) + lader_img[0:h, 0:w] * (lader_img[:, :, 3:]/255)
#result_img[0:h, 0:w] = result_img[0:h, 0:w] * (1 - overlay_img[:, :, 3:]/255) + overlay_img[0:h, 0:w] * (overlay_img[:, :, 3:]/255)
#result_img = cv2.cvtColor(result_img, cv2.COLOR_BGRA2BGR)
#cv2.imwrite("./tmp/result.png", result_img) # for debug...

# count rainy pixels
lader_img = cv2.cvtColor(lader_img, cv2.COLOR_BGRA2GRAY)

mask_img = cv2.imread(mask_filepath)
mask_img = cv2.cvtColor(mask_img, cv2.COLOR_BGRA2GRAY)
masked_img = cv2.bitwise_and(lader_img, mask_img)
#cv2.imwrite("./tmp/masked.png", masked_img) # for debug...

count = cv2.countNonZero(masked_img)

d = {}
d["rainy_pixel_count"] = count
d["last_update_t"] = dt.isoformat()

print(json.dumps(d))

