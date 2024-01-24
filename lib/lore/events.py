from .phrases import PhraseGraph

def _make_pg_found_hoard():
  pg = PhraseGraph()

  # Assume there is a collect_resources goal, and assume that goal requires
  # collecting crystals. This event will only be triggered if there are enough
  # crystals on the floor to complete the level.

  pg.start >> (
      'Wow! This ought to do it!',
      'Our intel was accurate. Look at all those Energy Crystals!',
  ) >> (
      pg(
          'Now, to get this back.',
          'Get this back to your base.',
      ) |
      pg(
          'With this, we have enough to complete our mission!',
          'Collect all the Energy Crystals you\'ve found and complete our '
          'mission!',
      ) & 'treasure_many' |
      pg(
          'I hope we can collect these without attracting too much attention.',
          'Be careful, Cadet! This is surely enough to attract those '
          '%(monster_type)s monsters.',
      ) & 'has_monsters'
  ) >> () >> (
      ~pg.states('treasure_one', 'treasure_many')
      >> ~pg.states('has_monsters')
  ) >> pg.end

  pg.compile()
  return pg

def _make_pg_found_hq():
  pg = PhraseGraph()

  find_lost_miners = (
      pg(
          'Now, find those lost Rock Raiders!',
      ) >> pg.states(
          'lost_miners_together', 'lost_miners_apart'
      ) |
      pg(
          'Now, find the lost Rock Raider!',
      ) & 'lost_miners_one'
  )

  pg.start >> pg(
      'There it is!',
      'Way to go, Cadet!',
  ) >> (
      find_lost_miners >> ~pg.states(
          'collect_resources'
      ) |
      pg(
          'Now, collect %(resources)s.'
      ) & 'collect_resources'
  ) >> pg.end

  pg.compile()
  return pg

FOUND_HOARD = _make_pg_found_hoard()
FOUND_HQ = _make_pg_found_hq()