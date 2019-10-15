bl_info = {
    "name": "Bone Hair Strands",
    "description": "Simulate Bone Pendulum Hair. Options a pendulum simulation and baking it are found in the Properties Panel of the 3D View.",
    "author": "Leander",
    "category": "Rigging",
    "version": (0, 5),
    "blender": (2, 79, 0),
    "warning": "Unfortunate bone rotation are not exception handled."
    }

import bpy
import bgl
import blf
import math
import mathutils

def draw_line_3d(color, start, end, width=1):
    bgl.glLineWidth(width)
    bgl.glColor4f(*color)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex3f(*start)
    bgl.glVertex3f(*end)

def draw_typo_2d(color, text):
    font_id = 0  # XXX, need to find out how best to get this.
    # draw some text
    bgl.glColor4f(*color)
    blf.position(font_id, 20, 70, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, text)

def get_active_pose_bone(context):
    if context.scene.objects.active == None or context.scene.objects.active.type != 'ARMATURE':
        return None
    ob = context.scene.objects.active
    if ob.data.bones.active == None:
        return None
    bone = ob.pose.bones[ob.data.bones.active.name]
    return bone

class HairStrand(object):
    def __init__(self, bone):
        self.gravity_vector = mathutils.Vector((0, 0, -1))
        
        self.bone = bone
        if bone.parent == None:
            raise Exception("HairStrand Bone needs a parent.")
        self.parent = self.bone.parent
        self.L = self.bone.length
        """
        self.up_axis = bone.bonehair.up_axis
        
        self.initial_rotation = bone.bonehair.initial_rotation
        self.theta = bone.bonehair.theta
        self.phi = bone.bonehair.phi
        self.theta_v = bone.bonehair.theta_v
        self.phi_v = bone.bonehair.phi_v
        self.retain_velocity = bone.bonehair.retain_velocity
        self.simulation_strength = bone.bonehair.simulation_strength
        self.preservation_direction = bone.bonehair.preservation_direction
        self.preservation_force = bone.bonehair.preservation_force
        movement_force
        parent_rest_quat
        self.steps = bone.bonehair.steps
        previous_base_position
        previous_base_velocity
        """
    
    def initialize(self):
        self.bone.rotation_mode = 'QUATERNION'
        self.bone.rotation_quaternion = mathutils.Quaternion((1, 0, 0, 0))
        self.bone.bonehair.theta_v = self.bone.bonehair.phi_v = 0.0
        self.bone.bonehair.theta, self.bone.bonehair.phi = self.get_angles_from_bone()
        # self.initial_rotation, self.up_axis, self.preservation_direction, parent_rest_quat
        self.set_initial_rotation(self.bone.bonehair.theta, self.bone.bonehair.phi)
        
    def set_position(self):
        self.bone.bonehair.theta_v = self.bone.bonehair.phi_v = 0.0
        self.bone.bonehair.theta, self.bone.bonehair.phi = self.get_angles_from_bone()
        self.bone.bonehair.initial_rotation = self.bone.bonehair.theta, self.bone.bonehair.phi
        
    def set_preservation(self):
        v = self.bone.tail - self.bone.head
        self.bone.bonehair.preservation_direction = v / v.length
        self.bone.bonehair.preservation_force = v.length
        
    def set_up_axis(self):
        v = self.bone.tail - self.bone.head
        self.bone.bonehair.up_axis = v / v.length
        
    def reset_movement(self):
        self.bone.bonehair.theta_v = self.bone.bonehair.phi_v = 0.0
        self.bone.bonehair.active = True
        self.bone.bonehair.theta, self.bone.bonehair.phi = self.bone.bonehair.initial_rotation
        self.bone.bonehair.previous_base_position = self.anchor()
        self.bone.bonehair.previous_base_velocity = mathutils.Vector((0, 0, 0))
        self.display_rotation()
    
    def get_angles_from_bone(self):
        v = self.bone.tail - self.bone.head
        phi = math.atan2(v.y, v.x)
        theta = self.gravity_vector.angle(v)
        return theta, phi
    
    def set_initial_rotation(self, theta, phi):
        self.bone.bonehair.initial_rotation = theta, phi
        self.bone.bonehair.up_axis = mathutils.Vector(self.get_bob(1, theta + math.pi/2, phi))
        
        direction = self.bone.tail - self.bone.head
        self.bone.bonehair.preservation_direction = direction / direction.length
        
        self.bone.bonehair.parent_rest_quat = self.parent.matrix.decompose()[1]
        
    
    def anchor(self):
        return self.bone.matrix.translation
    
    def get_bob(self, L, theta, phi):
        x = L * math.sin(theta) * math.cos(phi)
        y = L * math.sin(theta) * math.sin(phi)
        z = -L * math.cos(theta)
        return x, y, z
    
    def display_rotation(self):
        location = self.anchor()
        
        L, theta, phi = self.L, self.bone.bonehair.theta, self.bone.bonehair.phi
        x, y, z = self.get_bob(L, theta, phi)
        pointer = mathutils.Vector((x, y, z))
        
        up_axis = self.get_up_axis()
        up_difference = up_axis.rotation_difference(mathutils.Vector((0, 0, 1.0))).to_matrix().to_4x4()
        
        pointer.rotate(up_difference)
        
        quat = pointer.to_track_quat('Y', 'Z').to_matrix().to_4x4()
        quat = up_difference.inverted() * quat
        self.bone.matrix = mathutils.Matrix.Translation(location) * quat
    
    def get_parent_quat_mat(self):
        return self.parent.matrix.decompose()[1].to_matrix().to_4x4() * self.bone.bonehair.parent_rest_quat.to_matrix().to_4x4().inverted()
    
    def get_preservation_force(self):
        return self.get_parent_quat_mat() * self.bone.bonehair.preservation_direction * self.bone.bonehair.preservation_force
    
    def get_up_axis(self):
        return self.get_parent_quat_mat() * self.bone.bonehair.up_axis
    
    def get_initial_direction(self):
        direction = self.get_bob(self.L, * self.bone.bonehair.initial_rotation)
        return self.get_parent_quat_mat() * mathutils.Vector((direction))

    def calculate_preservation_force(self):
        direction = self.bone.bonehair.preservation_direction
        force_phi = math.atan2(direction.y, direction.x)
        force_theta = self.gravity_vector.angle(direction)
        
        theta, phi = self.bone.bonehair.initial_rotation
        print(force_theta, theta)
        
        if abs(force_phi - phi) > 0.000001:
            raise Exception('Phi angle doesn\'t match.')
        
        if theta >= force_theta:
            raise Exception('Force has to point more upward than rest position.')
        
        f = math.sin(theta) / math.sin(force_theta - theta) / direction.length
        
        self.bone.bonehair.preservation_force = f
        print(self.bone.bonehair.preservation_force)
    
    def do_step(self):
        theta_v, phi_v, theta, phi, L = self.bone.bonehair.theta_v, self.bone.bonehair.phi_v, self.bone.bonehair.theta, self.bone.bonehair.phi, self.L
        
        f = self.gravity_vector.copy()
        
        # check anchor movement
        location = self.anchor()
        velocity = location - self.bone.bonehair.previous_base_position
        acceleration = velocity - self.bone.bonehair.previous_base_velocity
        self.bone.bonehair.previous_base_velocity = velocity.copy()
        self.bone.bonehair.previous_base_position = location.copy()
        
        
        f -= acceleration * self.bone.bonehair.movement_force
        
        f += self.get_preservation_force()
        
        f *= self.bone.bonehair.simulation_strength
        
        steps = self.bone.bonehair.steps
        deltaT = 1 / steps
        for i in range(steps):
            # kinetic energy
            phi_a = 0.0001
            theta_a = math.pow(phi_v, 2) * math.sin(theta) * math.cos(theta)
                
            if theta != 0.0:
                phi_a = - 2 * theta_v * phi_v / math.tan(theta)
            # potential energy (is included in the generalized forces)
            # theta_a -= G/L * math.sin(theta)
            
            # convert generalized forces (directions)
            theta_d = mathutils.Vector((math.cos(phi) * math.cos(theta), math.sin(phi) * math.cos(theta), math.sin(theta)))
            phi_d = mathutils.Vector((-math.sin(phi), math.cos(phi),0))
            
            theta_f = theta_d.dot(f) / math.pow(theta_d.length, 2)
            phi_f = phi_d.dot(f) / math.pow(phi_d.length, 2)
            
            # apply generalized forces
            theta_a += theta_f / L
            phi_a += phi_f / L
            
            
            theta = theta_a / 2 * math.pow(deltaT, 2) + theta_v * deltaT + theta
            phi = phi_a / 2 * math.pow(deltaT, 2) + phi_v * deltaT + phi

            theta_v = theta_a * deltaT + theta_v
            phi_v = phi_a * deltaT + phi_v
            
        self.bone.bonehair.theta = theta
        self.bone.bonehair.phi = phi
        self.bone.bonehair.theta_v = theta_v * self.bone.bonehair.retain_velocity
        self.bone.bonehair.phi_v = phi_v * self.bone.bonehair.retain_velocity


