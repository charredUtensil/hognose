from .phrases import PhraseGraph

def _objectives(pg):
  find_lost_miners = pg() >> (
      pg('find the lost Rock Raider') & 'lost_miners_one' |
      pg('find the lost Rock Raiders') & 'lost_miners_together' |
      pg('find the lost Rock Raiders') & 'lost_miners_apart'
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
      pg(*_COMMENDATIONS) & 'commend' |
      pg(
          'Those %(monster_type)s monsters were no match for you!'
          ) & 'has_monsters'
      ) >> ()

  commend = (
      pg(*_COMMENDATIONS) |
      pg(
          'Keep up the good work, Cadet!'  
          )) & 'commend'

  able_to = pg(
      'You managed to',
      'You were able to')

  mission_complete = pg(
      '\nMission Complete!'
  )

  objectives = _objectives(pg)

  pg.start >> opening
  (pg.start | opening) >> able_to

  able_to >> objectives >> (commend | mission_complete)

  commend >> mission_complete
  mission_complete >> pg.end
  (mission_complete & 'has_monsters') >> pg.end

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