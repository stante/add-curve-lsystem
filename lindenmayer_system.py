# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Ftube.com/ree Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from copy import copy
from mathutils import *
from math import radians, pi
from random import random, seed
from collections import namedtuple
from bpy.props import StringProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import CollectionProperty
from bpy.props import PointerProperty
from bpy.props import BoolProperty
from bpy.types import PropertyGroup
from lindenmayer_system_parser import LindenmayerSystemParser, Token

bl_info = {
    "name"     : "Lindenmayer system",
    "author"   : "Alexander Stante",
    "version"  : (0, 1, 0),
    "blender"  : (2, 70, 0),
    "location" : "View3D > Add > Curve",
    "category" : "Add Curve",
    "warning"  : "Under development"
}

Rule = namedtuple('Rule', ['left', 'right', 'probability'])

def draw_rule(layout, rule, index):
    """Draw a Lindenmayer rule on the layout
    
    layout -- the layout to draw on
    rule   -- the rule to be drawn
    index  -- the index of the rule in the rule collection
    """
    col = layout.column(align=True)
    box = col.box()

    row = box.row()

    # Extended arrow
    prop = row.operator("lindenmayer_system.production_show_extended", 
                        icon='TRIA_DOWN' if rule.show_extended else 'TRIA_RIGHT', 
                        emboss=False)
    prop.index = index

    # Rule string
    row.prop(rule, "rule", icon='NONE' if rule.is_valid else 'ERROR')

    rowmove = row.row(align=True)
   
    # Move up
    op = rowmove.operator("lindenmayer_system.production_move", icon='TRIA_UP')
    op.direction = 'UP'
    op.index = index
    
    # Move down
    op = rowmove.operator("lindenmayer_system.production_move", icon='TRIA_DOWN')
    op.direction = 'DOWN'
    op.index = index
    
    # Remove rule
    prop = row.operator("lindenmayer_system.production_remove", icon='X', emboss=False)
    prop.index = index

    # Extendend properties
    if rule.show_extended:
        box = col.box()
        col = box.column()
        col.prop(rule, "probability")
        
    return box

def check_rule(self, context):
    if self.parser.rule_valid(self.rule):
        self.is_valid = True
    else:
        self.is_valid = False


class ProductionItem(bpy.types.PropertyGroup):
    is_valid = BoolProperty(True)
    rule = StringProperty(name="", default="F:=F", update=check_rule)

    show_extended = BoolProperty(default=True)

    probability = FloatProperty(name="Probability",
                                min=0,
                                max=1,
                                default=1)

    parser = LindenmayerSystemParser()
    
    def get_parsed(self):
        p = self.parser.parse(self.rule)
        
        return (p[0], p[2:])


class ProductionShowExtended(bpy.types.Operator):
    bl_idname = "lindenmayer_system.production_show_extended"
    bl_label = ""

    index = IntProperty()
    
    def execute(self, context):
        settings = context.active_operator
        settings.productions[self.index].show_extended = not settings.productions[self.index].show_extended
        
        return {'FINISHED'}

class ProductionMove(bpy.types.Operator):
    bl_idname = "lindenmayer_system.production_move"
    bl_label = ""

    direction = StringProperty()
    index = IntProperty()

    def execute(self, context):
        rules = context.active_operator.productions
        if self.direction == 'UP' and self.index > 0:
            rules.move(self.index, self.index - 1)
        elif self.direction == 'DOWN' and self.index < len(rules) - 1:
            rules.move(self.index, self.index + 1)

        return {'FINISHED'}

class ProductionRemove(bpy.types.Operator):
    bl_idname = "lindenmayer_system.production_remove"
    bl_label = ""

    index = IntProperty()

    def execute(self, context):
        context.active_operator.productions.remove(self.index)

        return {'FINISHED'}

class ProductionAdd(bpy.types.Operator):
    """Operator to add a new rule to the Lindenmayer System

    Adds a new rule by adding a ProductionItem to the production collection
    """
    bl_idname = "lindenmayer_system.production_add"
    bl_label = ""

    def execute(self, context):
        settings = context.active_operator

        if settings.production.is_valid:
            prop = settings.productions.add()
            prop.rule = settings.production.rule

        return {'FINISHED'}