def draw_callback_3d(self, bone):
    if bone == None:
        return
    
    bgl.glEnable(bgl.GL_BLEND)
    # object locations

    # green line
    strand = HairStrand(bone)
    
    head = bone.head
    length = (bone.tail - bone.head).length
    rest_direction = strand.get_initial_direction()
    force = strand.get_preservation_force()
    force_direction = mathutils.Vector((0, 0, 0))
    if force.length > 0:
        force_direction = force / force.length * length
    
    x, y = mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 1, 0))
    
    
    #draw_line_3d((1.0, 0.0, 0.0, 0.8), bone.head, rest_direction + bone.head)
    draw_line_3d((1.0, 0.0, 0.0, 0.8), bone.head, force_direction + bone.head)
    
    rest = rest_direction.to_track_quat('Y', 'Z')
    force = force_direction.to_track_quat('Y', 'Z')
    steps = 90
    for i in range(steps):
        a = mathutils.Vector((0, length, 0))
        b = a.copy()
        rot_a = rest.slerp(force, float(i)/steps)
        rot_b = rest.slerp(force, float(i+1)/steps)
        a.rotate(rot_a)
        b.rotate(rot_b)
        draw_line_3d((0.0, 0.5, 0.5, 0.5), a + head, b + head)
    
    
    draw_line_3d((0.0, 1.0, 0.0, 0.8), bone.tail, strand.get_preservation_force() + bone.tail)
    draw_line_3d((0.0, 0.7, 0.6, 0.8), bone.head, strand.get_initial_direction() + bone.head)
    draw_line_3d((0.0, 0.5, 0.8, 0.8), bone.head, strand.get_up_axis() * length + bone.head)
    
    
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def draw_callback_2d(self, bone):

    bgl.glEnable(bgl.GL_BLEND)

    # draw text
    draw_typo_2d((1.0, 1.0, 1.0, 1), "Hello Word ")

    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    
    
