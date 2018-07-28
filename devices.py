#!/usr/bin/env python
# device demons of epic legandary counterparty blockchain streaming proportions... chris b peter j  devices.py

from flask import Flask, jsonify, request
import json
import requests
import sys
import optparse
import time
import urllib.parse
import urllib.request
from requests.auth import HTTPBasicAuth
#import sockets



#######################################


#Counterparty endpoint (default: coindaddy)
#
#Currently HTTP -- adjustable with: @app.route("/add-fednode", methods=['POST'])
#                                   def add_fednode():
url = "http://public.coindaddy.io:14000/"
headers = {'content-type': 'application/json'}
auth = HTTPBasicAuth('rpc', '1234')

#Bitcoin endpoint (default: coindaddy)
#
#Currently HTTP -- adjustable with: @app.route("/add-fednode", methods=['POST'])
#                                   def add_fednode():
urlB = "http://public.coindaddy.io:18332/"
headersB = {'content-type': 'application/json'}
authB = HTTPBasicAuth('rpc', '1234')

#Block explorer api
urlX = "https://testnet.xchain.io/api/"

#nothing to see here#
PHONE_PUB = 'msrt1G7TL2PwVNU7Qo8z7tmbLBDMfDBjXJ'
PHONE_PRV = 'cRT1HVbuPr9e2LjpLBUvVpmog7NWhMDjP7wQrgieMT1DJAtLkS3f'
GUN_PUB = 'n2RqFDvTFVYwxnMf3ZKytV3cGzP44vDATb'
GUN_PRV = 'cRNkCJh1dQ5sbM2PuymN8M1NixXa4VjSXGGaHAp8RL6byWe1hxxy'
DRONE_PUB = 'mkbzBXagaWpKZemjYWsTwjPiqTZXt2b7xi'
DRONE_PRV = 'cTFERWg7GLkvmJYi5AUowEYJtoNAmdj3FZigUdWjqJ7L2ZFHPBPz'
OTHER_PUB = 'mpyvYAWLaVfLfd36g2Fb6SgN5i6DqcFaao'
OTHER_PRV = 'cQxnzLmUQPPuocLKHuk9JgTgAnWdg61qXD518TxjFu14CuDCKxVa'

#HOST_PORTS_USED = {
#    'full': [8332, 18332, 4000, 14000, 4100, 14100, 8080, 443, 27017]


    
app = Flask(__name__)



### def is_port_open(port):
###    # TCP ports only
###    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###    return sock.connect_ex(('0.0.0.0', port)) == 0  # returns True if the port is open
    
