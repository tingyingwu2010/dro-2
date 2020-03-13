"""
?Uses a face detector to crop the face only. This helps ensure that embeddings reflect
the users face, not other elements in the image (clothing, background), as much as
possible.

python3 scripts/detect_faces.py --img_dir /Users/jpgard/Documents/research/vggface2/train_partitioned_by_label/mouth_open_tiny/ --out_dir ./tmp/mouth_open_tiny_cropped
"""
from absl import app
from absl import flags
import glob
import numpy as np
import os

import tensorflow as tf

from mtcnn import MTCNN

# tf.compat.v1.enable_eager_execution()

AUTOTUNE = tf.data.experimental.AUTOTUNE
FLAGS = flags.FLAGS

flags.DEFINE_string("img_dir", None, "directory containing the images")
flags.DEFINE_string("out_dir", None, "directory to write new images to")


# Suppress the annoying tensorflow 1.x deprecation warnings; these make console output
# impossible to parse.
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
from PIL import Image
import re

face_detector = MTCNN()  # the detector to use below, using default weights


def extract_face(filename, required_size=(224, 224)):
    # load image from file
    pixels = Image.open(filename)
    pixels = np.array(pixels)
    # create the detector, using default weights
    # detect faces in the image
    results = face_detector.detect_faces(pixels)
    # extract the bounding box from the first face
    x1, y1, width, height = results[0]['box']
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    return image

def main(argv):
    out_dir = FLAGS.out_dir
    assert not out_dir.endswith("/"), "specify out_dir without a trailing /"
    filepattern = str(FLAGS.img_dir + '**/*.jpg')
    image_ids = glob.glob(filepattern, recursive=True)
    assert len(image_ids) > 0, "no images detected; try checking img_dir and filepattern."
    N = len(image_ids)
    for f in image_ids:
        try:
            face_im = extract_face(f)
            image_id = re.match('.*(.*/.*/.*\\.jpg)', f).group(1)
            out_fp = out_dir + image_id
            os.makedirs(os.path.dirname(out_fp), exist_ok=True)
            print("writing to %s" % out_fp)
            face_im.save(out_fp)
        except ValueError as e:
            print("[WARNING] crop error for {}; skipping".format(f))
            print(e)



if __name__ == "__main__":
    app.run(main)