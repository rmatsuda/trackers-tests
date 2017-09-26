import vtk
import random

def arrow(startPoint, endPoint):

    # Compute a basis
    normalizedX = [0 for i in range(3)]
    normalizedY = [0 for i in range(3)]
    normalizedZ = [0 for i in range(3)]

    # The X axis is a vector from start to end
    math = vtk.vtkMath()
    math.Subtract(endPoint, startPoint, normalizedX)
    length = math.Norm(normalizedX)
    math.Normalize(normalizedX)

    # The Z axis is an arbitrary vector cross X
    arbitrary = [0 for i in range(3)]
    arbitrary[0] = random.uniform(-10, 10)
    arbitrary[1] = random.uniform(-10, 10)
    arbitrary[2] = random.uniform(-10, 10)
    math.Cross(normalizedX, arbitrary, normalizedZ)
    math.Normalize(normalizedZ)

    # The Y axis is Z cross X
    math.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()

    # Create the direction cosine matrix
    matrix.Identity()
    for i in range(3):
        matrix.SetElement(i, 0, normalizedX[i])
        matrix.SetElement(i, 1, normalizedY[i])
        matrix.SetElement(i, 2, normalizedZ[i])

    # Apply the transforms arrow 1
    transform_1 = vtk.vtkTransform()
    transform_1.Translate(startPoint)
    transform_1.Concatenate(matrix)
    transform_1.Scale(length, length, length)
    # source
    arrowSource1 = vtk.vtkArrowSource()
    arrowSource1.SetTipResolution(50)
    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(arrowSource1.GetOutputPort())
    # Transform the polydata
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform_1)
    transformPD.SetInputConnection(arrowSource1.GetOutputPort())
    # mapper transform
    mapper.SetInputConnection(transformPD.GetOutputPort())
    # actor
    actor_arrow = vtk.vtkActor()
    actor_arrow.SetMapper(mapper)
    actor_arrow.GetProperty().SetColor(0, 0, 1)

    return actor_arrow

def sphere(center, radius, colour):

    sphere_sr = vtk.vtkSphereSource()
    sphere_sr.SetCenter(center)
    sphere_sr.SetRadius(radius)
    sphereStartMapper = vtk.vtkPolyDataMapper()
    sphereStartMapper.SetInputConnection(sphere_sr.GetOutputPort())
    sphere_ac = vtk.vtkActor()
    sphere_ac.SetMapper(sphereStartMapper)
    sphere_ac.GetProperty().SetColor(colour)

    return sphere_ac