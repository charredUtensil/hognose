from .phrases import PhraseGraph

def _make_pg_found_hoard():
  pg = PhraseGraph()

  pg.start >> pg(
      'Wow! This ought to do it!',
      'Our intel was accurate. Look at all those Energy Crystals!',
  ) >> (
      pg(
          'Now, to get this back.',
          'Get this back to your base.',
      ) |
      pg(
          'Collect all the Energy Crystals you\'ve found and complete our '
          'mission!',
      ) & 'treasure_many'
  ) >> pg.end

  pg.compile()
  return pg

def _make_pg_found_hq():
  pg = PhraseGraph()

  pg.start >> pg(
      'There it is!'
  ) >> (
      pg(
          'Now, find those lost Rock Raiders!'
      ) >> pg.states(
          'lost_miners_one', 'lost_miners_together', 'lost_miners_apart'
      ) |
      pg(
          'Now, collect %(resources)s.'
      ) & 'collect_resources'
  ) >> pg.end

  pg.compile()
  return pg

FOUND_HOARD = _make_pg_found_hoard()
FOUND_HQ = _make_pg_found_hq()