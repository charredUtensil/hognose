class Conditional(object):

  def __init__(self, condition, if_true, if_false=None):
    self.condition = condition
    self.if_true = if_true
    self.if_false = if_false

  def serialize(self, offset: Tuple[int, int]):
    return (
        f'(({condition.serialize(offset)}))'
        f'[{self.if_true.serialize(offset)}]'
        f'{f"[{self.if_false.serialize(offset)}]" if if_false else ""}')