from typing import Iterable

from .phrases import PhraseGraph

def _make_pg():
  pg = PhraseGraph()

  build_hq = pg.then(
      'build the Rock Raider HQ',
      'build up your base')

  and_defend_it = pg.on('has_monsters').then(
      'and keep it safe',
      'and make sure it is heavily defended')

  explore = pg.then(
      'explore the cavern')

  get_to_safety = pg.on('spawn_has_erosion').then(
      'move to a safer cavern',
      'get your Rock Raiders to safety')

  find_lost_miners = (
      pg.on('lost_miners_one').then(
          'find the lost Rock Raider',
          'locate the missing Rock Raider') |
      pg.on('lost_miners_many').then(
          'find the lost Rock Raiders',
          'locate the missing Rock Raiders')).then()

  defend_hq = pg.on('has_monsters').then(
      'defend the Rock Radier HQ',
      'build up your defenses',
      'arm your Rock Raiders')

  repair_hq = pg.on('spawn_is_ruins').then(
      'clean up this mess',
      'get the Rock Raider HQ back in operation')

  collect_resources = pg.on('collect_resources').then(
      'continue our mining operation by collecting %(resources)s',
      'collect %(resources)s')

  sendoff = pg.then(
      'We\'re counting on you, Cadet!',
      'Good luck out there, Cadet!'
  )

  first_task = pg.start.then(
      explore | build_hq | repair_hq | defend_hq | get_to_safety).then()

  defend_hq.then(', ').then(explore)
  get_to_safety.then(',').then(build_hq)
  first_task.then('and').then(collect_resources)
  first_task.then(
      ', then',
      'and',
      ).then(find_lost_miners)
  (build_hq | repair_hq).then(and_defend_it)
  and_defend_it.then(
      '. Then',
      '. Once you have done that,'
      ).then(collect_resources)
  pg.start.then().then(find_lost_miners)
  find_lost_miners.then(
      '. Once you have done that,',
      '. With them secure,',
      '. Along the way,'
      ).then(collect_resources)
  last_task = (and_defend_it | find_lost_miners | collect_resources).then('.')
  last_task.end()
  last_task.then(sendoff).end()
  return pg

ORDERS = _make_pg()