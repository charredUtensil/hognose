from typing import Iterable

from .phrases import PhraseGraph

def _make_pg():
  pg = PhraseGraph()

  greeting = (
      pg(
          'Are you ready for the next mission?',
          'Welcome back, Cadet.',
          'I hope you\'re prepared for this one, Cadet.',
          'Cadet, are you up for some more action?') |
      pg(
          'Are you ready to set sail?',
          'I hope you packed your lifejacket, Cadet.'
          ) & 'flooded_water' |
      pg(
          'I hope you\'re not afraid of a little heat!',
          'You\'d better keep your cool with this one!'
          ) & 'flooded_lava'
      ) >> ()

  we_found = (
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
      ) >> ()

  a_cave = (
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

  however = pg(
      '. However,',
      '. Unfortunately,',
      '. Unfortunately for us,',
      '. The bad news?')

  be_careful = pg(
      ', but be careful!',
      ', but use caution!',
      '. Stay sharp!',
      ', but it won\'t be easy.')

  miners_are_missing = pg() >> (
      pg(
          'one of our Rock Raiders has gone missing',
          'a recent cave-in has trapped one of our Rock Radiers',
          'a teleporter malfunction sent one of our Rock Raiders to the wrong '
          'cave') & 'lost_miners_one' |
      pg(
          'some of our Rock Raidiers have gone missing',
          'a group of our Rock Raiders is trapped somewhere in this cavern',
          'a recent cave-in has trapped some of our Rock Raiders',
          'a surveying group has not checked in for some time'
          ) & 'lost_miners_together' |
      pg(
          'some of our Rock Raidiers were exploring this cavern and have '
          'gone missing',
          'a teleporter malfunction has scattered some of our miners '
          'throughout the cavern'
          ) & 'lost_miners_apart'
      ) >> ()

  find_them = (
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
      )

  spawn_is_ruins = pg(
      'Recent seismic activity has damaged our Rock Raider HQ',
      'An earthquake in this area has caused several cave-ins and destroyed '
      'part of our Rock Raider HQ.'
      ) & 'spawn_is_ruins'

  hq_destroyed_and_miners_lost = spawn_is_ruins >> ('.', ', and') >> (
      pg('one of our Rock Raiders is missing') & 'lost_miners_one' |
      pg(
          'a group of Rock Raidiers are missing',
          'a group of Rock Raidiers are trapped somewhere in the cavern'
          ) & 'lost_miners_together' |
      pg(
          'some of our Rock Raidiers are missing',
          'our Rock Raiders are trapped throughout the cavern'
          ) & 'lost_miners_apart'
    ) >> ()

  reassurance = pg(
      'don\'t get discouraged.',
      'don\'t worry:',
      ) >> pg(
      'I\'m sure you will be able to meet this challenge head-on!',
      'This is well within the capabilities of someone with your skillset.',
      'You\'ve triumphed over tough challenges before!',
      )

  spawn_has_erosion = pg(
      'we are dangerously close to a cavern full of lava',
      'we are concerned about nearby lava flows that could engulf this cavern'
      ) & 'spawn_has_erosion'

  has_monsters = pg(
      'the tunnels here are full of creatures that threaten our operations',
      'we are picking up signs of large creatures in the area',
      'this cavern is inhabited by nests of %(monster_type)s monsters') & 'has_monsters'

  pg.start >> (
      'Our mining operations have been going smoothly, and we are ready to '
      'move on to the next cavern.',
      'There is nothing out of the ordinary to report today.',
      'Things have been quiet and I hope they should remain that way, Cadet!',
      ) >> pg.end

  pg.start >> greeting
  greeting >> we_found >> a_cave >> (pg('.') >> pg.end | however | be_careful)
  be_careful >> (spawn_has_erosion | has_monsters)
  (greeting | however) >> miners_are_missing
  miners_are_missing >> (', and', '.') >> find_them >> pg.end
  greeting >> spawn_is_ruins
  hardship_and = (
      miners_are_missing >> ('.', 'and', '. If that wasn\'t hard enough,') |
      spawn_is_ruins >> ('.', ', and') |
      hq_destroyed_and_miners_lost >> ('.', '. If that wasn\'t hard enough,')
      ) >> ()
  (hq_destroyed_and_miners_lost | spawn_has_erosion) >> '.' >> (
      reassurance >> pg.end | pg.end)
  (however | hardship_and) >> spawn_has_erosion
  (hardship_and | spawn_has_erosion >> '. Also,') >> has_monsters
  has_monsters >> '.' >> pg.end

  pg.compile()
  return pg

PREMISES = _make_pg()