

# add static library MathFunctions with source code mysqrt.cxx
add_library(MathFunctions SHARED mysqrt.cxx)
set_target_properties(MathFunctions PROPERTIES VERSION 1.2)

install(TARGETS MathFunctions DESTINATION bin)
install(FILES mysqrt.h DESTINATION include)
