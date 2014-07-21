import bpy
op = bpy.context.active_operator

op.start_symbol = 'X'
op.production.name = ''
op.production.probability = 1.0
op.production.is_valid = True
op.production.show_extended = True
op.production.rule = 'X:=F[+X]F[-X]+X'
op.iterations = 7
op.angle = 0.4485498070716858
op.bevel_depth = 0.0
op.bevel_resolution = 0
op.basic_length = 1.850000023841858
op.productions.clear()
item_sub_1 = op.productions.add()
item_sub_1.name = ''
item_sub_1.probability = 1.0
item_sub_1.is_valid = True
item_sub_1.show_extended = True
item_sub_1.rule = 'X:=F[+X][-X]FX'
item_sub_1 = op.productions.add()
item_sub_1.name = ''
item_sub_1.probability = 1.0
item_sub_1.is_valid = True
item_sub_1.show_extended = True
item_sub_1.rule = 'F:=FF'
