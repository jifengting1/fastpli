CMAKE_MINIMUM_REQUIRED(VERSION 3.2)
SET(subdir model/solver)

##########################################################################
# Building shared Library for Python
##########################################################################

# building core objects
SET(CoreModules solverCoreModules)
FILE(GLOB solverCoreFiles *.cpp)
IF ( NOT OPENGL_FOUND OR NOT GLUT_FOUND )
   MESSAGE(WARNING "OpenGL or GLUT not found. scene.cpp will not be compiled")
   LIST(REMOVE_ITEM solverCoreFiles ${CMAKE_CURRENT_SOURCE_DIR}/scene.cpp)
ENDIF ( )
ADD_LIBRARY(${CoreModules} OBJECT ${solverCoreFiles})
SET_PROPERTY(TARGET ${CoreModules} PROPERTY POSITION_INDEPENDENT_CODE TRUE)
IF ( OPENGL_FOUND AND GLUT_FOUND )
   TARGET_COMPILE_DEFINITIONS(${CoreModules} PRIVATE _VIS_LIBRARIES)
ENDIF ( )

# building python modules
pybind11_add_module(__solver
      bindings/solver_module.cpp
      $<TARGET_OBJECTS:${CoreModules}>
      $<TARGET_OBJECTS:objectsCoreModules>
      )
IF ( OPENGL_FOUND AND GLUT_FOUND )
   TARGET_LINK_LIBRARIES(__solver PRIVATE ${OPENGL_LIBRARIES} ${GLUT_LIBRARIES})
ENDIF ( )

SET_TARGET_PROPERTIES(__solver PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}/${subdir}")
IF ( OPENGL_FOUND AND GLUT_FOUND )
   TARGET_COMPILE_DEFINITIONS(__solver PRIVATE _VIS_LIBRARIES)
ENDIF ()

add_dependencies(__solver build_version)