#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "OGDF" for configuration "Release"
set_property(TARGET OGDF APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(OGDF PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/x86_64-linux-gnu/libOGDF.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS OGDF )
list(APPEND _IMPORT_CHECK_FILES_FOR_OGDF "${_IMPORT_PREFIX}/lib/x86_64-linux-gnu/libOGDF.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
