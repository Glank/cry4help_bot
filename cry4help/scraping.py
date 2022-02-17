import re

class NumericPattern:
  def __init__(self, regex, type_):
    self.regex = regex 
    self.compiled = re.compile(regex)
    self.type = type_
  def value(self, match):
    raise NotImplementedError()
  def start(self, match):
    if len(match.groups()) != 1:
      raise NotImplementedError("start() needs custom implementation for regex patterns with zero or more than one groups.")
    return match.start(1)
  def end(self, match):
    if len(match.groups()) != 1:
      raise NotImplementedError("end() needs custom implementation for regex patterns with zero or more than one groups.")
    return match.end(1)

class FloatPattern(NumericPattern):
  def __init__(self, regex):
    NumericPattern.__init__(self, regex, 'number')
  def value(self, match):
    return float(match[1])

class UnitPattern(NumericPattern):
  def __init__(self, regex, unit):
    NumericPattern.__init__(self, regex, 'unit')
    self.unit = unit
  def value(self, match):
    return self.unit
    
_NUMBER_PATTERNS = [
  FloatPattern(r'(\d+\.?\d*)'),
  FloatPattern(r'(\.\d+)'),
]
_UNIT_PATTERNS = [
  UnitPattern(r'(?:[^a-z]|^)(lbs?|pounds?)(?:[^a-z]|$)', 'lbs'),
  UnitPattern(r'(?:[^a-z]|^)(kgs?|kilo|k)(?:[^a-z]|$)', 'kg'),
  UnitPattern(r'(?:[^a-z]|^)(st|stones?)(?:[^a-z]|$)', 'st'),
  UnitPattern(r'(?:[^a-z]|^)(bmi)(?:[^a-z]|$)', 'bmi'),
]
_PATTERNS = _NUMBER_PATTERNS+_UNIT_PATTERNS

def scrape_numeric(string):
  """
  Given an arbitrary string, extract all the numeric data with or without units.
  Returns a list of tokens, like this:
  return [
    {
      "type": "number", # or unit
      "value": 3.14,
      "start": 4,  # index in string of start of pattern match
      "end": 12, # index of last char of pattern matched
    },
    ...
  ]
  """
  global _PATTERNS
  string = string.lower()
  offset = 0
  tokens = []
  match_found = True
  while match_found and len(string) > 0:
    match_found = False
    matches = []
    for pattern in _PATTERNS:
      match = pattern.compiled.search(string)
      if match:
        matches.append((pattern, match))
    if not matches:
      break
    match_found = True
    matches.sort(key=lambda pm: pm[0].start(pm[1]))
    pattern, match = matches[0]
    end = pattern.end(match)
    tokens.append({
      'type': pattern.type,
      'value': pattern.value(match),
      'start': pattern.start(match)+offset,
      'end': end+offset,
    })
    string = string[end:]
    offset += end
  return tokens

