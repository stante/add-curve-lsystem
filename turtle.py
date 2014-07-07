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
    "category" : "Add Curve"
    "warning"  : "Under development"
}

class TurtleOperator(bpy.types.Operator):
    """Construct turtle based on active object"""
    bl_idname = "object.turtle_operator"
    bl_label = "Construct turtle operator"

    lsystem = StringProperty(name='L-System',
                             default='F[+F]F[-F]F')

    iterations = IntProperty(name="Iterations",
                             min=0,
                             max=16,
                             default=0,
                             description="Iterations - number of rule applications")
    
    yaw_angle = FloatProperty(name="+,-", 
                              subtype="ANGLE",
                              unit='ROTATION',
                              default=radians(60))

    pitch_angle = FloatProperty(name='^,&',
                                subtype='ANGLE',
                                unit='ROTATION',
                                default=radians(60))

    roll_angle = FloatProperty(name='/,\\',
                               subtype='ANGLE',
                               unit='ROTATION',
                               default=radians(60))

    @classmethod
    def poll(cls, context):
        return True
        return bpy.context.object is not None
    
    def execute(self, context):
        self.apply_turtle()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def apply_turtle(self):
        direction = Vector((0, 0, 1))
        trans = Movement(direction)
        stack = []
        occ = self.lsystem.count('F')
        system = self.recursive_apply(self.iterations)

        # Create new curve object
        curve = bpy.data.curves.new('LSystem', 'CURVE')
        curve.dimensions = '3D'
        curve.fill_mode = 'FULL'
        obj = bpy.data.objects.new('LSystem', curve)
        bpy.context.scene.objects.link(obj)
        curve.splines.new('BEZIER')
        spline = curve.splines[-1]

        for symbol in system:
            if (symbol == 'F'):
                move_forward(spline, trans.get_vector(), 1.0)
                continue

            if (symbol == '+'):
                trans.yaw(self.yaw_angle)
                continue
                
            if (symbol == '-'):
                trans.yaw(-self.yaw_angle)
                continue
                
            if (symbol == '^'):
                trans.pitch(self.pitch_angle)
                continue

            if (symbol == '&'):
                trans.pitch(-self.pitch_angle)
                continue

            if (symbol == '\\'):
                trans.roll(self.roll_angle)
                continue

            if (symbol == '/'):
                trans.roll(-self.roll_angle)
                continue

            if (symbol == '['):
                oldpoint = spline.bezier_points[-1]

                stack.append((spline, copy(trans)))
                curve.splines.new('BEZIER')
                spline = curve.splines[-1]

                spline.bezier_points[-1].co = oldpoint.co
                continue

            if (symbol == ']'):
                spline, trans = stack.pop()
                continue

    def recursive_apply(self, times):
        newstring = self.lsystem

        for i in range(times):
            newstring = newstring.replace('F', self.lsystem)

        return newstring

def move_forward(spline, direction, scale):
    spline.bezier_points.add()
    newpoint = spline.bezier_points[-1]
    oldpoint = spline.bezier_points[-2]

    newpoint.co = oldpoint.co + (direction * 3 * scale)

    oldpoint.handle_right = oldpoint.co + direction
    newpoint.handle_left = newpoint.co - direction
    newpoint.handle_right = newpoint.co + direction
    
        
def menu_func(self, context):
    self.layout.operator(TurtleOperator.bl_idname, text="L-system", icon='PLUGIN')

def register():
    bpy.utils.register_class(TurtleOperator)
    bpy.types.INFO_MT_curve_add.append(menu_func)

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
