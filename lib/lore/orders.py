from typing import Iterable

from .phrases import PhraseGraph

def _make_pg():
  pg = PhraseGraph()

  build_hq = pg(
      'build the Rock Raider HQ',
      'build up your base')

  and_defend_it = pg(
      'and keep it safe',
      'and make sure it is heavily defended'
      ) & 'has_monsters'

  explore = pg(
      'explore the cavern')

  get_to_safety = pg(
      'move to a safer cavern',
      'get your Rock Raiders to safety'
      ) & 'spawn_has_erosion'

  find_lost_miners = pg() >> (
      pg(
          'find the lost Rock Raider',
          'locate the missing Rock Raider'
          ) & 'lost_miners_one' |
      pg(
          'find the lost Rock Raiders',
          'locate the missing Rock Raiders'
          ) & 'lost_miners_many'
      ) >> ()

  defend_hq = pg(
      'defend the Rock Radier HQ',
      'build up your defenses',
      'arm your Rock Raiders'
      ) & 'has_monsters'

  repair_hq = pg(
      'clean up this mess',
      'get the Rock Raider HQ back in operation'
      ) & 'spawn_is_ruins'

  find_hq = pg(
      'reach the Rock Raider HQ',
      'locate the base'
      ) & 'find_hq'

  and_use_it_to = pg(
      'and use it to',
      ', and from there you can')

  collect_resources = pg(
      'continue our mining operation by collecting %(resources)s',
      'collect %(resources)s'
      ) & 'collect_resources'

  sendoff = pg(
      'We\'re counting on you, Cadet!',
      'Good luck out there, Cadet!')

  first_task = pg.start >> (
      explore | build_hq | repair_hq | defend_hq |
      get_to_safety) >> ()

  pg.start >> find_hq
  get_to_safety >> ',' >> (build_hq | find_hq)

  pg.start >> find_lost_miners
  first_task >> (
      ', then',
      'and',
      ) >> find_lost_miners

  (build_hq | repair_hq | find_hq) >> and_defend_it
  find_hq >> and_use_it_to >> (find_lost_miners | collect_resources)
  defend_hq >> ',' >> explore

  (first_task | find_hq) >> 'and' >> collect_resources
  and_defend_it >> (
      '. Then',
      '. Once you have done that,'
      ) >> collect_resources
  find_lost_miners >> (
      '. Once you have done that,',
      '. With them secure,',
      '. Along the way,'
      ) >> collect_resources

  last_task = (and_defend_it | find_lost_miners | collect_resources) >> '.'
  last_task >> pg.end
  last_task >> sendoff >> pg.end

  return pg

ORDERS = _make_pg()