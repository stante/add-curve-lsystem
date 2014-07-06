import bpy
import mathutils

yaw_value = 0.1
pitch_value = 0.1
roll_value = 0.1
operations = []

class TurtleOperator(bpy.types.Operator):
    """Construct turtle based on active object"""
    bl_idname = "object.turtle_operator"
    bl_label = "Construct turtle operator"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None
    
    def execute(self, context):
        apply_turtle("F+FF")
        return {'FINISHED'}
  
def register():
    bpy.utils.register_class(TurtleOperator)  

def apply_turtle(lsystem):
    for symbol in lsystem:
        if (symbol == 'F'):
            for op in operations:
                op()
            operations.clear()
            operations.append(move)
            bpy.ops.object.duplicate()
            continue
        if (symbol == '+'):
            operations.append(yaw_up)
            continue
        if (symbol == '-'):
            operations.append(yaw_down)
            continue
        if (symbol == '^'):
            operations.append(pitch_up)
            continue
        if (symbol == '&'):
            operations.append(pitch_down)
            continue
        if (symbol == '\\'):
            operations.append(roll_up)
            continue
        if (symbol == '/'):
            operations.append(roll_down)
            continue


       
def move():
    bpy.ops.transform.translate(value=(0, 0, bpy.context.active_object.dimensions.z))
    
def yaw_up():
    bpy.ops.transform.rotate(value=yaw_value, axis=(1, 0,0 ), constraint_orientation='LOCAL')
    
def yaw_down():
    bpy.ops.transform.rotate(value=-yaw_value, axis=(1, 0, 0), constraint_orientation='LOCAL')
    
def pitch_up():
    bpy.ops.transform.rotate(value=pitch_value, axis=(0, 1, 0), constraint_orientation='LOCAL')

def pitch_down():
    bpy.ops.transform.rotate(value=-pitch_value, axis=(0, 1, 0), constraint_orientation='LOCAL')
    
def roll_up():
    bpy.ops.transform.rotate(value=roll_value, axis=(0, 0, 1), constraint_orientation='LOCAL')
    
def roll_down():
    bpy.ops.transform.rotate(value=-roll_value, axis=(0, 0, 1), constraint_orientation='LOCAL')
    

if __name__ == '__main__':
    register()