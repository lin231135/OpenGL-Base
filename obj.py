#obj.py
import os

class Obj(object):
    def __init__(self, filename):
        with open(filename, "r") as file:
            lines = file.read().splitlines()

        self.vertices = []
        self.texCoords = []
        self.normals = []
        self.faces = []  # [(face, materialName), ...]
        self.materials = {}  # materialName -> texturePath

        currentMaterial = None
        basePath = os.path.dirname(filename)

        for line in lines:
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue

            prefix, *value = line.split()
            if prefix == "v":
                self.vertices.append(list(map(float, value)))
            elif prefix == "vt":
                self.texCoords.append(list(map(float, value[:2])))
            elif prefix == "vn":
                self.normals.append(list(map(float, value)))
            elif prefix == "usemtl":
                currentMaterial = value[0]
            elif prefix == "f":
                face = []
                for vert in value:
                    vert = list(map(int, vert.split("/")))
                    face.append(vert)
                self.faces.append((face, currentMaterial))
            elif prefix == "mtllib":
                mtlPath = os.path.join(basePath, value[0])
                self.loadMTL(mtlPath, basePath)

    def loadMTL(self, filename, basePath):
        currentMat = None
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                prefix, *value = line.split()
                if prefix == "newmtl":
                    currentMat = value[0]
                elif prefix == "map_Kd" and currentMat:
                    texPath = os.path.join(basePath, value[0])
                    self.materials[currentMat] = texPath
