cmake_minimum_required(VERSION 2.6)
project(Tutorial)

# The version number
set (Tutorial_VERSION_MAJOR 1)
set (Tutorial_VERSION_MINOR 0)

# does this system provide the log and exp functions?
include(${CMAKE_ROOT}/Modules/CheckFunctionExists.cmake)
check_function_exists(log HAVE_LOG)
check_function_exists(exp HAVE_EXP)

# configure a header file to pass some of the CMake settings
# to the source code
configure_file(
    "${PROJECT_SOURCE_DIR}/TutorialConfig.h.in"
    "${PROJECT_BINARY_DIR}/TutorialConfig.h"
)

# add the binary tree to the search path for include files
# so that we will find the TutorialConfig.h
include_directories("${PROJECT_BINARY_DIR}")

# should we use our own math functions
option(USE_MYMATH "USE tutorial provided math implementation" ON)

if(USE_MYMATH)
    # add the mysqrt.h
    include_directories("${PROJECT_SOURCE_DIR}/MathFunctions")
    # the source code mysqrt.cxx
    add_subdirectory(MathFunctions)
    set (EXTRA_LIBS ${EXTRA_LIBS} MathFunctions)
endif(USE_MYMATH)

# add the add_executable
add_executable(Tutorial tutorial.cxx)
target_link_libraries(Tutorial ${EXTRA_LIBS})


install(TARGETS Tutorial DESTINATION bin)
install(FILES "${PROJECT_BINARY_DIR}/TutorialConfig.h"
 DESTINATION include)

 enable_testing()

#define a macro to simplify adding tests, then use it
macro(do_test arg result)
    add_test(TutorialComp${arg} Tutorial ${arg})
    set_tests_properties(TutorialComp${arg} PROPERTIES 
    PASS_REGULAR_EXPRESSION ${result})
endmacro(do_test)


do_test(25 "25 is 5")
do_test(0.01 "0.01 is 0.1")

# 构建一个 CPack 安装包
include (InstallRequiredSystemLibraries)
set (CPACK_RESOURCE_FILE_LICENSE
  "${CMAKE_CURRENT_SOURCE_DIR}/License.txt")
set (CPACK_PACKAGE_VERSION_MAJOR "${Tutorial_VERSION_MAJOR}")
set (CPACK_PACKAGE_VERSION_MINOR "${Tutorial_VERSION_MINOR}")
include (CPack)