#!/usr/bin/env python

from yahoo_finance import Share

print(Share('HLIT').get_price())