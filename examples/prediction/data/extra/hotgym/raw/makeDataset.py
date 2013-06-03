#! /usr/bin/env python
# ---------------------------------------------------------------------- 
#  Copyright (C) 2011 Numenta Inc. All rights reserved.
#
#  The information and source code contained herein is the
#  exclusive property of Numenta Inc. No part of this software
#  may be used, reproduced, stored or distributed in any form,
#  without explicit written authorization from Numenta Inc.
# ----------------------------------------------------------------------

"""Unify the various HotGym CSV files to a single coherent StandardFile

See README.txt for details
"""

import os
import sys

import glob
import operator
import datetime
"""from nupic.providers.WeatherProvider import (
  WeatherStation,
  getClosestStation)
"""

from nupic.data.file import File

  
def fixEOL(f):
  """Make sure the end of line character is '\n'
  
  This is needed in order to use fileinput.input() to process the files. The
  file format of the raw gym dataset unfortunately contains \r (old Mac format)
  EOL characters.
  """
  text = open(f).read()
  
  # If there are no carriage returns (\r) just return
  if text.find('\r') == -1:
    return
  # Takes care of Windows format
  text = text.replace('\r\n', '\n')
  # Takes care of old Mac format
  text = text.replace('\r', '\n')
  
  open(f, 'w').write(text)


def _parseTimestamp(t):
  tokens = t.split()
  day, month, year = [int(x) for x in tokens[0].split('/')]
  if len(tokens) == 1:
    hour = 0
    minute = 0
  else:
    assert len(tokens) == 3  
    hour, minute, seconds = [int(x) for x in tokens[1].split(':')]
    hour %= 12
    if tokens[2] == 'PM':
      hour += 12
      
  result = datetime.datetime(year, month, day, hour, minute)
  
  assert datetime.datetime(2010, 7, 2) <= result < datetime.datetime(2011, 1, 1)
  return result 
      

def _parseLine(line):
  # Get rid of the double quotes arounf each field
  line = line.replace('"', '')
  
  # Split the line and get rid of the first field (running count)
  fields = line[:-1].split(',')[1:]

  gym = fields[0]
  record = [gym] # Gym
  
  # Add in an address for each Gym
  
  gymAddresses = {
    'Balgowlah Platinum':	'Shop 67 197-215 Condamine Street Balgowlah 2093',
    'Lane Cove': '24-28 Lane Cove Plaza Lane Cove 2066',
    'Mosman': '555 Military Rd Mosman 2088',
    'North Sydney - Walker St': '100 Walker St North Sydney 2060',
    'Randwick':	'Royal Randwick Shopping Centre 73 Belmore Rd Randwick 2031'
  }
  
  address = gymAddresses[gym]
  record.append(address)
  
  # Parse field 2 to a datetime object
  record.append(_parseTimestamp(fields[1]))
  
  # Add the consumption
  record.append(float(fields[2]))
  
  return record

def makeDataset():
  """
  """
  inputFile = 'numenta_air_Con.csv'
  fixEOL(inputFile)
  
  fields = [
    ('gym', 'string', 'S'),
    ('address', 'string', ''),
    ('timestamp', 'datetime', 'T'),
    ('consumption', 'float', '')]
  
  gymName = None
  
  missing = 0
  total = 0
  # Create a the output file by parsing the customer given csv
  with File('./hotgym2.csv', fields) as o:
    with open(inputFile) as f:
      # Skip header
      f.readline()
      
      # iterate over all the lines in the input file
      for line in f.xreadlines():
        
        # Parse the fields in the current line
        record = _parseLine(line)

        # Write the merged record to the output file
        o.write(record)
        
        if record[0] != gymName:
          gymName = record[0]
          print gymName
 		  
  return total, missing
  
  
if __name__ == '__main__':
  makeDataset()
  
  print 'Done.'
  
