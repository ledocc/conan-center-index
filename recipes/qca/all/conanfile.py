from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"



class QcaConan(ConanFile):
    name = "qca"
    description = "Qt Cryptographic Architecture — straightforward cross-platform crypto API"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://invent.kde.org/libraries/qca"
    topics = ("Qt", "Cryptography")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_plugins": ["none", "all", "auto"],
        "build_with_qt6": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_plugins": "auto",
        "build_with_qt6": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.build_with_qt6:
            self.options["qt"].qt5compat = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.build_with_qt6:
            self.requires("qt/6.4.2@")
        else:
            self.requires("qt/5.15.9@")

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
        if ( not self.options.shared ) and ( self.options.build_plugins in [ "all", "auto" ] ):
            raise ConanInvalidConfiguration(
                f"{self.ref} fail to build static library with plugin."
            )

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QCA_SUFFIX"] = False
        tc.variables["BUILD_PLUGINS"] = self.options.build_plugins
        tc.variables["BUILD_WITH_QT6"] = self.options.build_with_qt6
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        vbe = VirtualBuildEnv(self)
        vbe.generate()

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
        rmdir(self, os.path.join(self.package_folder, "mkspecs"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["qca"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "QtCrypto")]

        self.cpp_info.set_property("cmake_file_name", "Qca")
        self.cpp_info.set_property("cmake_target_name", "Qca::Qca")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
