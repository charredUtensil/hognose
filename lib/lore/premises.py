from typing import Iterable

from .phrases import PhraseGraph

def _make_pg():
  pg = PhraseGraph()

  greeting = pg.start >> (
      pg(
          'Are you ready for the next mission?',
          'Welcome back, Cadet.',
          'I hope you\'re prepared for this one, Cadet.',
          'Up and at \'em, Cadet!',
          'Cadet, are you up for some more action?') |
      pg(
          'Are you ready to set sail?',
          'I hope you packed your lifejacket, Cadet.'
          ) & 'flooded_water' |
      pg(
          'I hope you\'re not afraid of a little heat!',
          'You\'d better keep your cool with this one!'
          ) & 'flooded_lava'
  ) >> '\n'
  greeting = (greeting | pg.start) >> ()

  negative_greeting = pg.start >> pg(
      'Things have been going smoothly... until now!',
      'Bad news, Cadet!',
      'We need your help, Cadet.',
  ) >> '\n'

  we_found_a_cave = pg() >> (
      pg(
          'A recent scan',
          'The Hognose scanner',
          'The Hognose scanner aboard the L.M.S. Explorer'
      ) >> ('found', 'has discovered', 'has indicated') |
      pg(
          'We',
          'The scanners',
          'The scanners aboard the L.M.S. Explorer'
      ) >> ('have found', 'have located', 'have discovered')
  ) >> (
      pg(
          'a large Energy Crystal signature near here',
          'a nearby cave with an abundance of Energy Crystals'
      ) & 'treasure_one' |
      pg(
          'large deposits of Energy Crystals in this cavern',
          'a cave system with an abundance of Energy Crystals'
      ) & 'treasure_many' |
      pg('another cavern where we can continue our mining operations')
  ) >> ()
  
  forced_to_evac = pg(
      ', when an increase in seismic activity forced us to evacuate.',
      ', but we were forced to evacuate when the cavern started to collapse.',
  )

  cavern_collapsed = pg(
      ', when the cavern collapsed.',
      'before a massive cave-in occurred.',
  )

  no_one_hurt_but_base_destroyed = (
    forced_to_evac | cavern_collapsed
  ) >> (
      'No one was hurt, but',
      'Everyone made it out, but'
  ) >> (
      pg(
          'our base is in ruins',
          'our Rock Raider HQ has taken heavy damage',
      ) & 'spawn_is_ruin' |
      pg(
          'we presume our Rock Radier HQ has been destroyed'
      ) & 'find_hq'
  )

  they_are_trapped_and = (
      pg(
          'Now they are trapped, and'
      ) >> pg.states('lost_miners_together', 'lost_miners_apart') |
      pg(
          'One Rock Raider is missing, and'
      ) & 'lost_miners_one'
  ) >> ()

  miners_were_exploring_then_lost = pg(
      'Some of our Rock Raiders were'
  ) >> (
      pg(
          'searching for a nearby cavern with an abundance of Energy '
          'Crystals'
      ) & 'treasure_one' |
      pg(
          'exploring this cavern',
          'conducting mining operations here',
      ) >> pg.states('treasure_many', None)
  ) >> (
      forced_to_evac >> '\nUnfortunately,' >> (
          pg(
              'some of them are still trapped within the cavern',
              'the teleporters have been acting up again and some of them '
              'have been left behind',
          ) >> pg.states('lost_miners_apart', 'lost_miners_together') |
          pg(
              'one of them is still trapped within the cavern',
              'one is still unaccounted for',
          ) & 'lost_miners_one'
      ) & 'spawn_is_ruin' |
      cavern_collapsed >> they_are_trapped_and >> pg(
          'we presume our Rock Radier HQ has been destroyed'
      ) & 'find_hq' |
      pg(
          ', but we have not been able to contact them for some time now',
          'and were buried by a recent cave-in',
      ) >> pg.states('lost_miners_together', 'lost_miners_apart') >> ()
  ) >> ()

  teleporter_malfunction = pg() >> (
      pg(
          'A teleporter malfunction sent one of our Rock Raiders to a cavern '
          'near here',
          'The teleporter on the L.M.S. Explorer has been acting up again and '
          'one of our Rock Raiders is trapped in an uncharted cavern',
          'One of our Rock Raiders was accidentally sent to the wrong cavern',
      ) & 'lost_miners_one' |
      pg(
          'A teleporter malfunction sent a group of our Rock Raiders to a '
          'cavern near here',
          'The teleporter on the L.M.S. Explorer has been acting up again and '
          'a group of our Rock Raiders ended up in an uncharted cavern',
      ) & 'lost_miners_together'
  ) >> ()

  however = pg(
      '. \nHowever,',
      '. \nUnfortunately,',
      '. \nUnfortunately for us,',
      '. \nThe bad news?',
      '. Use caution!',
      ', but proceed with caution!\n',
      ', but this is no walk in the park.')

  find_them = pg() >> (
      pg(
          'we need to find them before the %(monster_type)s '
          'monsters do.',
          'I hope they don\'t meet any of the %(monster_type)s '
          'monsters roaming this cavern.'
          ) & 'has_monsters' |
      pg(
          'we\'re counting on you to find them!',
          'we don\'t know how long they\'ll last out there.',
          )
  ) >> pg.states(None, 'spawn_has_erosion')

  hq_destroyed = pg(
      'Recent seismic activity has damaged our Rock Raider HQ',
      'An earthquake in this area has caused several cave-ins and destroyed '
      'part of our Rock Raider HQ',
  )

  hq_destroyed_but_evacuated = hq_destroyed >> (
      '. We were able to evacuate in time',
      '. All of our Rock Raiders made it out',
      '. We evacuated the cavern',
      '. Everyone evacuated safely'
  ) >> (
      pg(
          ', but this is as close as we can get for now',
          ', but the teleporter seems to have been destroyed',
      ) & 'find_hq' |
      pg(
          ', but this is all that\'s left',
          'and the geology seems to be stable again',
      ) & 'spawn_is_ruin'
  )

  hq_destroyed_and_miners_lost = hq_destroyed >> ', and' >> (
      pg('one of our Rock Raiders is missing') & 'lost_miners_one' |
      pg(
          'a group of Rock Raidiers are missing',
          'a group of Rock Raidiers are trapped somewhere in the cavern'
          ) & 'lost_miners_together' |
      pg(
          'some of our Rock Raidiers are missing',
          'our Rock Raiders are trapped throughout the cavern'
          ) & 'lost_miners_apart'
    ) >> pg.states('spawn_is_ruin', 'find_hq') >> ()

  reassurance = pg(
      'Don\'t get discouraged.',
      'Don\'t worry!',
  ) >> (
      'I\'m sure you will be able to meet this challenge head-on!',
      'This is well within the capabilities of someone with your skillset.',
      'You\'ve triumphed over tough challenges before!',
      'You\'ve beaten worse odds before!',
  )

  spawn_has_erosion = pg(
      'we are dangerously close to a cavern full of lava',
      'we are concerned about nearby lava flows that could engulf this cavern',
      'you will need to keep an eye on the volcanic activity in this cavern',
  ) & 'spawn_has_erosion'

  has_monsters_texts = (
      'the tunnels here are full of large creatures that threaten our operations',
      'we are picking up signs of large creatures in the area',
      'this cavern is inhabited by nests of %(monster_type)s monsters',
      'we have reason to believe there are dozens of %(monster_type)s '
      'monsters just out of sight',
  )

  has_monsters = pg(*has_monsters_texts) & 'has_monsters'
  and_has_monsters = pg(', and') >> pg(*has_monsters_texts) & 'has_monsters'

  pg.start >> (
      'Our mining operations have been going smoothly, and we are ready to '
      'move on to the next cavern.',
      'There is nothing out of the ordinary to report today.',
      'Things have been quiet and I hope they should remain that way, Cadet!',
  ) >> pg.end

  greeting >> we_found_a_cave >> (pg('.') >> pg.end | however)
  however >> (spawn_has_erosion | has_monsters)

  (greeting | negative_greeting) >> pg() >> (
      miners_were_exploring_then_lost |
      teleporter_malfunction |
      hq_destroyed
  )

  (
      (miners_were_exploring_then_lost | teleporter_malfunction)
      >> '.'
      >> find_them
  )

  they_are_trapped_and >> find_them

  find_them >> pg.end

  empty_hq_destroyed = (
      no_one_hurt_but_base_destroyed |
      hq_destroyed_but_evacuated
  ) >> '.'
  empty_hq_destroyed >> pg.end

  hardship_and = (
      empty_hq_destroyed |
      (
          miners_were_exploring_then_lost |
          hq_destroyed_and_miners_lost |
          teleporter_malfunction
      ) >> ('.', '. If that wasn\'t hard enough,')
  ) >> ()

  (
      and_has_monsters |
      hq_destroyed_and_miners_lost
  ) >> '.' >> (reassurance | pg.end)
  
  hardship_and >> (spawn_has_erosion | has_monsters)
  spawn_has_erosion >> and_has_monsters

  (spawn_has_erosion | has_monsters | and_has_monsters) >> '.' >> pg.end

  reassurance >> pg.end

  pg.compile()
  return pg

PREMISES = _make_pg()