#Input: formated issuance paramaters
#returns response from counterparty server
def counterparty_api_issuance(params):
    payload = {
        "method": 'create_issuance',
        "params": params,
        "jsonrpc": "2.0",
        "id": 0
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    pres = json.loads(response.text)
    hexString = pres['result']
    return hexString

#Input: formated send paramaters
#returns response from counterparty server
def counterparty_api_send(params):
    payload = {
        "method": 'create_send',
        "params": params,
        "jsonrpc": "2.0",
        "id": 0
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    pres = json.loads(response.text)
    hexString = pres['result']
    return hexString

#Input: unsigned hash and privatekey
#decode and signs tx using bitcoin server
#returns signed transaction
def decodeAndSign(hash_tx,prv):
    payloadB = {
        "method": "decoderawtransaction",
        "params": [hash_tx],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    rawTX = json.loads(responseB.text)
    tx_id = rawTX['result']['txid']
    scriptPubKey = rawTX['result']['vout'][0]['scriptPubKey']['asm']
    scriptPubKey = scriptPubKey.split(' ')[1]

    payloadB = {
        "method": "signrawtransaction",
        "params": [
            hash_tx,
            [{"txid":tx_id,
              "vout":0,
              "scriptPubKey": scriptPubKey,
              "redeemScript": None,
              "amount": 0.0001}],
            [prv]
        ],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    rawSigned = json.loads(responseB.text)
    signed_tx = rawSigned['result']['hex']
    return signed_tx

#Input: params for issuance
#broadcasts the transaction to bitcoin server
#returns tx_hash
def do_issuance(source, sourcePrv, asset, quantity, desc, div):
    unsigned_tx = counterparty_api_issuance({"source": source,"asset": asset,"quantity": quantity,"description": desc,"divisible": div})
    signed_tx = decodeAndSign(unsigned_tx,sourcePrv)
    new_tx_hash_issuance = signed_tx
    payloadB = {
        "method": "sendrawtransaction",
        "params": [signed_tx],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    tx_confirm_raw = json.loads(responseB.text)
    tx_confirm = tx_confirm_raw['result']
    return tx_confirm

#Input: params for ownership transfer
#broadcasts the transaction to bitcoin server
#returns tx_hash
##Untested
def do_transfer(source, sourcePrv, asset, quantity, desc, div):
    unsigned_tx = counterparty_api_issuance({"source": source, "asset": asset, "quantity": quantity, "description": desc, "divisible": div})
    signed_tx = decodeAndSignDev(unsigned_tx, sourcePrv)
    new_tx_hash_issuance = signed_tx
    payloadB = {
        "method": "sendrawtransaction",
        "params": [signed_tx],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    tx_confirm_raw = json.loads(responseB.text)
    tx_confirm = tx_confirm_raw['result']
    return tx_confirm

#Input: params for asset send
#broadcasts transaction to bitcoin server
#returns tx_hash
def do_send(source, sourcePrv, destination, asset, quantity, memo):
    unsigned_tx = counterparty_api_send({'source': source, 'destination': destination, 'asset': asset, 'quantity': quantity, 'memo': memo})
    signed_tx = decodeAndSign(unsigned_tx,sourcePrv)
    new_tx_hash_send = signed_tx
    payloadB = {
        "method": "sendrawtransaction",
        "params": [signed_tx],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    tx_confirm_raw = json.loads(responseB.text)
    tx_confirm = tx_confirm_raw['result']
    return tx_confirm

#Input: params for asset send device
#broadcasts the transaction to bitcoin server
#returns tx_hash
##Dev for devices
def do_send_device(source,sourcePrv, destination, asset, quantity, memo):
    unsigned_tx = counterparty_api_send({'source': source, 'destination': destination, 'asset': asset, 'quantity': quantity, 'memo': memo})
    signed_tx = decodeAndSignDev(unsigned_tx,sourcePrv)
    new_tx_hash_send = signed_tx
    payloadB = {
        "method": "sendrawtransaction",
        "params": [signed_tx],
        "jsonrpc": "2.0",
        "id": 0
    }
    responseB = requests.post(urlB, data=json.dumps(payloadB), headers=headersB, auth=authB)
    tx_confirm_raw = json.loads(responseB.text)
    tx_confirm = tx_confirm_raw['result']
    return tx_confirm

#Input: pubAddress
#returns all assets under that address
def get_assets(addr):
    payload = {
        "method": "get_balances",
        "params": {
            "filters": [{"field": "address", "op": "==", "value": addr}],
        },
        "jsonrpc": "2.0",
        "id": 0
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    raw_assets = json.loads(response.text)
    assets = raw_assets['result']
    return assets

#Input: asset name
#returns asset info
def get_asset_info(asset):
    payload = {
        "method": "get_asset_info",
        "params": {'assets':[asset]},
        "jsonrpc": "2.0",
        "id": 0
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    raw_assets_info = json.loads(response.text)
    assets_info = raw_assets_info['result']
    return assets_info

#Input: address
#pulls assets from counterparty server
#formats response
#returns [{'id': '', 'deviceName': '', 'deviceKey': '', 'deviceType': ''}]
def format_assets(address):
    all_assets = get_assets(address)
    build_list = []

    for x in all_assets:
        build_json = get_asset_info(x['asset'])[0]
        final_json = {'id': '', 'deviceName': '', 'deviceKey': '', 'deviceType': ''}
        
        if x['asset'] != 'XCP':
            final_json['id'] = x['asset']
            if build_json['asset_longname'] == None:
                final_json['deviceName'] = 'No name'
                final_json['deviceType'] = x['asset']
            else:
                name = build_json['asset_longname']
                nameL = name.split('.')
                final_json['deviceName'] = nameL[1]
                final_json['deviceType'] = nameL[0]
            final_json['deviceKey'] = build_json['description']
        build_list.append(final_json)
        
    return build_list

#Input: DeviceType-phone/gun/drone
#returns address and asset info
def handle_device_type(devType):
    if devType == 'phone':
        return ['SIOTPHONE',PHONE_PUB,PHONE_PRV]
    if devType == 'gun':
        return ['SIOTGUN',GUN_PUB,GUN_PRV]
    if devType == 'drone':
        return ['SIOTDRONE',DRONE_PUB,DRONE_PRV]
    return ['SIOTOTHER',OTHER_PUB,OTHER_PRV]



@app.route("/", methods=['GET', 'POST'])
def index():
    return jsonify({"about":"Hello World!"})

#Change sever info for counterparty
#'{"counterparty":"http://0.0.0.0:14000","user":"rpc", "pass":"rpc",}'
@app.route("/add-counterparty-server", methods=['POST'])
def add_counterparty():
    inj = request.get_json()
    url = inj['counterparty']
    auth = HTTPBasicAuth(inj['user'],inj['pass'])
    return inj

#Change sever info for bitcoin
#'{"bitcoin":"http://0.0.0.0:18332","user":"rpc", "pass":"rpc",}'
@app.route("/add-bitcoin-server", methods=['POST'])
def add_bitcoin():
    inj = request.get_json()
    urlB = inj['bitcoin']
    authB = HTTPBasicAuth(inj['user'],inj['pass'])
    return inj

#Input: '{"DeviceKey":"", "DeviceName":"", "DeviceType":"phone/gun/drone"}'
#Creates subasset from respective providers asset
#returns tx
@app.route("/add-device", methods=['POST'])
def add_device():
    inj = request.get_json()
    dataBuild = '{K:'+inj['DeviceKey']+'}'
    assetBuild = handle_device_type(inj['DeviceType'])

    tx_hash = do_issuance(assetBuild[1],assetBuild[2],assetBuild[0]+'.'+inj['DeviceName'], 1, dataBuild, False)
    return jsonify({'tx_hash': tx_hash}), 201

###################################################################################
# confirm tx is valid with /Check-tx/tx_hash before sending asset with /send-device
###################################################################################

#Input: '{"DeviceType":"phone/gun/drone","Address":"", "DeviceName":"", "data":"{key:value}"}'
#sends device asset token to address
#returns tx
@app.route("/send-device", methods=['POST'])
def send_device():
    inj = request.get_json()
    assetBuild = handle_device_type(inj['DeviceType'])
    
    tx_hash = do_send(assetBuild[1],assetBuild[2], inj['Address'], assetBuild[0]+'.'+inj['DeviceName'], 1 ,inj['data'])
    return jsonify({'tx_hash': tx_hash}), 201

#Input: hash_tx
#returns True or False for valid status
@app.route("/check-tx/<string:tx>", methods=['GET'])
def check_tx(tx):
    response = requests.get(urlX+'tx/'+tx)
    return str(response.json()['status'] == 'valid')

#retuns list of assets for address
#[{"DeviceType":"phone/gun/drone", "DeviceName":"", "DeviceKey":"", "DeviceID":""}]
@app.route('/get-devices/<string:pubname>', methods=['GET'])
def get_devices(pubname):
    out_assets = format_assets(pubname)
    return jsonify({'result':out_assets})

#Input: '{"addFrom":"","prvKey":"", "addTo":"", "name":"", "data":"{key:value}"}'
#sends asset "name" from "addFrom" to "addTo"
#returns tx
@app.route("/send", methods=['POST'])
def send():
    inj = request.get_json()

    tx_hash = do_send(inj['addFrom'], inj['prvKey'], inj['addTo'], inj['name'], 1 ,inj['data'])

    return jsonify({'tx_hash': tx_hash}), 201

##############
@app.route("/add-device-dev", methods=['POST'])
def add_device_dev():
    inj = request.get_json()
    dataBuild = '{K:'+inj['DeviceKey']+'}'
    assetBuild = handle_device_type(inj['DeviceType'])
    tx_hash = do_issuance(assetBuild[1],assetBuild[2],assetBuild[0]+'.'+inj['DeviceName'], 1, dataBuild, False)

    return jsonify({'tx_hash': tx_hash}), 201    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)