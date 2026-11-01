RULES={
'Rice/Grain':('Safe edible surplus: consider donation first if food-safety/time controls allow. Inedible scraps: segregate as organic waste; use an authorised composting or anaerobic-digestion route where accepted.','organic'),
'Vegetarian':('Separate edible surplus from inedible scraps. Edible surplus may be donated if safe. Inedible organic material can go to authorised composting/organic processing where accepted.','organic'),
'Fruit':('Edible surplus can be considered for donation if safe. Fruit scraps are suitable for segregated organic processing/composting where accepted.','organic'),
'Bread':('Safe edible surplus may be donated. Inedible bread should be segregated and sent to an accepted organic-processing route; do not contaminate recyclable dry waste.','organic'),
'Dairy':('Donate only safe, within-shelf-life surplus with appropriate temperature control. Spoiled dairy should not be donated; use an authorised organic-waste route that accepts dairy.','organic'),
'Meat':('Do not donate unsafe/spoiled meat. Keep meat/bones separate and use an authorised animal-derived organic waste or anaerobic-digestion route only if the facility accepts it.','animal-derived'),
'Fish':('Keep fish waste separate and use an authorised animal-derived organic-waste/anaerobic-digestion route only if accepted. Do not put it on soil or in drains.','animal-derived'),
'Egg':('Safe surplus may be donated if compliant. Shells and inedible egg waste should be segregated for an accepted organic-processing route.','organic'),
'Beverage':('Separate liquid food waste from packaging. Avoid drains for fats/oils. Send organic residue to an accepted organic-processing route.','organic'),
'Bakery':('Safe edible surplus may be donated. Inedible bakery waste can be segregated for accepted organic processing.','organic')}
def get_rule(category): return RULES.get(category,('Prevent waste first; segregate edible surplus, organic waste and packaging, then use an authorised local treatment route based on facility acceptance.','general'))
