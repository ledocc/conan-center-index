from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
import os


required_conan_version = ">=1.53.0"


class QGISConan(ConanFile):
    name = "qgis"
    description = "short description"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qgis.org"
    topics = ("GIS", "Qt")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_with_qt6": [True, False],
        "with_qtquick": [True, False],
        "with_qtserialport": [True, False],
        "with_bindings": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_with_qt6": False,
        "with_qtquick": False,
        "with_qtserialport": False,
        "with_bindings": False
    }

    short_paths=True
    
    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("draco/1.5.6")
        self.requires("exiv2/0.27.5")
        self.requires("expat/2.5.0")
        self.requires("geos/3.11.2")
        self.requires("gdal/3.5.3")
        self.requires("gsl/2.7")
        self.requires("hdf5/1.14.0")
        self.requires("libpq/14.7")
        self.requires("libspatialindex/1.9.3")
#        self.requires("libspatialite/5.0.1")
        self.requires("libzip/1.9.2")
        self.requires("netcdf/4.8.1")
        self.requires("opencl-clhpp-headers/2023.04.17")
        self.requires("opencl-icd-loader/2023.04.17")
        self.requires("pdal/2.3.0")
        self.requires("proj/9.1.1")
        self.requires("protobuf/3.21.9")
        self.options["protobuf"].lite=True

        if self.options.build_with_qt6:
            self.requires("qt/6.4.2")
        else:
            self.requires("qt/5.15.9")
        self.options["qt"].gui=True
        self.options["qt"].widgets=True
        self.options["qt"].qt3d=True
        self.options["qt"].qtdeclarative=True
        self.options["qt"].qtmultimedia=True
        if self.options.with_qtserialport:
            self.options["qt"].qtserialport=True
        self.options["qt"].qttools=True
        self.options["qt"].qtsvg=True
        self.options["qt"].with_dbus=True
        if self.options.with_qtquick:
            self.options["qt"].qtquick=True
        self.requires("qca/2.3.6")
        self.options["qca"].build_with_qt6=self.options.build_with_qt6
        self.requires("qscintilla/2.14.1")
        self.options["qscintilla"].build_with_qt6=self.options.build_with_qt6
        self.requires("qtkeychain/0.14.1")
        self.options["qtkeychain"].build_with_qt6=self.options.build_with_qt6
        self.requires("qwt/6.2.0")
        self.requires("sqlite3/3.42.0")
        self.requires("zlib/1.2.13")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("bison/[>=2.4]")
        self.tool_requires("flex/[>=2.5.6]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_WITH_QT6"] = self.options.build_with_qt6
        tc.variables["WITH_DESKTOP"] = False
        tc.variables["WITH_QUICK"] = self.options.with_qtquick
        tc.variables["WITH_QTWEBKIT"] = False
        tc.variables["WITH_BINDINGS"] = self.options.with_bindings
        tc.variables["WITH_QTSERIALPORT"] = self.options.with_qtserialport
        tc.variables["WITH_SPATIALITE"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

        tc = VirtualRunEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "man"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):

#        self.cpp_info.set_property("cmake_file_name", "qgis")
#        self.cpp_info.set_property("pkg_config_name", "qgis")

#        self.cpp_info.names["cmake_find_package"] = "qgis"
#        self.cpp_info.names["cmake_find_package_multi"] = "qgis"

        def _create_module(component_name, requires=[]):
            namespace = "qgis"
            assert component_name not in self.cpp_info.components, f"Module {component_name} already present in self.cpp_info.components"
            
            self.cpp_info.components[component_name].set_property("cmake_target_name", f"{namespace}::{component_name}")
            self.cpp_info.components[component_name].names["cmake_find_package"] = component_name
            self.cpp_info.components[component_name].names["cmake_find_package_multi"] = component_name

            libname = f"{namespace}_{component_name}"
            self.cpp_info.components[component_name].libs = [libname]
            self.cpp_info.components[component_name].requires = requires

            
        _create_module( "core",[
            "exiv2::exiv2",
            "expat::expat",
            "geos::geos",
            "gdal::gdal",
            "libspatialindex::libspatialindex",
            "libzip::libzip",
            "opencl-icd-loader::opencl-icd-loader",
            "proj::proj",
            "protobuf::protobuf",
            "qt::qtConcurrent",
            "qt::qtCore",
            "qt::qtGui",
            "qt::qtNetwork",
            "qt::qtSql",
            "qt::qtSvg",
            "qt::qtXml",
            "qt::qtWidgets",
            "qtkeychain::qtkeychain",
            "sqlite3::sqlite3",
            "zlib::zlib"
        ] )
            
        _create_module( "analysis", [
            "core",
            "gsl::gsl",
            "opencl-icd-loader::opencl-icd-loader",
        ] )
        _create_module( "gui", [
            "analysis",
            "core",
            "qscintilla::qscintilla",
            "qt::qtMultimedia",
            "qt::qtMultimediaWidgets",
            "qt::qtQuickWidgets",
            "qt::qtUiTools",
            "qwt::qwt",
        ] )
        _create_module( "native", [
            "qt::qtCore",
            "qt::qtDBus",
            "qt::qtGui"
        ] )

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
