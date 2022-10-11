cmake_minimum_required(VERSION 3.5)
project(ros_report)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
# find_package(cti_rblite_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)


# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
 
  #set(ament_cmake_copyright_FOUND TRUE)

  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

include_directories(
  include
)

add_executable(${PROJECT_NAME}  src/report.cpp)
ament_target_dependencies(${PROJECT_NAME} rclcpp std_msgs sensor_msgs  geometry_msgs)   # cti_rblite_msgs
target_link_libraries(${PROJECT_NAME} -lmysqlclient -lpython3.10 jsoncpp)

install(TARGETS ${PROJECT_NAME}
    DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
)

ament_package()
