from lib.lore.phrases import PhraseGraph
# Pylint doesn't like the PhraseGraph api's use of >>
# pylint: disable=expression-not-assigned,pointless-statement,too-many-locals


def _make_pg_found_hoard():
  pg = PhraseGraph()

  # Assume there is a collect_resources goal, and assume that goal requires
  # collecting crystals. This event will only be triggered if there are enough
  # crystals on the floor to complete the level.

  pg.start >> (
      'Wow! This ought to do it!',
      'You\'ve found quite the haul here.',
      'Our intel was accurate. Look at all those Energy Crystals!',
  ) >> (
      pg(
          'Now, transport these Energy Crystals back to your base.',
          'Bring this to your base to complete our mission!',
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
  ) >> () >> ~pg.states(
      'treasure_one',
      'treasure_many',
  ) >> ~pg.states(
      'has_monsters',
  ) >> pg.end

  pg.compile()
  return pg


def _make_pg_found_hq():
  pg = PhraseGraph()

  positive_greeting = pg(
      'Our Rock Raider HQ is safe and sound!',
      'Way to go, Cadet!',
  )

  neutral_greeting = pg(
      'You found the Rock Raider HQ.',
      'There it is!',
  )

  defend_it = pg(
      'Shore up the base defenses',
      'Now, get some Electric Fences up',
  ) >> pg.states(
      'has_monsters'
  )

  before_the_monsters = (
      'before the monsters find it too!',
      'and keep it safe from those %(monster_type)s monsters!',
      'and hope those monsters don\'t cause any more damage!',
  ) >> ~pg.states(
      'lost_miners_together',
      'lost_miners_apart',
      'lost_miners_one',
  )

  when_its_safe = pg(
      '. We need this base secure if we\'re going to',
      '. Once the base is safe,'
  )

  find_lost_miners = (
      pg(
          'find those lost Rock Raiders!',
      ) >> pg.states(
          'lost_miners_together', 'lost_miners_apart'
      ) |
      pg(
          'find the lost Rock Raider!',
      ) & 'lost_miners_one'
  )

  collect_resources = pg(
      'collect %(resources)s.',
      'get those %(resource_names)s.',
  ) & 'collect_resources'

  (
      pg.start
      >> (positive_greeting | neutral_greeting)
      >> ('Now, ', 'Now you should be able to')
      >> ~(pg.void >> defend_it >> when_its_safe)
      >> (find_lost_miners | collect_resources >> pg.end)
  )

  (
      (find_lost_miners | neutral_greeting >> defend_it >> before_the_monsters)
      >> ()
      >> ~pg.states('collect_resources')
      >> pg.end
  )

  pg.compile()
  return pg


def _make_pg_found_lost_miners():
  pg = PhraseGraph()

  pg.start >> (
      pg(
          'Look! It\'s one of the lost Rock Radiers!',
          'You found a lost Rock Raider!',
          'You found one of the lost Rock Raiders!',
      ) & 'found_miners_one' |
      pg(
          'Look at that! %(found_miners_count)s of the lost Rock Raiders are '
          'here, safely together.',
          'That\'s %(found_miners_count)s Rock Raiders found!',
          'You found %(found_miners_count)s of them here!'
      ) & 'found_miners_many'
  ) >> () >> ~pg(
      'Keep going!',
      'Keep searching, Cadet.',
  ) >> () >> ~pg(
      'We need to find all %(lost_miners_count)s before we can leave.',
  ) >> pg.end

  pg.compile()
  return pg


def _make_pg_found_all_lost_miners():
  pg = PhraseGraph()

  pg.start >> (
      pg(
          'Look! It\'s the lost Rock Raider!',
          'You found the missing Rock Raider!',
      ) & 'lost_miners_one' |
      pg(
          'And that makes %(lost_miners_count)s Rock Raiders found!',
          'You found all %(lost_miners_count)s Rock Raiders!',
          'That\'s all %(lost_miners_count)s Rock Raiders found!',
      )  # No need to check condition here. This isn't used without lost miners.
  ) >> () >> ~(
      pg(
          'Now, collect %(resources)s.'
      ) & 'collect_resources'
  ) >> pg.end

  pg.compile()
  return pg


FOUND_HOARD = _make_pg_found_hoard()
FOUND_HQ = _make_pg_found_hq()
FOUND_LOST_MINERS = _make_pg_found_lost_miners()
FOUND_ALL_LOST_MINERS = _make_pg_found_all_lost_miners()
