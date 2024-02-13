

    if stage == 'script':
      infos = [
          p.monster_spawner.script_info
          for p in self.cavern.conquest.somatic_planners
          if (
            hasattr(p, 'monster_spawner')
            and p.monster_spawner
            and p.monster_spawner.script_info)]
      for info in infos:
        for x, y in info.trigger_tiles:
          frame.draw_rect(
              SCRIPT_TRIGGER_COLOR,
              (x, y, 1, 1),
              1)
        for x, y in info.secondary_trigger_tiles:
          frame.draw_rect(
              SCRIPT_SECONDARY_TRIGGER_COLOR,
              (x, y, 1, 1),
              1)
      for info in infos:
        for x, y in info.trigger_tiles:
          frame.draw_line(
              SCRIPT_WIRE_COLOR,
              (x + 0.5, y + 0.5),
              (info.emerges[0][0] + 0.5, info.emerges[0][1] + 0.5))
        for x, y in info.secondary_trigger_tiles:
          frame.draw_line(
              SCRIPT_WIRE_COLOR,
              (x + 0.5, y + 0.5),
              (info.emerges[0][0] + 0.5, info.emerges[0][1] + 0.5))
        if info.discovery_tile:
          frame.draw_line(
              SCRIPT_WIRE_COLOR,
              (info.discovery_tile[0] + 0.5, info.discovery_tile[1] + 0.5),
              (info.emerges[0][0] + 0.5, info.emerges[0][1] + 0.5))
      for info in infos:
        if info.discovery_tile:
          frame.draw_circle(
              SCRIPT_TRIGGER_COLOR,
              (info.discovery_tile[0] + 0.5, info.discovery_tile[1] + 0.5),
              0.4)
      for info in infos:
        for x, y, r in info.emerges:
          frame.draw_rect(
              CREATURE_COLOR,
              (x - r, y - r, 2 * r + 1, 2 * r + 1),
              2)
        for (x1, y1, _), (x2, y2, _) in itertools.pairwise(info.emerges):
          frame.draw_line(
              CREATURE_COLOR,
              (x1 + 0.5, y1 + 0.5),
              (x2 + 0.5, y2 + 0.5),
              2)