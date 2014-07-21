import bpy
op = bpy.context.active_operator

op.start_symbol = 'F'
op.production.name = ''
op.production.probability = 1.0
op.production.is_valid = True
op.production.show_extended = True
op.production.rule = 'F:=F'
op.iterations = 4
op.angle = 0.3926992416381836
op.bevel_depth = 0.0
op.bevel_resolution = 0
op.basic_length = 0.6800000667572021
op.productions.clear()
item_sub_1 = op.productions.add()
item_sub_1.name = ''
item_sub_1.probability = 1.0
item_sub_1.is_valid = True
item_sub_1.show_extended = True
item_sub_1.rule = 'F:=FF-[-F+F+F]+[+F-F-F]'
