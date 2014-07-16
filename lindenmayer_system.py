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
from math import radians
from bpy.props import StringProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import CollectionProperty
from bpy.props import PointerProperty
from bpy.props import BoolProperty
from bpy.types import PropertyGroup

bl_info = {
    "name"     : "Lindenmayer system",
    "author"   : "Alexander Stante",
    "version"  : (0, 1, 0),
    "blender"  : (2, 70, 0),
    "location" : "View3D > Add > Curve",
    "category" : "Add Curve",
    "warning"  : "Under development"
}

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
    row.prop(rule, "rule")

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

class ProductionItem(bpy.types.PropertyGroup):
    rule = StringProperty("Rule", name="")

    show_extended = BoolProperty(default=True)

    probability = FloatProperty(name="Probability",
                                min=0,
                                max=1,
                                default=1)

class OperatorSettings(bpy.types.PropertyGroup):
    bl_idname = "lindenmayer_system.settings"

    rule = StringProperty(name="Rule", default='F[+F]F[-F]F')

    iterations = IntProperty(name="Iterations",
                             min=0,
                             max=8,
                             default=0,
                             description="Iterations - number of rule applications")
    
    angle = FloatProperty(name="Angle", 
                              subtype="ANGLE",
                              unit='ROTATION',
                              default=radians(60))
    
    bevel_depth = FloatProperty(name="Depth",
                                min=0,
                                precision=3,
                                step=0.1,
                                default=0)

    bevel_resolution = IntProperty(name="Resolution",
                                   min=0,
                                   max=32,
                                   default=0)
    
    basic_length = FloatProperty(name="Length",
                                 min=0, 
                                 default=2)

    productions = CollectionProperty(type=ProductionItem)

class ProductionShowExtended(bpy.types.Operator):
    bl_idname = "lindenmayer_system.production_show_extended"
    bl_label = ""

    index = IntProperty()
    
    def execute(self, context):
        settings = context.window_manager.lindenmayer_settings
        settings.productions[self.index].show_extended = not settings.productions[self.index].show_extended
        
        return {'FINISHED'}

class ProductionMove(bpy.types.Operator):
    bl_idname = "lindenmayer_system.production_move"
    bl_label = ""

    direction = StringProperty()
    index = IntProperty()

    def execute(self, context):
        rules = context.window_manager.lindenmayer_settings.productions
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
        context.window_manager.lindenmayer_settings.productions.remove(self.index)

        return {'FINISHED'}

class ProductionAdd(bpy.types.Operator):
    """Operator to add a new rule to the Lindenmayer System

    Adds a new rule by adding a ProductionItem to the production collection
    """
    bl_idname = "lindenmayer_system.production_add"
    bl_label = ""

    def execute(self, context):
        settings = context.window_manager.lindenmayer_settings
        prop = settings.productions.add()
        prop.rule = settings.rule

        return {'FINISHED'}

class LindenmayerSystem(bpy.types.Operator):
    """Construct turtle based on active object"""
    bl_idname = "curve.lindenmayer_system"
    bl_label = "Create L-system"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        self.apply_turtle(context.window_manager.lindenmayer_settings)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

    def draw(self, context):
        settings = context.window_manager.lindenmayer_settings
        layout = self.layout
        column = layout.column()

        # Rules
        row = column.row(align=True)
        row.prop(settings, "rule", icon='ERROR')
        row.operator("lindenmayer_system.production_add", icon='ZOOMIN')

        for idx, prop in enumerate(settings.productions):
            draw_rule(column, prop, idx)

        # Settings
        column.separator()
        column.label("Settings")
        column.prop(settings, "iterations")
        column.prop(settings, "angle")
        column.prop(settings, "bevel_depth")
        column.prop(settings, "bevel_resolution")
        column.prop(settings, "basic_length")

    def apply_turtle(self, settings):
        direction = Vector((0, 0, 1))
        trans = Movement(direction)
        stack = []
        occ = count(settings.rule, 'F')
        system = recursive_apply("F", settings.rule, settings.iterations)

        # Create new curve object
        curve = bpy.data.curves.new('LSystem', 'CURVE')
        curve.dimensions = '3D'
        curve.fill_mode = 'FULL'
        curve.bevel_depth = settings.bevel_depth
        curve.bevel_resolution = settings.bevel_resolution

        obj = bpy.data.objects.new('LSystem', curve)
        bpy.context.scene.objects.link(obj)
        
        spline = branch(curve, Vector((0, 0, 0)))

        for symbol in system:
            if (symbol == 'F'):
                grow(spline, trans.get_vector(), settings.basic_length * 1.0 / (occ ** settings.iterations))
                continue

            if (symbol == '+'):
                trans.yaw(settings.angle)
                continue
                
            if (symbol == '-'):
                trans.yaw(-settings.angle)
                continue
                
            if (symbol == '^'):
                trans.pitch(settings.angle)
                continue

            if (symbol == '&'):
                trans.pitch(-settings.angle)
                continue

            if (symbol == '\\'):
                trans.roll(settings.angle)
                continue

            if (symbol == '/'):
                trans.roll(-settings.angle)
                continue

            if (symbol == '['):
                stack.append((spline, copy(trans)))

                spline = branch(curve, spline.bezier_points[-1].co)
                continue

            if (symbol == ']'):
                spline, trans = stack.pop()
                continue

def recursive_apply(start, rules, times):
    newstring = start

    for i in range(times):
        newstring = newstring.replace('F', rules)

    return newstring

def count(string, character):
    cnt = 0
    stack = []

    for c in string:
        if c == character and not stack:
            cnt+=1
            continue

        if c == '[':
            stack.append('[')

        if c == ']':
            stack.pop()

    return cnt
        
def grow(spline, direction, amount):
    newpoint = spline.bezier_points[-1]
    oldpoint = spline.bezier_points[-2]
    direction = direction * amount

    newpoint.co = newpoint.co + direction

    oldpoint.handle_left = oldpoint.co - direction
    oldpoint.handle_right = oldpoint.co + direction
    newpoint.handle_left = newpoint.co - direction
    newpoint.handle_right = newpoint.co + direction
    
def branch(curve, position):
    """Creates a branch in curve at position
    
    Arguments:
    curve    -- Blender curve
    position -- Starting point of the new branch
    """

    # New spline (automatically creates a bezier point)
    spline = new_spline(curve, position)

    # Add second point
    spline.bezier_points.add()
    newpoint = spline.bezier_points[-1]
    oldpoint = spline.bezier_points[-2]
    newpoint.co = oldpoint.co
    
    return spline

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
    bpy.types.WindowManager.lindenmayer_settings = PointerProperty(type=OperatorSettings,
                                                                   name="Operator Settings")

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_curve_add.remove(menu_func)

class Movement:
    def __init__(self, vector):
        self._vector = vector

    def rotate(self, amount, axis):
        self._vector = self._vector * Matrix.Rotation(amount, 3, axis)

    def yaw(self, amount):
        self.rotate(amount, 'X')

    def pitch(self, amount):
        self.rotate(amount, 'Y')

    def roll(self, amount):
        self.rotate(amount, 'Z')

    def get_vector(self):
        return self._vector

if __name__ == '__main__':
    register()
