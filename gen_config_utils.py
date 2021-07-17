import os
import collections

ffrlEndpoints = collections.OrderedDict()

ffrlEndpoints["bb-b-fra2-fra"] = "185.66.194.1"
ffrlEndpoints["bb-b-ak-ber"] = "185.66.195.1"
ffrlEndpoints["bb-a-ix-dus"] = "185.66.193.0"
ffrlEndpoints["bb-a-fra2-fra"] = "185.66.194.0"
ffrlEndpoints["bb-b-ix-dus"] = "185.66.193.1"
ffrlEndpoints["bb-a-ak-ber"] =  "185.66.195.0"

def md(d):
    os.makedirs(d, exist_ok=True)
