import bpy
from copy import copy
from mathutils import *
from math import radians
from bpy.props import StringProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty

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
                move_forward(spline, trans.get_vector())
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

def move_forward(spline, direction):
    spline.bezier_points.add()
    newpoint = spline.bezier_points[-1]
    oldpoint = spline.bezier_points[-2]

    newpoint.co = oldpoint.co + (direction * 3)

    oldpoint.handle_right = oldpoint.co + direction
    newpoint.handle_left = newpoint.co - direction
    newpoint.handle_right = newpoint.co + direction
    
        
def register():
    bpy.utils.register_class(TurtleOperator)  

# class Movement:
#     def __init__(self, matrix):
#         self._matrix = matrix

#     def move(self, distance):
#         self._matrix = self._matrix * Matrix.Translation((0, 0, distance))

#     def yaw(self, amount):
#         self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'X')

#     def pitch(self, amount):
#         self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'Y')

#     def roll(self, amount):
#         self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'Z')

#     def get_matrix(self):
#         return self._matrix

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
