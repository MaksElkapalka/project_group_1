import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

def generate_qr_code(url: str) -> StreamingResponse:
    """
    Generate a QR code from a given URL.
    
    :param url: The URL to encode in the QR code.
    :return: StreamingResponse containing the QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='yellow')

    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")