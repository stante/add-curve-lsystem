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
#  along with this program; if not, write to the Free Software Foundation,
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

bl_info = {
    "name"     : "Lindenmayer system",
    "author"   : "Alexander Stante",
    "version"  : (0, 1, 0),
    "blender"  : (2, 70, 0),
    "location" : "View3D > Add > Curve",
    "category" : "Add Curve",
    "warning"  : "Under development"
}

class LindenmayerSystem(bpy.types.Operator):
    """Construct turtle based on active object"""
    bl_idname = "object.lindenmayer_system"
    bl_label = "Create L-system"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    lsystem = StringProperty(name='L-System',
                             default='F[+F]F[-F]F')

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

    @classmethod
    def poll(cls, context):
        return True
        return bpy.context.object is not None
        
    def execute(self, context):
        self.apply_turtle()
        return {'FINISHED'}

    def invoke(self, context, event):
        #wm = context.window_manager
        #return wm.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        
        # Rules
        column.label("Rules:")
        column.prop(self, "lsystem")

        # Settings
        column.label("Settings")
        column.prop(self, "iterations")
        column.prop(self, "angle")
        column.prop(self, "bevel_depth")
        column.prop(self, "bevel_resolution")
        column.prop(self, "basic_length")

    def apply_turtle(self):
        direction = Vector((0, 0, 1))
        trans = Movement(direction)
        stack = []
        occ = count(self.lsystem, 'F')
        system = self.recursive_apply(self.iterations)

        # Create new curve object
        curve = bpy.data.curves.new('LSystem', 'CURVE')
        curve.dimensions = '3D'
        curve.fill_mode = 'FULL'
        curve.bevel_depth = self.bevel_depth
        curve.bevel_resolution = self.bevel_resolution

        obj = bpy.data.objects.new('LSystem', curve)
        bpy.context.scene.objects.link(obj)
        
        spline = branch(curve, Vector((0, 0, 0)))

        for symbol in system:
            if (symbol == 'F'):
                grow(spline, trans.get_vector(), self.basic_length * 1.0 / (occ ** self.iterations))
                continue

            if (symbol == '+'):
                trans.yaw(self.angle)
                continue
                
            if (symbol == '-'):
                trans.yaw(-self.angle)
                continue
                
            if (symbol == '^'):
                trans.pitch(self.angle)
                continue

            if (symbol == '&'):
                trans.pitch(-self.angle)
                continue

            if (symbol == '\\'):
                trans.roll(self.angle)
                continue

            if (symbol == '/'):
                trans.roll(-self.angle)
                continue

            if (symbol == '['):
                stack.append((spline, copy(trans)))

                spline = branch(curve, spline.bezier_points[-1].co)
                continue

            if (symbol == ']'):
                spline, trans = stack.pop()
                continue

    def recursive_apply(self, times):
        newstring = self.lsystem

        for i in range(times):
            newstring = newstring.replace('F', self.lsystem)

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
