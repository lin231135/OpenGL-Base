# gl.py

import glm  # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from camera import Camera
from skybox import Skybox

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        glViewport(0, 0, self.width, self.height)
        glClearColor(0.08, 0.1, 0.12, 1.0)
        glEnable(GL_DEPTH_TEST)

        # --- VAO global por compatibilidad con drivers AMD (core profile) ---
        self.globalVAO = glGenVertexArrays(1)
        glBindVertexArray(self.globalVAO)

        # Arranca en FILL y SIN culling para evitar desaparecer el modelo por winding
        self._filled = True
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)

        # Matrices / escena
        self.camera = Camera(self.width, self.height)
        self.scene = []

        self.activeShader = None
        self.skybox = None

        # Luces / uniformes
        self.pointLight = glm.vec3(0, 0, 0)
        self.ambientLight = 0.14
        self.value = 0.0
        self.elapsedTime = 0.0

    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera

    def ToggleFilledMode(self):
        self._filled = not self._filled
        if self._filled:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glDisable(GL_CULL_FACE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glEnable(GL_CULL_FACE)
            glFrontFace(GL_CCW)
            glCullFace(GL_BACK)

    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram(
                compileShader(vertexShader, GL_VERTEX_SHADER),
                compileShader(fragmentShader, GL_FRAGMENT_SHADER)
            )
        else:
            self.activeShader = None

    def Render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(self.globalVAO)

        self.camera.Update()

        if self.skybox is not None:
            self.skybox.Render()
            glBindVertexArray(self.globalVAO)

        if self.activeShader is not None:
            glUseProgram(self.activeShader)

            glUniformMatrix4fv(
                glGetUniformLocation(self.activeShader, "viewMatrix"),
                1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix)
            )

            glUniformMatrix4fv(
                glGetUniformLocation(self.activeShader, "projectionMatrix"),
                1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix)
            )

            glUniform3fv(
                glGetUniformLocation(self.activeShader, "pointLight"),
                1, glm.value_ptr(self.pointLight)
            )
            glUniform1f(
                glGetUniformLocation(self.activeShader, "ambientLight"),
                self.ambientLight
            )

            glUniform1f(glGetUniformLocation(self.activeShader, "value"), self.value)
            glUniform1f(glGetUniformLocation(self.activeShader, "time"), self.elapsedTime)

            glUniform1i(glGetUniformLocation(self.activeShader, "tex0"), 0)
            glUniform1i(glGetUniformLocation(self.activeShader, "tex1"), 1)

        for obj in self.scene:
            if self.activeShader is not None:
                glUniformMatrix4fv(
                    glGetUniformLocation(self.activeShader, "modelMatrix"),
                    1, GL_FALSE, glm.value_ptr(obj.GetModelMatrix())
                )
            obj.Render()
