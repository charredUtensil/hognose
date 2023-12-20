def premise():
  ph = phrasegen()

  ths = ph.start.then('The Hognose scanner')
  alm = ths.then('aboard the L.M.S. Explorer')
  ipu = ph.start.any(ths, alm).then(
      'is picking up', 'has discovered', 'indicates', 'is showing')

  ts  = ph.start.then('The scanners')
  alm = tsz.then('aboard the L.M.S. Explorer')
  we  = ph.start.then('We')
  hf  = ph.any(ts, alm, we).then(
      'have found', 'have located', 'have discovered')

  itr = ph.any(ipu, hf)
  del ths, alm, ipu, ts, we, hf

  otc = itr.on(treasure_caves == 1).then(
      'a large Energy Crystal signature near here',
      'a nearby cave with an abundance of Energy Crystals')

  mtc = itr.on(treasure_caves > 1).then(
      'large deposits of Energy Crystals in this cavern',
      'a cave system with an abundance of Energy Crystals')

  gcr = itr.then(
      'another cavern to continue our mining operations')

  fcs = ph.any(otc, mtc, gcr).then('.')
  del otc, mtc, gcr
  fcs.end()

  pnb = fcs.then(
      'However,',
      'Unfortunately,',
      'The bad news?')

  olm = ph.any(ph.start, pnb).on(lost_miners == 1).then(
      'one of our Rock Raiders has gone missing',
      'a recent cave-in has trapped one of our Rock Radiers',
      'a teleporter malfunction sent one of our Rock Raiders to the wrong cave')

  lmt = ph.any(ph.start, pnb).on(lost_miners > 1 and lost_miner_caves == 1).then(
      'some of our Rock Radiers have gone missing',
      'a recent cave-in has trapped some of our Rock Raiders',
      'our Rock Raider surveying group has not checked in for some time')

  lma = ph.any(ph.start, pnb).on(lost_miner_caves > 1).then(
      'some of the Rock Radiers that were exploring this cavern have gone '
      'missing',
      'a teleporter malfunction has scattered some of our miners throughout '
      'the cavern')

  lm  = ph.any(olm, lmt, lma)
  del olm, lmt, lma
  lm.then('.').end()
  nxp = ph.any(pnb, lm.then('.', 'and', '. If that wasn\'t hard enough,'))

  sha = nxp.then(
      'a nearby lava flow is threatening our Rock Raider HQ',
      'we are dangerously close to a cavern full of lava',
      'we are worried about nearby lava flows')
  sha.then('.').end()

  mp  = ph.any(nxp, sha.then('.')).then(
      'we are picking up signs of %s in the area' % monster_type,
      'this cavern is inhabited by nests of %s' % monster_type)
  mp.then('.').end()

  ph.start.then(
      'our mining operations have been going smoothly, and we are ready to '
      'move on to the next cavern',
      'there is nothing out of the ordinary to report today',
      'things have been quiet and I hope they should remain that way, Cadet',
      ).then('.').end()
  
  return ph.generate()


class Phrase(object):

  def __init__(self, pg: 'PhraseGenerator', id: int, texts: Iterable[str], condition):
    self._pg = pg
    self._id = id
    self._texts = tuple(texts)
    self._after = []
    self._before = []

  def _then(self, other):
    self._after.append(other)
    other._before.append(self)

  def then(self, *texts) -> 'Phrase':
    r = self._pg._phrase(*texts)
    self._then(r)
    return r

  def end(self):
    self._then(self._pg._end)


class PhraseGenerator(object):

  def __init__(self):
    self._phrases = []
    self.start = self._phrase()
    self._end = self._phrase()

  def _phrase(self, *texts) -> Phrase:
    r = Phrase(self, len(), texts)
    self._phrases.append(r)
    return r

  def any(self, *phrases):
    r = self._phrase()
    for ph in phrases:
      ph._then(r)
    return r
