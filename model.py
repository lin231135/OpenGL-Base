#model.py
from OpenGL.GL import *
from obj import Obj
from buffer import Buffer
import glm
import pygame
import os

class SubMesh:
    def __init__(self, positions, texCoords, normals, texturePath=None):
        self.positions = Buffer(positions)
        self.texCoords = Buffer(texCoords)
        self.normals = Buffer(normals)
        self.vertexCount = int(len(positions) / 3)
        self.texture = None
        if texturePath:
            self.loadTexture(texturePath)

    def loadTexture(self, filename):
        textureSurface = pygame.image.load(filename)
        if textureSurface.get_bytesize() == 4:
            textureData = pygame.image.tostring(textureSurface, "RGBA", True)
            texFormat = GL_RGBA
        else:
            textureData = pygame.image.tostring(textureSurface, "RGB", True)
            texFormat = GL_RGB

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, texFormat,
                     textureSurface.get_width(),
                     textureSurface.get_height(),
                     0, texFormat, GL_UNSIGNED_BYTE, textureData)
        glGenerateMipmap(GL_TEXTURE_2D)

    def render(self):
        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)

        self.positions.Use(0, 3)
        self.texCoords.Use(1, 2)
        self.normals.Use(2, 3)
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)


class Model:
    def __init__(self, filename):
        self.objFile = Obj(filename)
        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        self.scale = glm.vec3(1, 1, 1)
        self.submeshes = []
        self.loadSubMeshes(filename)

    def loadSubMeshes(self, filename):
        basePath = os.path.dirname(filename)
        currentMaterial = None
        materialMap = self.objFile.materials  # new dictionary from Obj
        positions, texCoords, normals = [], [], []

        for face, matName in self.objFile.faces:
            if matName != currentMaterial and len(positions) > 0:
                texPath = materialMap.get(currentMaterial)
                submesh = SubMesh(positions, texCoords, normals, texPath)
                self.submeshes.append(submesh)
                positions, texCoords, normals = [], [], []
            currentMaterial = matName

            for i in range(len(face)):
                v = self.objFile.vertices[face[i][0] - 1]
                t = self.objFile.texCoords[face[i][1] - 1]
                n = self.objFile.normals[face[i][2] - 1]
                positions += v
                texCoords += t
                normals += n

        if len(positions) > 0:
            texPath = materialMap.get(currentMaterial)
            submesh = SubMesh(positions, texCoords, normals, texPath)
            self.submeshes.append(submesh)

    def GetModelMatrix(self):
        identity = glm.mat4(1)
        translateMat = glm.translate(identity, self.position)
        pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        yawMat = glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        rollMat = glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        rotationMat = pitchMat * yawMat * rollMat
        scaleMat = glm.scale(identity, self.scale)
        return translateMat * rotationMat * scaleMat

    def Render(self):
        for submesh in self.submeshes:
            submesh.render()
