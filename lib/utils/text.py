def word_wrap(text: str, chars: int):
  def h():
    for line in text.splitlines():
      while line:
        if len(line) <= chars:
          yield line
          break
        ptr = chars
        while ptr > 0:
          if line[ptr].isspace():
            yield line[:ptr]
            line = line[ptr + 1:]
            break
          ptr -= 1
        else:
          yield line[:chars]
          line = line[chars:]
  return '\n'.join(h())