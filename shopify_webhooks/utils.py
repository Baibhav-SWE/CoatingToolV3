import hmac
import hashlib
import base64


def validate_shopify_hmac(request, shared_secret):
    """
    Validate the Shopify HMAC signature of the incoming request.
    """
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    data = request.get_data()

    # Calculate the HMAC
    calculated_hmac = base64.b64encode(
        hmac.new(shared_secret.encode("utf-8"), data, hashlib.sha256).digest()
    ).decode()

    # Compare the calculated HMAC with the one provided in the request
    return hmac.compare_digest(hmac_header, calculated_hmac)
