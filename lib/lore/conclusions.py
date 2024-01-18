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
  return objs >> '.'

_COMMENDATIONS = (
    'Well done!',
    'Good work!',
    'Outstanding!',
    'I knew you could do it, Cadet!',
    'We were right to count on you, Cadet!',)

def _make_pg_success():
  pg = PhraseGraph()

  opening = (
      pg(
          'Wow!',
          *_COMMENDATIONS
      ) & 'commend' |
      pg(
          'Those %(monster_type)s monsters were no match for you!'
      ) & 'has_monsters'
  )
  opening = (pg.start >> opening | pg.start) >> ()

  commend = pg(
      'Keep up the good work, Cadet!',
      *_COMMENDATIONS
  ) & 'commend'

  able_to = pg(
      'You managed to',
      'You were able to')

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

  you = pg('you')

  tail = pg('\n') >> (
      commend >> mission_complete |
      mission_complete
  ) >> pg.states(None, 'has_monsters') >> pg.end

  objectives = _objectives(pg)
  opening >> able_to >> objectives >> tail
  opening >> you >> (
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
      'Oh, dear.')

  console = pg(
      'You\'ll do better next time.'
      ) & 'console'

  unable_to = pg(
      'You didn\'t',
      'You couldn\'t',
      'We were counting on you to',
      )

  mission_failed = pg(
      '\nMission Failed')

  pg.start >> opening
  (pg.start | opening) >> unable_to
  
  unable_to >> _objectives(pg) >> (console | mission_failed)
  
  console >> mission_failed >> pg.end

  pg.compile()
  return pg

SUCCESS = _make_pg_success()
FAILURE = _make_pg_failure()