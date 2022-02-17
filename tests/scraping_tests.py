import cry4help as c4h

class TestCase:
  def __init__(self, string, expected_tokens):
    self.string = string
    self.expected_tokens = expected_tokens
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

def main():
  TEST_CASES = [
    TestCase("5 lb", [
      {'type':'number', 'value':5, 'start':0, 'end':1},
      {'type':'unit', 'value':'lbs', 'start':2, 'end':4},
    ]),
    TestCase("I'm worried that I've only lost 56 lbs.", [
      {'type':'number', 'value':56},
      {'type':'unit', 'value':'lbs'},
    ]),
    TestCase("I'm worried that I've only lost 27.5 pound.", [
      {'type':'number', 'value':27.5},
      {'type':'unit', 'value':'lbs'},
    ]),
    TestCase("I'm worried that I've only lost .5 st.", [
      {'type':'number', 'value':0.5},
      {'type':'unit', 'value':'st'},
    ]),
    TestCase("I'm worried that I've only lost 10 kgs and my BMI is 50", [
      {'type':'number', 'value':10},
      {'type':'unit', 'value':'kg'},
      {'type':'number', 'value':50},
      {'type':'unit', 'value':'bmi'},
    ]),
  ]
  for test_case in TEST_CASES:
    test_case.test()
