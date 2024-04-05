import frappe
from frappe.utils import now_datetime
import base64


def get_ura_efris_settings(doc):
    """Get the URA EFRIS Settings for the company

    Args:
        doc (obj): The document to
    Returns:
        tuple: The TIN, device number and URL for the company
    """

    if not doc.get("company"):
        doc.company = frappe.db.get_value("Global Defaults", None, "default_company")
    efris_settings = frappe.get_doc("Efris Settings Uganda", {"company": doc.company})
    tin = efris_settings.tin
    deviceNo = efris_settings.deviceno
    url = efris_settings.url
    return tin, deviceNo, url


def create_global_info(interfaceCode, deviceNo, tin):
    """Create the global info for the request to EFRIS

    Args:
        interfaceCode (str): The interface code for the request
        deviceNo (str): The device number for the request
        tin (str): The TIN for the request

    Returns:
        dict: The global info for the request
    """

    return {
        "appId": "AP01",
        "version": "1.1.20191201",
        "dataExchangeId": "9230489223014123",
        "interfaceCode": interfaceCode,
        "requestCode": "TP",
        "requestTime": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        "responseCode": "TA",
        "userName": "1016668923",
        "deviceMAC": "FFFFFFFFFFFF",
        "deviceNo": deviceNo,
        "tin": tin,
        "taxpayerID": "1",
        "longitude": "116.397128",
        "latitude": "39.916527",
        "extendField": {
            "responseDateFormat": "dd/MM/yyyy",
            "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
        },
    }


def create_data(base64message):
    """Create the data for the request to EFRIS

    Args:
        base64message (str): The base64 encoded message to send to EFRIS

    Returns:
        dict: The data for the request
    """
    return {
        "content": base64message,
        "signature": "",
        "dataDescription": {"codeType": "0", "encryptCode": "1", "zipCode": "0"},
    }


def b64encode(message):
    """Encode a message to base64

    Args:
        message (str): The message to encode

    Returns:
        str: The encoded message
    """
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("utf-8")


def get_main_content_from_reponse(response):
    """Get the main content from the response

    Args:
        response (obj): The response from EFRIS

    Returns:
        str: The main content from the response
    """
    response_json = response.json()
    response_data = response_json["data"]
    response_data_content = response_data["content"]
    content_encoded = response_data_content.encode("utf-8")
    base64_content_encoded = base64.b64decode(content_encoded)
    if response_data["dataDescription"]["zipCode"] == "1":
        import zlib

        base64_content_encoded = zlib.decompress(base64_content_encoded, 15 + 32)
    return base64_content_encoded.decode("utf-8")


def get_return_code_and_message(response):
    """Get the return code from the response

    Args:
        response (obj): The response from EFRIS

    Returns:
        tuple: The return code and message from the response
    """
    response_json = response.json()
    returnStateInfo = response_json["returnStateInfo"]
    returnMessage = returnStateInfo["returnMessage"]
    returnCode = returnStateInfo["returnCode"]
    return returnCode, returnMessage
