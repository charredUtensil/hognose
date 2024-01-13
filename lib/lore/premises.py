from typing import Iterable

from .phrases import PhraseGraph

def _make_pg():
  pg = PhraseGraph()

  greeting = (
      pg.then(
          'Are you ready for the next mission?',
          'I hope you\'re prepared for this one, Cadet.',
          'Cadet, are you up for some more action?') |
      pg.on('flooded_water').then(
          'Are you ready to set sail?',
          'I hope you packed your lifejacket, Cadet.') |
      pg.on('flooded_lava').then(
          'I hope you\'re not afraid of a little heat!')).then()

  we_found = (
      pg.then(
          'A recent scan',
          'The Hognose scanner',
          'The Hognose scanner aboard the L.M.S. Explorer'
          ).then(
          'found', 'has discovered', 'has indicated') |
      pg.then(
          'We',
          'The scanners',
          'The scanners aboard the L.M.S. Explorer'
          ).then(
          'have found', 'have located', 'have discovered')).then()

  a_cave = (
      pg.on('treasure_one').then(
          'a large Energy Crystal signature near here',
          'a nearby cave with an abundance of Energy Crystals') |
      pg.on('treasure_many').then(
          'large deposits of Energy Crystals in this cavern',
          'a cave system with an abundance of Energy Crystals') |
      pg.then(
        'another cavern where we can continue our mining operations')).then()

  however = pg.then(
      '. However,',
      '. Unfortunately,',
      '. Unfortunately for us,',
      '. The bad news?')

  be_careful = pg.then(
      ', but be careful!',
      ', but use caution!',
      '. Stay sharp, though.')

  miners_are_missing = pg.then().then(
      pg.on('lost_miners_one').then(
          'one of our Rock Raiders has gone missing',
          'a recent cave-in has trapped one of our Rock Radiers',
          'a teleporter malfunction sent one of our Rock Raiders to the wrong '
          'cave') |
      pg.on('lost_miners_together').then(
          'some of our Rock Raidiers have gone missing',
          'a recent cave-in has trapped some of our Rock Raiders',
          'a surveying group has not checked in for some time') |
      pg.on('lost_miners_many').then(
          'some of the Rock Raidiers that were exploring this cavern have '
          'gone missing',
          'a teleporter malfunction has scattered some of our miners '
          'throughout the cavern')).then()

  find_them = (
    pg.on('has_monsters').then(
      '. We need to find them before the %(monster_type)s monsters do.',
      ', and I hope they don\'t meet any of the %(monster_type)s monsters '
      'roaming this cavern.')
  )

  spawn_is_ruins = pg.on('spawn_is_ruins').then(
      'Recent seismic activity has damaged our Rock Raider HQ')

  hq_destroyed_and_miners_lost = spawn_is_ruins.then('.', ', and').then(
      pg.on('lost_miners_one').then(
          'one of our Rock Raiders is missing') |
      pg.on('lost_miners_together').then(
          'a group of Rock Raidiers are missing',
          'a group of Rock Raidiers are trapped somewhere in the cavern') |
      pg.on('lost_miners_many').then(
          'some of our Rock Raidiers are missing',
          'our Rock Raiders are trapped throughout the cavern')).then()

  hardship_and = (
      miners_are_missing.then(
          '.', 'and', '. If that wasn\'t hard enough,') |
      spawn_is_ruins.then('.', ', and') |
      hq_destroyed_and_miners_lost.then(
          '.', '. If that wasn\'t hard enough,')).then()

  spawn_has_erosion = pg.on('spawn_has_erosion').then(
      'we are dangerously close to a cavern full of lava',
      'we are concerned about nearby lava flows that could engulf this cavern')

  has_monsters = pg.on('has_monsters').then(
      'the tunnels here are full of creatures that threaten our operations',
      'we are picking up signs of large creatures in the area',
      'this cavern is inhabited by nests of %(monster_type)s monsters')

  pg.start.then(
      'Our mining operations have been going smoothly, and we are ready to '
      'move on to the next cavern.',
      'There is nothing out of the ordinary to report today.',
      'Things have been quiet and I hope they should remain that way, Cadet!',
      ).end()

  pg.start.then(greeting)
  greeting.then(we_found).then(a_cave)
  a_cave.then('.').end()
  a_cave.then(however | be_careful)
  (greeting | however).then(miners_are_missing)
  greeting.then(spawn_is_ruins)
  hq_destroyed_and_miners_lost.then('.').end()
  (however | hardship_and).then(spawn_has_erosion)
  miners_are_missing.then(find_them).then('.').end()
  be_careful.then(spawn_has_erosion | has_monsters)
  spawn_has_erosion.then('.').end()
  (hardship_and | spawn_has_erosion.then('. Also,')).then(has_monsters)
  has_monsters.then('.').end()
  return pg

PREMISES = _make_pg()