class LindenmayerSystem(bpy.types.Operator):
    """Construct turtle based on active object"""
    bl_idname = "curve.lindenmayer_system"
    bl_label = "Create L-system"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    start_symbol = StringProperty(name="Start Symbol", default="F")
    production = PointerProperty(type=ProductionItem, name="Production")

    iterations = IntProperty(name="Iterations",
                             min=0,
                             max=8,
                             default=0,
                             description="Number of iterations for rule application")
    
    angle = FloatProperty(name="Angle", 
                          subtype="ANGLE",
                          unit='ROTATION',
                          default=radians(60),
                          description="Angle for each branching")
    
    rule_seed = IntProperty(name="Rule Seed",
                            default=0,
                            description="Seed for rule random number generator")
    
    angle_seed = IntProperty(name="Angle Seed",
                             default=0,
                             description="Seed for angle random number generator")
    
    random_angle = FloatProperty(name="Random Angle",
                                 min=0,
                                 max=1,
                                 precision=3,
                                 step=0.1,
                                 default=0,
                                 description="Variation for branching angle")
    
    bevel_depth = FloatProperty(name="Depth",
                                min=0,
                                precision=3,
                                step=0.1,
                                default=0,
                                description="Bevel depth")

    bevel_resolution = IntProperty(name="Resolution",
                                   min=0,
                                   max=32,
                                   default=0,
                                   description="Resolution for the bevel depth")
    
    basic_length = FloatProperty(name="Length",
                                 min=0, 
                                 default=2,
                                 description="Basic length of generated plant")

    productions = CollectionProperty(type=ProductionItem)

    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        self.apply_turtle(self)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
        
    def get_angle(self):
        if self.random_angle != 0:
            var = pi / 4 * self.random_angle
            var = var * (1 - random() * 2)
            return self.angle + var
        else:
            return self.angle

    def draw(self, context):
        settings = context.active_operator
        layout = self.layout
        column = layout.column()

        # Rules
        column.label("Rules:")
        row = column.row(align=True)
        row.prop(settings.production, "rule", icon='NONE' if settings.production.is_valid
                 else 'ERROR')
        row.operator("lindenmayer_system.production_add", icon='ZOOMIN')
        
        column.separator()
        row = column.row()
        row.prop(settings, "rule_seed")
        row.prop(settings, "iterations")
        column.separator()

        for idx, prop in enumerate(settings.productions):
            draw_rule(column, prop, idx)

        # Settings
        column.separator()
        column.label("Settings:")
        column.prop(settings, "start_symbol")
        column2 = column.column(align=True)
        column2.prop(settings, "angle")
        column2.prop(settings, "random_angle")
        column2.prop(settings, "angle_seed")
        column.prop(settings, "bevel_depth")
        column.prop(settings, "bevel_resolution")
        column.prop(settings, "basic_length")

    def apply_turtle(self, settings):
        direction = Vector((0, 0, 1))
        stack = []

        # Create start token
        start = [Token(type='SYMBOL', value=settings.start_symbol)]

        # Construct dictionary rules
        rules = {}
        for production in settings.productions:
            l, r = production.get_parsed()
            new_rule = Rule(l, r, production.probability)

            if l.value in rules:
                rules[l.value].append(new_rule)
            else:
                rules[l.value] = [new_rule]

        system = apply_rules(start, rules, settings.iterations, self.rule_seed)
        length = calculate_length(system, settings.basic_length)

        turtle = TurtleMovement(direction, length)

        # Get curve
        curve = turtle.get_curve()
        curve.bevel_depth = settings.bevel_depth
        curve.bevel_resolution = settings.bevel_resolution

        # Initialize seed for angle variations
        seed(self.angle_seed)

        for token in system:
            if (token.type == 'SYMBOL'):
                if (token.value == 'F'):
                    turtle.forward(length)
                    continue

            if (token.type == 'DIRECTION'):
                if (token.value == '+'):
                    turtle.yaw(self.get_angle())
                    continue
                
                if (token.value == '-'):
                    turtle.yaw(-self.get_angle())
                    continue
                
                if (token.value == '^'):
                    turtle.pitch(self.get_angle())
                    continue

                if (token.value == '&'):
                    turtle.pitch(-self.get_angle())
                    continue

                if (token.value == '\\'):
                    turtle.roll(self.get_angle())
                    continue

                if (token.value == '/'):
                    turtle.roll(-self.get_angle())
                    continue

            if (token.type == 'PUSH'):
                stack.append(copy(turtle))
                turtle.branch()
                continue

            if (token.type == 'POP'):
                turtle.branch_end()
                turtle = stack.pop()
                continue

