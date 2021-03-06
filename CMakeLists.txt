CMAKE_MINIMUM_REQUIRED(VERSION 3.0.0)
PROJECT(prand LANGUAGES CXX)

# Settings
# --------
SET(CMAKE_VERBOSE_MAKEFILE ON)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_STANDARD 17)
SET(CMAKE_CXX_EXTENSIONS OFF)
SET(CMAKE_CUDA_STANDARD 14)
SET(CMAKE_CUDA_STANDARD_REQUIRED ON)
SET(CMAKE_POSITION_INDEPENDENT_CODE ON)
SET(CMAKE_FIND_LIBRARY_SUFFIXES ".so")
OPTION(JPEG_AS_NUMPY "GetFrame returns jpeg as a numpy ndarray" OFF)
OPTION(CUDA_USE_STATIC_CUDA_RUNTIME FALSE)
IF(CMAKE_BUILD_TYPE STREQUAL "")
	SET(CMAKE_BUILD_TYPE "Release")
ENDIF()

# Dependencies
# ------------
FIND_PACKAGE(CUDA REQUIRED)
FIND_PACKAGE(OpenMP REQUIRED)
FIND_PACKAGE(OpenCV REQUIRED core highgui cudaimgproc)
EXECUTE_PROCESS(COMMAND python3 -c "import site; print(site.getusersitepackages(), end='')"
				OUTPUT_VARIABLE Python3_USER_SITE_DIR)
EXECUTE_PROCESS(COMMAND python3 -c "import numpy; print(numpy.get_include(), end='')"
				OUTPUT_VARIABLE Python3_NumPy_INCLUDE_DIRS)
FIND_PACKAGE(PythonLibs; 3 REQUIRED)

# Compiler Options
#-----------------
SET(COMPILE_DEFINITIONS "-DCUDA_VERSION_MINOR=${CUDA_VERSION_MINOR}")
IF(JPEG_AS_NUMPY)
	LIST(APPEND COMPILE_DEFINITIONS -DJPEG_AS_NUMPY)
ENDIF()
STRING(TOUPPER ${CMAKE_BUILD_TYPE} CMAKE_BUILD_TYPE)
IF(CMAKE_BUILD_TYPE STREQUAL "DEBUG")
	LIST(APPEND COMPILE_DEFINITIONS -DNDEBUG)
ENDIF()

# Build CUDA kernels
# ------------------
FILE(GLOB_RECURSE CVTCOLOR_SRC "${CMAKE_CURRENT_SOURCE_DIR}/src/NvDecoder/*.cu")
LIST(APPEND CUDA_NVCC_FLAGS " -Xcompiler -fPIC -Xcompiler -std=c++11")
CUDA_ADD_LIBRARY(cvtcolor STATIC ${CVTCOLOR_SRC})
TARGET_INCLUDE_DIRECTORIES(cvtcolor PRIVATE ${CUDA_INCLUDE_DIRS})
TARGET_COMPILE_DEFINITIONS(cvtcolor PRIVATE ${COMPILE_DEFINITIONS})
SET_TARGET_PROPERTIES(cvtcolor PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Build Main Library
# ------------------
FILE(GLOB_RECURSE LIB_SRC_FILES "${CMAKE_SOURCE_DIR}/src/*.cpp")
ADD_LIBRARY(${PROJECT_NAME} SHARED ${LIB_SRC_FILES})
TARGET_COMPILE_DEFINITIONS(${PROJECT_NAME} PRIVATE ${COMPILE_DEFINITIONS})
TARGET_COMPILE_OPTIONS(${PROJECT_NAME} PRIVATE ${OpenMP_CXX_FLAGS})
SET_TARGET_PROPERTIES(${PROJECT_NAME} PROPERTIES PREFIX "")
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME}
	PRIVATE ${CUDA_INCLUDE_DIRS}
	PRIVATE ${OpenCV_INCLUDE_DIRS}
	PRIVATE ${PYTHON_INCLUDE_DIRS}
	PRIVATE ${Python3_NumPy_INCLUDE_DIRS}
	)
TARGET_LINK_OPTIONS(${PROJECT_NAME}
	PRIVATE ${OpenMP_EXE_LINKER_FLAGS}
	PRIVATE ${OpenMP_CXX_FLAGS}
)
TARGET_LINK_LIBRARIES(${PROJECT_NAME}
	PRIVATE cvtcolor
	PRIVATE ${OpenCV_LIBRARIES}
	PRIVATE ${CUDA_LIBRARIES}
	PRIVATE ${PYTHON_LIBRARIES}
	PRIVATE nvcuvid
	PRIVATE cuda
	PRIVATE nvjpeg
	PRIVATE avformat
	PRIVATE avcodec
	PRIVATE avutil
	PRIVATE glog
	PRIVATE gflags
	)
ADD_DEPENDENCIES(${PROJECT_NAME} cvtcolor)

# Build Test
# ----------
ADD_EXECUTABLE(${PROJECT_NAME}_test test/test.cpp)
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME}_test
	PRIVATE ${OpenCV_INCLUDE_DIRS}
	)
TARGET_LINK_LIBRARIES(${PROJECT_NAME}_test
	PRIVATE ${PROJECT_NAME}
	PRIVATE ${OpenCV_LIBRARIES}
	PRIVATE glog
	PRIVATE gflags
	)
ADD_DEPENDENCIES(${PROJECT_NAME}_test ${PROJECT_NAME})

# Installation
# ------------
INSTALL(FILES "${CMAKE_SOURCE_DIR}/python/__init__.py"
	$<TARGET_FILE:${PROJECT_NAME}>
	DESTINATION ${Python3_USER_SITE_DIR}/${PROJECT_NAME})
INSTALL(FILES "${CMAKE_SOURCE_DIR}/include/prand.hpp"
	$<TARGET_FILE:${PROJECT_NAME}>
	DESTINATION ${Python3_USER_SITE_DIR}/${PROJECT_NAME})