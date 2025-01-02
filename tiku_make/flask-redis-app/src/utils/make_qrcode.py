import qrcode
from io import BytesIO
import base64

code = "https://jubilant-engine-r59p4g5x6gj3wxjq-5000.app.github.dev/"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(code)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

# to base64
buffered = BytesIO()
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
print(img_str)

# to file
img.save("qrcode.png")

