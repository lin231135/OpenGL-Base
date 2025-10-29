# RendererOpenGL2025.py

import importlib
import vertexShaders

import pygame
import pygame.display
from pygame.locals import *
import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import *
from fragmentShaders import *

# ---------------- Inicialización Pygame + OpenGL ----------------
# En algunas GPUs (especialmente APU AMD) es CRÍTICO setear atributos ANTES del set_mode
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

# ---------------- Configuración de ventana ----------------
width = 960
height = 540
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

# ---------------- Renderer principal ----------------
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)

currVertexShader = vertex_shader
currFragmentShader = fragment_shader
rend.SetShaders(currVertexShader, currFragmentShader)

# ---------------- Skybox (opcional; puedes comentarlo si quieres aislar el problema) ----------------
skyboxTextures = [
    "skybox/right.jpg",
    "skybox/left.jpg",
    "skybox/top.jpg",
    "skybox/bottom.jpg",
    "skybox/front.jpg",
    "skybox/back.jpg"
]
rend.CreateSkybox(skyboxTextures)

# ---------------- Modelo ----------------
# Asegúrate que models/pacman.obj tenga:  mtllib pacman.mtl
# y que pacman.mtl tenga map_Kd apuntando a tus texturas
pacmanModel = Model("models/tomato.obj")
pacmanModel.position = glm.vec3(0.0, -1.5, -4.0)
pacmanModel.scale    = glm.vec3(0.25, 0.25, 0.25)
# Si sospechas orientación rara:
# pacmanModel.rotation.y = 90

rend.scene.append(pacmanModel)

# ---------------- Loop principal ----------------
isRunning = True
while isRunning:

    deltaTime = clock.tick(60) / 1000.0
    rend.elapsedTime += deltaTime

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()  # alterna fill/wireframe + culling

            # Cambiar fragment shaders
            if event.key == pygame.K_1:
                currFragmentShader = fragment_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_2:
                currFragmentShader = toon_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_3:
                currFragmentShader = negative_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_4:
                currFragmentShader = magma_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            # Cambiar vertex shaders
            if event.key == pygame.K_7:
                currVertexShader = vertex_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_8:
                currVertexShader = fat_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_9:
                currVertexShader = melt_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_0:
                importlib.reload(vertexShaders)
                currVertexShader = vertexShaders.earth_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Shader Tierra recargado y activado")

    # ---------------- Movimiento cámara ----------------
    if keys[K_UP]:
        rend.camera.position.z += 2.0 * deltaTime
    if keys[K_DOWN]:
        rend.camera.position.z -= 2.0 * deltaTime
    if keys[K_RIGHT]:
        rend.camera.position.x += 2.0 * deltaTime
    if keys[K_LEFT]:
        rend.camera.position.x -= 2.0 * deltaTime

    # ---------------- Movimiento luz ----------------
    if keys[K_w]:
        rend.pointLight.z -= 10 * deltaTime
    if keys[K_s]:
        rend.pointLight.z += 10 * deltaTime
    if keys[K_a]:
        rend.pointLight.x -= 10 * deltaTime
    if keys[K_d]:
        rend.pointLight.x += 10 * deltaTime
    if keys[K_q]:
        rend.pointLight.y -= 10 * deltaTime
    if keys[K_e]:
        rend.pointLight.y += 10 * deltaTime

    # ---------------- Uniformes útiles ----------------
    if keys[K_z]:
        rend.value = max(0.0, rend.value - 1.0 * deltaTime)
    if keys[K_x]:
        rend.value = min(1.0, rend.value + 1.0 * deltaTime)

    # ---------------- Animación simple ----------------
    pacmanModel.rotation.y += 45.0 * deltaTime

    # ---------------- Render ----------------
    rend.Render()
    pygame.display.flip()

pygame.quit()
