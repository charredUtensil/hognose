from .phrases import PhraseGraph


def _objectives(pg):
  find_lost_miners = pg() >> (
      pg(
          'find the lost Rock Raider'
      ) & 'lost_miners_one' |
      pg(
          'find the lost Rock Raiders'
      ) >> pg.states('lost_miners_together', 'lost_miners_apart')
  ) >> ()

  get_resources = pg(
      'collect all %(resources)s',
      'get the %(resources)s we needed'
  ) & 'collect_resources'

  objs = (find_lost_miners | get_resources)
  find_lost_miners >> 'and' >> get_resources
  return objs


_COMMENDATIONS = (
    'Well done!',
    'Good work!',
    'Outstanding!',
    'I knew you could do it, Cadet!',
    'You\'re very good at this, Cadet!',
    'Your efforts have been outstanding!',
    'We were right to count on you, Cadet!',)


def _make_pg_success():
  pg = PhraseGraph()

  opening_commendation = pg(
      'Wow!',
      *_COMMENDATIONS
  ) & 'commend'

  opening_monsters = pg(
      'Those %(monster_type)s monsters were no match for you!',
      'You had nothing to fear from those %(monster_type)s monsters!'
  ) & 'has_monsters'

  commend = pg(
      'Keep up the good work, Cadet!',
      'You make this look rather easy, Cadet!',
      *_COMMENDATIONS
  ) & 'commend'

  despite_the_odds = pg(
      'Despite the odds,',
      'In the face of danger,',
      'Even with the odds against you,',
  )

  you = pg('you')

  able_to = pg(
      'managed to',
      'were able to')

  mission_complete = pg(
      'Mission Complete!'
  )

  repaired_hq = pg(
      'repaired the Rock Raider HQ',
      'restored our mining operations',
  ) & 'spawn_is_ruin'

  found_hq = pg(
      'found the base',
  ) & 'find_hq'

  found_lost_miners_no_resources = pg() >> (
      pg(
          'found the lost Rock Raider',
          'located the lost Rock Raider',
      ) & 'lost_miners_one' |
      pg(
          'found the lost Rock Raiders',
          'located the lost Rock Raiders',
      ) >> pg.states('lost_miners_together', 'lost_miners_apart')
  ) >> (
      ', safe and sound',
      'before anything could happen to them',
  )

  found_lost_miners = pg() >> (
      pg(
          'found the lost Rock Raider',
          'located the lost Rock Raider',
      ) & 'lost_miners_one' |
      pg(
          'found the lost Rock Raiders',
          'located the lost Rock Raiders',
      ) >> pg.states('lost_miners_together', 'lost_miners_apart')
  ) >> ()

  got_resources = pg(
      'collected %(resources)s',
      'collected all %(resources)s',
      'got all %(resources)s'
  ) & 'collect_resources'

  while_facing_danger = (
      pg(
          'despite that horde of %(monster_type)s monsters!',
      ) & 'has_monsters'
  )

  tail = pg('\n\n') >> (
      commend >> mission_complete |
      mission_complete
  ) >> ~pg.states(
      'has_monsters'
  ) >> ~pg.states(
      'spawn_has_erosion'
  ) >> pg.end

  objectives = _objectives(pg)

  pg.start >> (opening_commendation | opening_monsters)
  opening_monsters >> (despite_the_odds | you)
  (
      pg.start |
      opening_commendation
  ) >> () >> ~(
    pg.states('has_monsters', 'spawn_has_erosion') >> despite_the_odds
  ) >> you

  you >> able_to >> objectives >> () >> (while_facing_danger | pg('.')) >> tail
  you >> (
      repaired_hq | found_hq
  ) >> (
      pg() | pg(',') >> found_lost_miners
  ) >> 'and' >> (
      got_resources | found_lost_miners_no_resources
  ) >> '.' >> tail
  you >> found_lost_miners_no_resources

  pg.compile()
  return pg


def _make_pg_failure():
  pg = PhraseGraph()

  opening = pg(
      'Oh, dear.',
  )

  console = pg(
      'Chin up, Cadet!',
      'You must succeed, Cadet!',
      'You\'ll do better next time.',
  ) & 'console'

  unable_to = pg(
      'You didn\'t',
      'You couldn\'t',
      'You were unable to',
      'We were counting on you to',
  )

  mission_failed = pg(
      '\n\nMission Failed')

  pg.start >> opening
  (pg.start | opening) >> unable_to

  (
      unable_to >>
      _objectives(pg) >>
      '.' >>
      ~console >>
      mission_failed >>
      pg.end
  )

  pg.compile()
  return pg


SUCCESS = _make_pg_success()
FAILURE = _make_pg_failure()
