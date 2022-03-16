from nltk.tokenize import TreebankWordTokenizer

class Tokenizer:
  def __init__(self, token_dict_filename = None):
    """
      token_dict_filename:
        name of file containing an existing token dictionary
        if None or unset then no token dictionary is used
    """
    self.token_dict_filename = token_dict_filename 
    self.base_tokenizer = TreebankWordTokenizer()
  def add_tokens_to_dict(self, string):
    pass #TODO
