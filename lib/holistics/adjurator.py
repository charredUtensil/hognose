import math

from lib.plastic import Objective, FindMinerObjective, ResourceObjective, VariableObjective

def adjure(cavern):
  def gen():
    for planner in cavern.conquest.somatic_planners:
      yield from planner.objectives
  objs = list(Objective.uniq(gen()))
  # If none of the caverns have objectives, generate one to collect a
  # reasonable number of crystals.
  crystals = math.floor(
      cavern.diorama.total_crystals * cavern.context.crystal_goal_ratio)
  crystals -= (crystals % 5)
  if (not any(isinstance(o, FindMinerObjective) or isinstance(o, ResourceObjective) for o in objs)
      or (len(objs) == 1
          and isinstance(objs[0], ResourceObjective)
          and not objs[0].ore
          and not objs[0].studs
          and objs[0].crystals < crystals)):
    objs = Objective.uniq(objs + [ResourceObjective(crystals=crystals)])
  cavern.diorama.objectives.extend(objs)