def system_to_human(system):
    string = ""
    for token in system:
        if token.type == 'SYMBOL' or token.type == 'DIRECTION' or token.type == 'PUSH' or token.type == 'POP':
            string += token.value

    return string

def apply_single_rule(start, rules):
    lsystem = []
    for token in start:
        if token.type == 'SYMBOL':
            if token.value in rules:
                rewrite_rule = rules[token.value]

                if len(rewrite_rule) > 1:
                    # Rules with probability
                    rnd = random()
                    probability = 0
                    for r in rewrite_rule:
                        probability += r.probability
                        if rnd <= probability:
                            lsystem.extend(r.right)
                            break
                else:
                    lsystem.extend(rewrite_rule[0].right)
            else:
                lsystem.append(token)
        else:
            lsystem.append(token)

    return lsystem
    
def apply_rules(start, rules, times, rseed):
    lsystem = start
    seed(rseed)
    for i in range(times):
        lsystem = apply_single_rule(lsystem, rules)

    return lsystem

def calculate_length(system, basic_length):
    cnt = 0
    stack = []

    for token in system:
        if token.type == 'SYMBOL' and token.value == 'F' and not stack:
            cnt+=1
            continue

        if token.type == 'PUSH':
            stack.append('[')

        if token.type == 'POP':
            stack.pop()

    return basic_length / cnt if cnt else 0
        
    
def new_spline(curve, position):
    curve.splines.new('BEZIER')
    spline = curve.splines[-1]
    spline.bezier_points[-1].co = position
    return spline

    
def menu_func(self, context):
    self.layout.operator(LindenmayerSystem.bl_idname, text="L-system", icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_curve_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_curve_add.remove(menu_func)

class TurtleMovement:

    def __init__(self, vector, length):
        self._has_changed = True
        self._vector = vector
        self._basic_length = length

        # Create new curve object
        self._curve = bpy.data.curves.new('LSystem', 'CURVE')
        self._curve.dimensions = '3D'
        self._curve.fill_mode = 'FULL'
        self._curve.resolution_u = 1

        self._object = bpy.data.objects.new('LSystem', self._curve)
        self._object.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.link(self._object)
        
        self.branch_at(Vector((0, 0, 0)))
        
    def forward(self, amount):
        direction = self.get_vector()
        direction = direction * amount
        new_position = self._spline.bezier_points[-1].co + direction

        if self.has_changed() or len(self._spline.bezier_points) == 1:
            # Add second point
            self._spline.bezier_points.add()

        p1 = self._spline.bezier_points[-1]
        p2 = self._spline.bezier_points[-2]

        p1.co = new_position
            
        p1.handle_left = p1.co - direction / 5
        handle_direction = (p2.co - p1.co ).normalized()
        handle_direction = handle_direction * self._basic_length / 5
        p1.handle_right = p1.co - handle_direction
        p2.handle_right = p2.co + direction / 5

    def branch_at(self, position):
        """Creates a branch in curve at position
        
        Arguments:
        curve    -- Blender curve
        position -- Starting point of the new branch
        """
    
        # New spline (automatically creates a bezier point)
        self._spline = new_spline(self._curve, position)
        
        p = self._spline.bezier_points[-1]
        p.handle_left = p.co - self.get_vector() * self._basic_length / 5
            
    def branch(self):
        self.branch_at(self._spline.bezier_points[-1].co)
        

    def branch_end(self):
        if len(self._spline.bezier_points) == 1:
            self.remove_spline()

    # Just temporary
    def remove_spline(self):
        self._curve.splines.remove(self._spline)

    # Just temporary
    def get_curve(self):
        return self._curve

    def rotate(self, amount, axis):
        self._has_changed = True
        self._vector = self._vector * Matrix.Rotation(amount, 3, axis)
            
    def yaw(self, amount):
        self._has_changed = True
        self.rotate(amount, 'Y')

    def pitch(self, amount):
        self._has_changed = True
        self.rotate(amount, 'X')

    def roll(self, amount):
        self._has_changed = True
        self.rotate(amount, 'Z')

    def get_vector(self):
        return self._vector

    def has_changed(self):
        if self._has_changed:
            self._has_changed = False
            return True
        else:
            return False
            
if __name__ == '__main__':
    register()
