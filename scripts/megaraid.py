#!/usr/bin/env python
"""
Python library for MegaCli
This is a simple Python library that wraps around MegaCli to provide an OO interface.
@author: lijingwei9060@qq.com
"""

import os
import re
import subprocess

class MegaCLIError(Exception):
  pass

class MegaCLI:
  def __init__(self, cli_path = '/opt/MegaRAID/MegaCli/MegaCli64'):
    """
    Construct a new 'MegaCLI' object
    :param cli_path: path to MegaCli executable
    :type cli_path: string
    :return: nothing
    """
    self.cli_path = cli_path

    if not os.path.exists(cli_path):
      raise RuntimeError('{0} not found'.format(cli_path))

  def execute(self, cmd):
    """
    Execute a MegaCLI command
    :param cmd: command line arguments for MegaCLI
    :type cmd: string
    :return: MegaCLI command output
    :rtype: int
    """
    proc = subprocess.Popen("{0} {1} -NoLog".format(self.cli_path, cmd), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    if isinstance(out, bytes):
      out = out.decode(errors="ignore")
    if isinstance(err, bytes):
      err = err.decode(errors="ignore")

    if proc.returncode:
      ex = MegaCLIError(err.rstrip())
      ex.exitcode = proc.returncode
      raise ex
    else:
      return [re.sub(':$', '', re.sub('\s*:\s*', ':', re.sub('(^\s*|\s*$)', '', line)).lower()) for line in filter(None, out.rstrip().split("\n"))]

  def __raid_level(self, level):
    """
    Map a RAID level string to a RAID level integer
    :param level: RAID level
    :type level: string
    :return: RAID level
    :rtype: int
    """

    levels = {
      'primary-0, secondary-0, raid level qualifier-0': 0,
      'primary-1, secondary-0, raid level qualifier-0': 1,
      'primary-5, secondary-0, raid level qualifier-3': 5,
      'primary-6, secondary-0, raid level qualifier-3': 6,
      'primary-1, secondary-3, raid level qualifier-0': 10,
    }

    if level in levels:
      return levels[level]
    else:
      return None

  def __to_property(self, key, value):
    """
    Decode raw MegaCLI key value pairs into properties
    :param key: raw property name
    :type key: string
    :param value: raw property value
    :type value: string
    :return: decoded property name and value
    """
    k = key.replace(' ', '_').replace("'s", '').replace('.', '').replace('/', '_').replace('&', 'and')

    if value == 'n/a' or value == 'none':
      return k, None

    if value == 'yes':
      return k, True

    if value == 'no':
      return k, False

    # deal with integers
    m = re.match('^(\d+)\s*%?$', value)
    if m:
      return k, int(m.group(1))

    # deal with floats
    m = re.match('^(\d+)(?:\.\d+)?\s*%?$', value)
    if m:
      return k, float(m.group(1))

    # deal with temperatures
    if re.match('.*temperature.*', key):
      m = re.match('^(\d+)\s*(?:c|degree celcius)', value)
      if m:
        return k, int(m.group(1))

    # deal with sizes
    m = re.match('^(\d+(?:\.\d+)?)\s*(b|kb|mb|gb|tb|pb)', value)
    if m:
      size = float(m.group(1))
      unit = m.group(2)

      multiplier = 1
      if unit == 'kb':
        multiplier = 1024
      elif unit == 'mb':
        multiplier = 1024 * 1024
      elif unit == 'gb':
        multiplier = 1024 * 1024 * 1024
      elif unit == 'tb':
        multiplier = 1024 * 1024 * 1024 * 1024
      elif unit == 'pb':
        multiplier = 1024 * 1024 * 1024 * 1024 * 1024

      return k, (size * multiplier)

    # deal with times
    m = re.match('^(\d+)\s*(s|sec|secs|seconds|m|min|mins|minutes|h|hour|hours|d|day|days)$', value)
    if m:
      time = int(m.group(1))
      unit = m.group(2)

      multiplier = 1
      if unit == 'm' or unit == 'min' or unit == 'minute' or unit == 'mins' or unit =='minutes':
        mutiplier = 60
      elif unit == 'h' or unit == 'hour' or unit == 'hours':
        mutiplier = 60 * 60
      elif unit == 'd' or unit == 'day' or unit == 'days':
        mutiplier = 60 * 60 * 24

      return k, (time * multiplier)

    return k, value

  def __array_to_dic(self, arr, prefix, separator = '.'):
    ret = {}
    for i in range(len(arr)):
      ret.update({ prefix + separator + str(i) + separator + k : v for k,v in arr[i].items()})
      
    ret.update({prefix + separator + 'count' : len(arr)})
    return ret

  def enclosures(self):
    """
    Get enclosures
    :return: a list of all available enclosures
    :rtype: list
    """
    ret = []

    data = self.execute("-EncInfo -aALL")
    if data:
      adapter_id = None
      enc = {}

      for line in data:
        m = re.match('^number of enclosures on adapter (\d+) --', line)
        if m:
          if 'adapter_id' in enc:
            ret.append(enc)
            enclosure = {}

          enc['adapter_id'] = int(m.group(1))
          adapter_id = enc['adapter_id']
          continue

        if adapter_id is not None:
          m = re.match('^enclosure (\d+)', line)
          if m:
            if 'id' in enc:
              ret.append(enc)
              enc = {'adapter_id': adapter_id}

            enc['id'] = int(m.group(1))
            continue

          if 'id' in enc:
            fields = line.split(':', 1)
            if len(fields) > 1:
              k, v = self.__to_property(*fields)

              if k == 'exit_code':
                continue

              enc[k] = v

      if len(enc):
        ret.append(enc)

    return self.__array_to_dic(arr=ret,prefix='enclosures')

  def logicaldrives(self):
    """
    Get logical drives
    :return: a list of all configured logical drives
    :rtype: list
    """
    ret = []

    data = self.execute("-LDInfo -LAll -aAll")
    if data:
      adapter_id = None
      ld = {}

      for line in data:
        m = re.match('^adapter (\d+) -- virtual drive information$', line)
        if m:
          if 'adapter_id' in ld:
            ret.append(ld)
            ld = {}

          ld['adapter_id'] = int(m.group(1))
          adapter_id = ld['adapter_id']
          continue

        if adapter_id is not None:
          m = re.match('^virtual drive:(\d+)', line)
          if m:
            if 'id' in ld:
              ret.append(ld)
              ld = {'adapter_id': adapter_id}

            ld['id'] = int(m.group(1))
            continue

          if 'id' in ld:
            fields = line.split(':', 1)
            if len(fields) > 1:
              k, v = self.__to_property(*fields)

              if k == 'exit_code':
                continue

              if k == 'raid_level':
                level = self.__raid_level(v)
                if level is not None:
                  v = level

              ld[k] = v
              continue

      if len(ld):
        ret.append(ld)

    return self.__array_to_dic(arr=ret,prefix='lds')

  def physicaldrives(self):
    """
    Get physical drives
    :return: a list of all installed physical drives
    :rtype: list
    """
    ret = []

    data = self.execute("-PDList -aAll")
    if data:
      adapter_id = None
      pd = {}

      for line in data:
        m = re.match('^adapter #(\d+)', line)
        if m:
          if 'adapter_id' in pd:
            ret.append(pd)
            pd = {}

          pd['adapter_id'] = int(m.group(1))
          adapter_id = pd['adapter_id']
          continue

        if adapter_id is not None:
          m = re.match('^enclosure device id:(\d+|n\/a)', line)
          if m:
            if 'enclosure_id' in pd:
              ret.append(pd)
              pd = {'adapter_id': adapter_id}

            pd['enclosure_id'] = int(m.group(1)) if m.group(1) != "n/a" else 0
            continue

          if 'enclosure_id' in pd:
            fields = line.split(':', 1)
            if len(fields) > 1:
              k, v = self.__to_property(*fields)

              if k == 'exit_code':
                continue

              pd[k] = v

      if len(pd):
        ret.append(pd)

    return self.__array_to_dic(arr=ret,prefix='pds')

  def bbu(self):
    """
    Get battery backup units
    :return: a list of all installed BBUs
    :rtype: list
    """
    ret = []

    data = self.execute("-AdpBbuCmd  -aAll")
    if data:
      bbu = {}

      for line in data:
        m = re.match('^bbu status for adapter:(\d+)', line)
        if m:
          if 'adapter_id' in bbu:
            ret.append(bbu)
            bbu = {}

          bbu['adapter_id'] = int(m.group(1))
          continue

        if 'adapter_id' in bbu:
          fields = line.split(':', 1)
          if len(fields) > 1:
            k, v = self.__to_property(*fields)

            if k == 'exit_code':
              continue

            bbu[k] = v

      if len(bbu):
        ret.append(bbu)

    return self.__array_to_dic(arr=ret,prefix='bbus')

  def adapters(self):
    """
    Get MegaRAID adapters
    :return: a list of all installed MegaRAID adapters
    :rtype: list
    """
    ret = []

    data = self.execute("-AdpAllInfo -aAll")
    if data:
      adapter_id = None
      adapter = {}

      for line in data:
        m = re.match('^adapter #(\d+)', line)
        if m:
          if 'id' in adapter:
            ret.append(adapter)
            adapter = {}

          adapter['id'] = int(m.group(1))
          continue

        if 'id' in adapter:
          fields = line.split(':', 1)
          if len(fields) > 1:
            k, v = self.__to_property(*fields)

            if k == 'exit_code':
              continue

            adapter[k] = v

      if len(adapter):
        ret.append(adapter)

    return self.__array_to_dic(arr=ret,prefix='adapters')

  

def main():
  from distutils.spawn import find_executable
  MegaCli = find_executable('MegaCli')

  if MegaCli :
    cli = MegaCLI(cli_path=MegaCli)

  elif os.path.exists('/opt/MegaRAID/MegaCli/MegaCli64'):
    cli = MegaCLI()
  else :
    return 

  try:
    # print result to sysout ,so golang could get the info 
    for k,v in cli.adapters().items():  
      print("%s:%s"%(k,v))
    for k,v in cli.bbu().items():  
      print("%s:%s"%(k,v))
    for k,v in cli.logicaldrives().items():  
      print("%s:%s"%(k,v)) 
    for k,v in cli.physicaldrives().items():  
      print("%s:%s"%(k,v))
  except MegaCLIError as e:
    print("error:{0}".format( e))

  

if __name__ == "__main__":
    # execute only if run as a script
    main()