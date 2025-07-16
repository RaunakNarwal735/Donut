from vpython import canvas, vector, color, box, arrow, label, button, radians, pi, rate

# Create the scene
scene = canvas(title='3D Cube: Rotate and Reflect', width=800, height=600, center=vector(0,0,0), background=color.white)

# Create the cube
cube = box(pos=vector(0,0,0), size=vector(2,2,2), color=color.cyan, opacity=0.7)

# Axes for reference
def draw_axes():
    arrow(pos=vector(0,0,0), axis=vector(3,0,0), color=color.red)
    label(pos=vector(3.2,0,0), text='x', color=color.red, box=False)
    arrow(pos=vector(0,0,0), axis=vector(0,3,0), color=color.green)
    label(pos=vector(0,3.2,0), text='y', color=color.green, box=False)
    arrow(pos=vector(0,0,0), axis=vector(0,0,3), color=color.blue)
    label(pos=vector(0,0,3.2), text='z', color=color.blue, box=False)

draw_axes()

# Rotation and reflection functions
def rotate_cube(axis):
    angle = radians(15)
    cube.rotate(angle=angle, axis=axis, origin=vector(0,0,0))

def reflect_cube(axis):
    # Reflection: invert the corresponding axis
    s = cube.size
    if axis.x:
        cube.size = vector(-s.x, s.y, s.z)
    elif axis.y:
        cube.size = vector(s.x, -s.y, s.z)
    elif axis.z:
        cube.size = vector(s.x, s.y, -s.z)
    # To visually reflect, rotate 180 around the axis perpendicular to the reflection
    cube.rotate(angle=pi, axis=axis, origin=vector(0,0,0))

# UI Buttons
def rotate_x(): rotate_cube(vector(1,0,0))
def rotate_y(): rotate_cube(vector(0,1,0))
def rotate_z(): rotate_cube(vector(0,0,1))
def reflect_x(): reflect_cube(vector(1,0,0))
def reflect_y(): reflect_cube(vector(0,1,0))
def reflect_z(): reflect_cube(vector(0,0,1))

scene.append_to_caption('\n')
button(text='Rotate X', bind=lambda _: rotate_x())
button(text='Rotate Y', bind=lambda _: rotate_y())
button(text='Rotate Z', bind=lambda _: rotate_z())
scene.append_to_caption('    ')
button(text='Reflect X', bind=lambda _: reflect_x())
button(text='Reflect Y', bind=lambda _: reflect_y())
button(text='Reflect Z', bind=lambda _: reflect_z())
scene.append_to_caption('\n\nUse the mouse to drag and zoom the view.\n')

# Keep the window open
while True:
    rate(60) 