class BoneHairOp(bpy.types.Operator):
    """Edit Bone Simulation"""
    bl_idname = "pose.bonehair_op"
    bl_label = "Edit Bone Hair"
    
    action = bpy.props.StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        return get_active_pose_bone(context) != None

    def execute(self, context):
        bone = context.object.pose.bones[context.object.data.bones.active.name]
        strand = None
        action = self.action
        
        if action == '':
            return {'CANCELLED'}
        if action == 'REMOVE':
            bone.bonehair.created = False
            return {'FINISHED'}
        
        try:
            strand = HairStrand(bone)
        except Exception as e:
            self.report({'ERROR_INVALID_INPUT'}, message=str(e))
            return {'CANCELLED'}
        
        if action == 'CREATE':
            strand.initialize()
            bone.bonehair.created = True
            
        if action == 'POSITION':
            strand.set_position()
            return {'FINISHED'}
        if action == 'FORCE':
            strand.set_preservation()
            return {'FINISHED'}
        if action == 'UP_AXIS':
            strand.set_up_axis()
            return {'FINISHED'}
        if action == 'CALC_FORCE':
            try:
                strand.calculate_preservation_force()            
            except Exception as e:
                self.report({'ERROR_INVALID_INPUT'}, message=str(e))
                return {'CANCELLED'}
            return {'FINISHED'}
        # get other bones
        rig = context.object
        bones = [bone for bone in rig.pose.bones if bone.bone.select and bone.bonehair.created]
            
        if action == 'RESET':
            for bone in bones:
                HairStrand(bone).reset_movement()
            return {'FINISHED'}
        if action == 'CLEAR_ANIMATION' or action == 'BAKE':
            if rig.animation_data != None:
                if rig.animation_data.action != None:
                    for bone in bones:
                        for i in range(4):
                            dp = 'pose.bones["' + bone.name + '"].rotation_quaternion'
                            fcurve = rig.animation_data.action.fcurves.find(dp, i)
                            if fcurve != None:
                                rig.animation_data.action.fcurves.remove(fcurve)
                        bone.bonehair.active = True
        if action == 'BAKE':
            frame = context.scene.frame_current
            while (frame <= context.scene.frame_end):
                context.scene.frame_set(frame)
                for bone in bones:
                    strand = HairStrand(bone)
                    strand.display_rotation()
                    strand.bone.keyframe_insert(data_path = 'rotation_quaternion')
                frame += 1
            for bone in bones:
                bone.bonehair.active = False
            return {'FINISHED'}
        
        if action == 'COPY_SETTINGS':
            for bone in bones:
                strand = HairStrand(bone)
                strand.display_rotation()
                strand.bone.keyframe_insert(data_path = 'rotation_quaternion')
                frame += 1
            for bone in bones:
                bone.bonehair.active = False
            return {'FINISHED'}
            
        return {'FINISHED'}


