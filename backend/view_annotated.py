import base64
import json

import cv2
import numpy as np


with open("output_fast_annotated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

img_b64 = data.get("annotated_image")
if not img_b64:
    raise ValueError("No annotated_image field found in output_fast_annotated.json")

img_bytes = base64.b64decode(img_b64)
img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

if img is None:
    raise ValueError("Failed to decode annotated image")

cv2.imshow("Annotated Fast Vision Output", img)
cv2.waitKey(0)
cv2.destroyAllWindows()