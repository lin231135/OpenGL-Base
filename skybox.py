# skybox.py
from numpy import array, float32
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame

# Bajamos a 330 core para compatibilidad amplia (incluyendo algunos drivers AMD).
skybox_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec3 texCoords;

void main()
{
    texCoords = inPosition;
    // Quitamos la traslación de la vista para que el cubo siga a la cámara
    mat4 vm = mat4(mat3(viewMatrix));
    gl_Position = projectionMatrix * vm * vec4(inPosition, 1.0);
}
'''

skybox_fragment_shader = '''
#version 330 core

uniform samplerCube skybox;

in vec3 texCoords;

out vec4 fragColor;

void main()
{
    fragColor = texture(skybox, texCoords);
}
'''

class Skybox(object):
    def __init__(self, textureList):
        self.cameraRef = None

        skyboxVertices = [
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,

             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,

            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0
        ]

        self.vertexBuffer = array(skyboxVertices, dtype=float32)
        self.VBO = glGenBuffers(1)

        # --- FIX AMD/CORE PROFILE: crear y configurar un VAO propio del skybox ---
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertexBuffer.nbytes, self.vertexBuffer, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4 * 3, ctypes.c_void_p(0))

        glBindVertexArray(0)  # Desenlazar VAO para evitar side-effects

        self.shaders = compileProgram(
            compileShader(skybox_vertex_shader, GL_VERTEX_SHADER),
            compileShader(skybox_fragment_shader, GL_FRAGMENT_SHADER)
        )

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        for i in range(len(textureList)):
            texture = pygame.image.load(textureList[i])
            # pygame entrega superficies BGR-> usamos RGB y sin volteo
            textureData = pygame.image.tostring(texture, "RGB", False)

            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                         0,
                         GL_RGB,
                         texture.get_width(),
                         texture.get_height(),
                         0,
                         GL_RGB,
                         GL_UNSIGNED_BYTE,
                         textureData)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def Render(self):
        if self.shaders is None:
            return

        glUseProgram(self.shaders)

        if self.cameraRef is not None:
            glUniformMatrix4fv(
                glGetUniformLocation(self.shaders, "viewMatrix"),
                1, GL_FALSE, glm.value_ptr(self.cameraRef.viewMatrix)
            )
            glUniformMatrix4fv(
                glGetUniformLocation(self.shaders, "projectionMatrix"),
                1, GL_FALSE, glm.value_ptr(self.cameraRef.projectionMatrix)
            )

        glDepthMask(GL_FALSE)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        # Enlazamos el VAO ya configurado y dibujamos
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)

        glDepthMask(GL_TRUE)