class BoneHairModalOperator(bpy.types.Operator):
    bl_idname = "view3d.bonehair_show"
    bl_label = "Bone Hair Display Operator"

    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if self.bone.bonehair.highlighted == False:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, 'WINDOW')
            self._handle_2d = self._handle_3d = None
            return {'CANCELLED'}
        
        if context.object == self.rig:
            if self._handle_2d == None:
                # re-add handles
                args = (self, self. bone)
                self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, 'WINDOW', 'POST_VIEW')
                self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, 'WINDOW', 'POST_PIXEL')
            return {'PASS_THROUGH'}
        else:
            if self._handle_2d != None:
                # re-add handles
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_2d, 'WINDOW')
                self._handle_2d = self._handle_3d = None
            return {'PASS_THROUGH'}
        
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            bone = get_active_pose_bone(context)
            if bone == None:
                return {'CANCELLED'}
            self.bone = bone
            if self.bone.bonehair.highlighted:
                self.bone.bonehair.highlighted = False
                return {'CANCELLED'}
            
            self.rig = context.object
            self.bone.bonehair.highlighted = True
            
            # the arguments we pass the the callback
            args = (self, bone)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, 'WINDOW', 'POST_VIEW')
            self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class BoneHairPanel(bpy.types.Panel):
    """Panel in the properties N Panel"""
    bl_label = "Bone Hair"
    bl_idname = "pose.bonehair_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    
    def draw(self, context):
        layout = self.layout
        bone = get_active_pose_bone(context)
        
        if bone == None:
            return
        
        row = layout.row()
        col = row.column()
        col.label(bone.name, icon = 'BONE_DATA')
        
        if bone.bonehair.created == False:
            op = row.column().operator('pose.bonehair_op', text="Create")
            op.action = 'CREATE'
            if bone.parent == None:
                row.enabled = False
            return
        else:
            op = row.column().operator('pose.bonehair_op', text="Remove")
            op.action = 'REMOVE'
        
        
        row = layout.row()
        row.column().prop(bone.bonehair, "active")
        text = "Show"
        if bone.bonehair.highlighted:
            text = "Hide"
        op = row.column().operator('view3d.bonehair_show', text=text+" Guides")
        
        row = layout.row()
        op = row.column().operator('pose.bonehair_op', text="Reset")
        op.action = 'RESET'
        op = row.column().operator('pose.bonehair_op', text="Clear Anim")
        op.action = 'CLEAR_ANIMATION'
        op = row.column().operator('pose.bonehair_op', text="Bake")
        op.action = 'BAKE'
        
        box = layout.box()
        row = box.row()
        row.label("Assign Starting Values")
        row = box.row()
        op = row.column().operator('pose.bonehair_op', text="Position")
        op.action = 'POSITION'
        op = row.column().operator('pose.bonehair_op', text="Force")
        op.action = 'FORCE'
        op = row.column().operator('pose.bonehair_op', text="Up Axis")
        op.action = 'UP_AXIS'
        
        
        box = layout.box()
        row = box.row()
        row.column().label("Push Force")
        op = row.column().operator('pose.bonehair_op', text="Calculate")
        op.action = 'CALC_FORCE'
        row = box.row()
        row.prop(bone.bonehair, "preservation_force", text="Strength")
        row = box.row()
        row.prop(bone.bonehair, "preservation_direction", text="Direction")
        
        row = layout.row()
        row.prop(bone.bonehair, "retain_velocity", text='Keep Velocity')
        row = layout.row()
        row.prop(bone.bonehair, "movement_force", text='Root Motion Influence')
        row = layout.row()
        row.prop(bone.bonehair, "simulation_strength", text='Speed')
        row = layout.row()
        row.prop(bone.bonehair, "steps")

        #reference_object['some_property']
    
