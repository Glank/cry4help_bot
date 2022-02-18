import cry4help as c4h

class TokenizerTest:
  def __init__(self, string, expected_tokens, unexpected_tokens=None):
    self.string = string
    self.expected_tokens = expected_tokens
    self.unexpected_tokens = unexpected_tokens if unexpected_tokens else []
  def test(self):
    tokens = c4h.scraping.scrape_numeric(self.string)
    for expected_token in self.expected_tokens:
      found_match = False
      for token in tokens:
        is_match = True
        for key in expected_token:
          if token[key] != expected_token[key]:
            is_match = False
            break
        if is_match:
          found_match = True
          break
      if not found_match:
        raise RuntimeError("Expected to see token like {} but only got:\n{}".format(expected_token, tokens))
    for unexpected_token in self.unexpected_tokens:
      found_match = False
      for token in tokens:
        is_match = True
        for key in expected_token:
          if token[key] != expected_token[key]:
            is_match = False
            break
        if is_match:
          found_match = True
          break
      if found_match:
        raise RuntimeError("Expected to not see token like {} but got:\n{}".format(expected_token, tokens))

def clustering_test():
  tokens = c4h.scraping.scrape_numeric("I've lost 50 lbs and I'm 5' tall")
  clusters = c4h.scraping.group_tokens(tokens)
  expected_clusters = [
    "delta_imperial: ['keyword', 'number', 'unit']",
    "height_imperial: ['number', 'unit', 'keyword']",
  ]
  actual_clusters = []
  for c in clusters:
    if c['rule'] is None:
      continue
    cluster = "{}: {}".format((c['rule']), [t['type'] for t in c['tokens']])
    actual_clusters.append(cluster)
  if "|".join(actual_clusters) != "|".join(expected_clusters):
    raise RuntimeError("Expected {} but got {}".format(expected_clusters, actual_clusters))

def main():
  TEST_CASES = [
    TokenizerTest("5 lb", [
      {'type':'number', 'value':5, 'start':0, 'end':1},
      {'type':'unit', 'value':'lbs', 'start':2, 'end':4},
    ]),
    TokenizerTest("I'm worried that I've only lost 56 lbs.", [
      {'type':'number', 'value':56},
      {'type':'unit', 'value':'lbs'},
    ]),
    TokenizerTest("I'm worried that I've only lost 27.5 pound.", [
      {'type':'number', 'value':27.5},
      {'type':'unit', 'value':'lbs'},
    ]),
    TokenizerTest("I'm worried that I've only lost .5 st.", [
      {'type':'number', 'value':0.5},
      {'type':'unit', 'value':'st'},
    ]),
    TokenizerTest("I'm worried that I've only lost 10 kgs and my BMI is 50", [
      {'type':'number', 'value':10},
      {'type':'unit', 'value':'kg'},
      {'type':'number', 'value':50},
      {'type':'unit', 'value':'bmi'},
    ]),
    # TODO: improve recognition of feet, meter, and inch units
    #TokenizerTest("I'm 3m tall.", [
    #  {'type':'number', 'value':3},
    #  {'type':'unit', 'value':'m', 'start':5},
    #], [
    #  {'type':'unit', 'value':'ft', 'start':1},
    #  {'type':'unit', 'value':'m', 'start':2},
    #]),
  ]
  for test_case in TEST_CASES:
    test_case.test()
  clustering_test()

