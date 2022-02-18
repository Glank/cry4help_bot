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
  def _get_regex(unit_regex):
    return r'(?:[^a-z]|^)'+unit_regex+r'(?:[^a-z]|$)'
  def __init__(self, unit_regex, unit):
    NumericPattern.__init__(self, UnitPattern._get_regex(unit_regex), 'unit')
    self.unit = unit
  def value(self, match):
    return self.unit

class KeywordPattern(NumericPattern):
  def _get_regex(keyword_regex):
    return r'(?:[^a-z]|^)'+keyword_regex+r'(?:[^a-z]|$)'
  def __init__(self, keyword_regex, group):
    NumericPattern.__init__(self, KeywordPattern._get_regex(keyword_regex), 'keyword')
    self.group = group 
  def value(self, match):
    return self.group
    
_NUMBER_PATTERNS = [
  FloatPattern(r'(\d+\.?\d*)'),
  FloatPattern(r'(\.\d+)'),
]
_UNIT_PATTERNS = [
  UnitPattern(r'(lbs?|pounds?)', 'lbs'),
  UnitPattern(r'(kgs?|kilo|k)', 'kg'),
  UnitPattern(r'(st|stones?)', 'st'),
  UnitPattern(r'(bmi)', 'bmi'),
  UnitPattern(r'(inches|"|in)', 'in'),
  UnitPattern(r"(feet|'|ft)", 'ft'),
  UnitPattern(r'(cm)', 'cm'),
  UnitPattern(r'(m)', 'm'),
]
_KEYWORD_PATTERNS = [
  KeywordPattern(r'(down|lost|so far|total)', 'delta'),
  KeywordPattern(r'(gw|goal)', 'goal'),
  KeywordPattern(r'(cw|current|currently|stuck at)', 'current'),
  KeywordPattern(r'(weigh)', 'weight'),
  KeywordPattern(r'(tall)', 'height'),
]
_PATTERNS = _NUMBER_PATTERNS+_UNIT_PATTERNS+_KEYWORD_PATTERNS

def scrape_numeric(string):
  """
  Given an arbitrary string, extract all the numeric data with or without units.
  Returns a list of tokens, like this:
  return [
    {
      "type": "number", # or "unit" or "keyword"
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

def _token_dist(t1, t2):
  return min(t1['end'], t2['end']) - min(t1['start'], t2['start'])

class StickyRule:
  def __init__(self, name):
    self.name = name
  def sticks(self, cluster):
    raise NotImplementedError()

class BasicStickyRule(StickyRule):
  def __init__(self, name, units, keyword_groups, max_dist=250):
    StickyRule.__init__(self, name)
    self.units = units
    self.keyword_groups = keyword_groups
    self.max_dist = max_dist
  def sticks(self, cluster):
    cluster.sort(key=lambda t:t['start'])
    last_token = None
    for token in cluster:
      if last_token is not None:
        dist = _token_dist(last_token, token)
        if self.max_dist and dist>self.max_dist:
          return False
      if token['type'] == 'numeric':
        continue
      elif token['type'] == 'unit':
        if token['value'] not in self.units:
          return False
      elif token['type'] == 'keyword':
        if token['value'] not in self.keyword_groups:
          return False
    return True

_STICKY_RULES = [
  BasicStickyRule('height_imperial', ['ft', 'in'], ['height']),
  BasicStickyRule('height_metric', ['m', 'cm'], ['height']),
  BasicStickyRule('weight_imperial', ['st', 'lbs'], ['weight', 'current', 'goal']),
  BasicStickyRule('weight_metric', ['kg'], ['weight', 'current', 'goal']),
  BasicStickyRule('delta_imperial', ['st', 'lbs'], ['delta']),
  BasicStickyRule('delta_metric', ['kg'], ['delta']),
  BasicStickyRule('bmi', ['bmi'], []),
]
_STICKY_RULES = dict((r.name, r) for r in _STICKY_RULES)

def group_tokens(tokens):
  """
  Given a list of tokens generated from scrape_numeric, returns a clustering of those tokens
  by distance, type, and 'stickiness' rules (see above), like this:
  return [
    {
      "rule": "_rule_name_",
      "tokens": [...],
    }
    ...
  ]
  """
  global _STICKY_RULES
  tokens.sort(key=lambda t:t['start'])
  clusters = [{'rules':set(_STICKY_RULES.keys()), 'tokens':[t]} for t in tokens]
  found_merge = True
  while found_merge:
    # sort cluster pairs by distance
    cluster_pairs = []
    for i in range(len(clusters)-1):
      c1 = clusters[i]
      c2 = clusters[i+1]
      dist = _token_dist(c1['tokens'][-1], c2['tokens'][0])
      cluster_pairs.append((i, dist))
    cluster_pairs.sort(key=lambda p:-p[1])
    # go through the cluster pairs, looking for the clost mergable pair
    found_merge = False
    while cluster_pairs:
      i, dist = cluster_pairs.pop()
      c1 = clusters[i]
      c2 = clusters[i+1]
      rule_intersection = c1['rules'] & c2['rules']
      if rule_intersection:
        merged_tokens = c1['tokens']+c2['tokens']
        merged_rules = set()
        for rule_name in rule_intersection:
          rule = _STICKY_RULES[rule_name]
          if rule.sticks(merged_tokens):
            found_merge = True
            merged_rules.add(rule_name)
        if found_merge:
          clusters.pop(i+1)
          clusters[i] = {
            'rules': merged_rules,
            'tokens': merged_tokens,
          }
          break
  # select final rules
  for c in clusters:
    if len(c['tokens']) == 1:
      c['rules'] = []
      c['rule'] = None
    else:
      c['rules'] = list(c['rules'])
      c['rule'] = c['rules'][0]
  return clusters
