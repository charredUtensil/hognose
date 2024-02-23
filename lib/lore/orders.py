from lib.lore.phrases import PhraseGraph
# Pylint doesn't like the PhraseGraph api's use of >>
# pylint: disable=expression-not-assigned,pointless-statement,too-many-locals


def _make_pg():
  pg = PhraseGraph()

  build_hq = pg(
      'build the Rock Raider HQ',
      'build up your base')

  and_defend_it = pg(
      'and keep it safe',
      'and make sure it is heavily defended',
  ) & 'has_monsters'

  get_to_safety = pg(
      'get your Rock Raiders to safety',
      'make sure your Rock Raiders are safe',
  ) & 'spawn_has_erosion'

  move_hq = pg(
      'move to a safer cavern',
      'find a more suitable location',
  ) >> pg.states('spawn_has_erosion') >> pg.states('spawn_is_ruin')

  find_lost_miners = pg(
      'find',
      'locate',
      'search the cavern for'
  ) >> (
      pg('the', 'that') >> pg(
          'lost Rock Raider',
          'missing Rock Raider'
      ) & 'lost_miners_one' |
      pg('the', 'that') >> pg(
          'cavern with the lost Rock Raiders',
          'missing group of Rock Raiders',
      ) & 'lost_miners_together' |
      pg('the', 'those') >> pg(
          'lost Rock Raiders',
          'missing Rock Raiders',
      ) & 'lost_miners_apart'
  ) >> ()

  before_monsters_do = pg(
      'before the %(monster_type)s monsters do!',
  ) & 'has_monsters'

  defend = (
      pg.start >> 'defend the Rock Radier HQ' |
      (
          'build up your defenses',
          'arm your Rock Raiders',
      )
  ) & 'has_monsters'

  repair_hq = pg(
      'clean up this mess',
      'get the Rock Raider HQ back in operation',
  ) & 'spawn_is_ruin'

  find_hq = pg(
      'reach the Rock Raider HQ',
      'locate the base',
  ) & 'find_hq'

  and_use_it_to = pg('and use it to')

  asap = pg(
      'as soon as possible',
      'as soon as you can',
  )

  collect_resources = pg(
      'collect %(resources)s',
      'continue our mining operation by collecting %(resources)s',
  )

  continue_mining = pg(
      'continue mining operations',
      'explore the cavern',
      'resume our mining operation',
      'search the cavern',
  )

  we_need_resources = pg(
      'we need %(resources)s',
      'you need to collect %(resources)s'
  )

  sendoff = pg(
      'Best of luck!',
      'Good luck out there!',
      'We\'re counting on you!',
  )

  tail = () >> ~sendoff >> pg.end

  and_endgame = pg()
  endgame = pg()

  pg.start >> (
      build_hq | get_to_safety | move_hq | find_lost_miners | repair_hq |
      find_hq | defend)

  (build_hq | defend) >> and_endgame
  asap_and_endgame = () >> ~asap >> and_endgame
  (repair_hq | find_hq) >> asap_and_endgame
  (get_to_safety | move_hq) >> () >> (
      ',' >> defend | asap_and_endgame
  )
  get_to_safety >> ',' >> (build_hq | find_hq)

  (build_hq | repair_hq | find_hq) >> and_defend_it
  find_hq >> and_use_it_to >> endgame

  (
      and_defend_it |
      endgame >> continue_mining
  ) >> '.' >> we_need_resources
  and_endgame >> 'and' >> endgame
  endgame >> (find_lost_miners | collect_resources)
  find_lost_miners >> (before_monsters_do | '.') >> () >> (
      tail |
      (
          'Once you\'ve found them,',
          'With them safe,',
          'When they are safe,',
      ) >> (collect_resources | we_need_resources)
  )
  (
      collect_resources | we_need_resources
  ) >> pg.states('collect_resources') >> '.' >> tail

  pg.compile()
  return pg


ORDERS = _make_pg()