class BoneHairSettings(bpy.types.PropertyGroup):
    highlighted = bpy.props.BoolProperty(default=False)
    created = bpy.props.BoolProperty(default=False)
    
    theta = bpy.props.FloatProperty()
    phi = bpy.props.FloatProperty()
    initial_rotation = bpy.props.FloatVectorProperty(size=2)
    theta_v = bpy.props.FloatProperty()
    phi_v = bpy.props.FloatProperty()
    up_axis = bpy.props.FloatVectorProperty(size=3, subtype='DIRECTION')
    parent_rest_quat = bpy.props.FloatVectorProperty(size=4, subtype='QUATERNION')
    previous_base_position = bpy.props.FloatVectorProperty(size=3, subtype='DIRECTION')
    previous_base_velocity = bpy.props.FloatVectorProperty(size=3, subtype='DIRECTION')
    
    active = bpy.props.BoolProperty(name='Active', default=True)
    retain_velocity = bpy.props.FloatProperty(name="Velocity", subtype='PERCENTAGE', min=0, max=1, default=0.9)
    preservation_direction = bpy.props.FloatVectorProperty(subtype='ACCELERATION', unit='ACCELERATION')
    preservation_force = bpy.props.FloatProperty(subtype='FACTOR', soft_min=0, soft_max=2)
    movement_force = bpy.props.FloatProperty(name="Movement Force", description="Influence of the base movement on the rotation.", subtype='FACTOR', soft_min=0, soft_max=2, default=1)
    simulation_strength = bpy.props.FloatProperty(name = 'Strength', description='Strength of the sum of forces. Lower strength will slow down the overall movement.', subtype='FACTOR', default=1, min=0.000001, soft_max=1)

    steps = bpy.props.IntProperty(name="Steps", min=0, soft_max = 1000, default=250)

def frame_change(scene):
    if scene.objects.active == None:
        return
    if scene.objects.active.type != 'ARMATURE':
        return
    rig = scene.objects.active
    for bone in rig.pose.bones:
        if bone.bonehair.created and bone.bonehair.active:
            strand = HairStrand(bone)
            try:
                strand.do_step()
                strand.display_rotation()
            except:
                strand.bone.bonehair.active = False



def register():
    bpy.app.handlers.frame_change_pre.append(frame_change)
    bpy.utils.register_class(BoneHairSettings)
    bpy.utils.register_class(BoneHairOp)
    bpy.types.PoseBone.bonehair = bpy.props.PointerProperty(type=BoneHairSettings)
    bpy.utils.register_class(BoneHairPanel)
    bpy.utils.register_class(BoneHairModalOperator)
    
  
def unregister():
    
    bpy.app.handlers.frame_change_pre.remove(frame_change)
    
    bpy.utils.unregister_class(BoneHairSettings)
    bpy.utils.unregister_class(BoneHairOp)
    bpy.utils.unregister_class(BoneHairPanel)
    bpy.utils.unregister_class(BoneHairModalOperator)
    
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
    for ob in bpy.data.objects:
        if ob.type == 'ARMATURE':
            for bone in ob.pose.bones:
                bone.bonehair.highlighted = False
