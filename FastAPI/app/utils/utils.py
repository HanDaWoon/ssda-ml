import base64
import requests
from io import BytesIO

def from_image_to_bytes(img):
    """
    pillow image 객체를 bytes로 변환
    """
    # Pillow 이미지 객체를 Bytes로 변환
    imgByteArr = BytesIO()
    img.save(imgByteArr, format=img.format)
    imgByteArr = imgByteArr.getvalue()
    # Base64로 Bytes를 인코딩
    encoded = base64.b64encode(imgByteArr)
    # Base64로 ascii로 디코딩
    decoded = encoded.decode('ascii')
    return decoded