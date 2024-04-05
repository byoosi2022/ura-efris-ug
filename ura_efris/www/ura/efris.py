# -*- coding: utf-8 -*-
# Copyright (c) 2022, mututa paul and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe

from frappe import _, throw, msgprint
from frappe.utils import nowdate

import six
from six import string_types

import base64

import requests
import json

url = "http://192.168.1.179:9880/efristcs/ws/tcsapp/getInformation"
class ItemDoc(Document):
	def before_save(self,doctype=None):
		# frappe.msgprint(_("Thanks your Data has been sent to Efris + base64_string"))
		dataitem =[{
        "operationType": "101",
    	"goodsName": "MUTUTA BYOOSI FINAL POSTING",
    	"goodsCode": "3768070",
    	"measureUnit": "115",
    	"unitPrice": "9000",
    	"currency": "101",
    	"commodityCategoryId": "10111301",
    	"haveExciseTax": "102",
    	"description": "1",
    	"stockPrewarning": "10",
    	"pieceMeasureUnit": "",
    	"havePieceUnit": "102",
    	"pieceUnitPrice": "",
    	"packageScaledValue": "",
    	"pieceScaledValue": "",
    	"exciseDutyCode": "",
    	"haveOtherUnit": "102",
    	"goodsTypeCode": "101"
        }]
		temp = json.dumps(dataitem)
		message_bytes = temp.encode('ascii')
		base64_bytes = base64.b64encode(message_bytes)
		base64_message = base64_bytes.decode('ascii')
		data ={
		"data":{
		"content": base64_message,
 		"signature": "",
 		"dataDescription": {
	    "codeType": "0",
 		"encryptCode": "1",
 		"zipCode": "0"
		  }  
		 },
		"globalInfo": {
 		"appId": "AP01",
		"version": "1.1.20191201",
 		"dataExchangeId": "9230489223014123",
 		"interfaceCode": "T130",
 		"requestCode": "TP",
 		"requestTime": "2022-12-30 16:29:07",
 		"responseCode": "TA",
 		"userName": "1016668923",
 		"deviceMAC": "FFFFFFFFFFFF",
		"deviceNo": "TCS096646781232438",
 		"tin": "1016668923",
		"taxpayerID": "1",
		"longitude": "116.397128",
		"latitude": "39.916527",
		"extendField": {
 		"responseDateFormat": "dd/MM/yyyy",
 		"responseTimeFormat": "dd/MM/yyyy HH:mm:ss"
		}
		},
		"returnStateInfo": {
 		"returnCode": "",
	    "returnMessage": ""
 		}
		}
		response = requests.post(url,json=data)
		frappe.msgprint(_("Thanks your Data has been sent to Efris <br>" + base64_message))
    #  temp = json.dumps(dataitem)
    #  data_bytes = temp.encode('ascii')
    #  base64_bytes = base64.base64encode(data_bytes)
    #  base64_string = base64_bytes.decode(ascii)
	# pass

