import bpy
from copy import copy
from mathutils import Matrix
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
        return bpy.context.object is not None
    
    def execute(self, context):
        self.apply_turtle()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def apply_turtle(self):
        trans = Movement(bpy.context.object.matrix_basis)
        stack = []
        system = self.recursive_apply(self.iterations)
        print(system)

        for symbol in system:
            if (symbol == 'F'):
                bpy.ops.object.duplicate(linked=True)
                bpy.context.object.matrix_basis = trans.get_matrix()
                trans.move(bpy.context.object.dimensions.z)
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
                stack.append(copy(trans))
                continue

            if (symbol == ']'):
                trans = stack.pop()
                continue

    def recursive_apply(self, times):
        newstring = self.lsystem

        for i in range(times):
            newstring = newstring.replace('F', self.lsystem)

        return newstring

def register():
    bpy.utils.register_class(TurtleOperator)  

class Movement:
    def __init__(self, matrix):
        self._matrix = matrix

    def move(self, distance):
        self._matrix = self._matrix * Matrix.Translation((0, 0, distance))

    def yaw(self, amount):
        self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'X')

    def pitch(self, amount):
        self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'Y')

    def roll(self, amount):
        self._matrix = self._matrix * Matrix.Rotation(amount, 4, 'Z')

    def get_matrix(self):
        return self._matrix


if __name__ == '__main__':
    register()
