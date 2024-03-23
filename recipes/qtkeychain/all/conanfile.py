from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.gnu import PkgConfigDeps
import os


required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


class PackageConan(ConanFile):
    name = "qtkeychain"
    description = "QtKeychain is a Qt API to store passwords and other secret data securely"
    license = "BSD-3-Clause-Modification"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/frankosterfeld/qtkeychain"
    topics = ("password", "security")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_with_qt6": [True, False],
        "build_translation": [True, False],
        "translation_as_resource": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_with_qt6": False,
        "build_translation": True,
        "translation_as_resource": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
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
        if self.settings.os == "Linux":
            self.options["qt"].with_dbus=True
        if self.options.build_translation:
            self.options["qt"].qttranslations=True
        self.options["qt"].qttranslations=True
        if self.options.build_with_qt6:
            self.options["qt"].qt5compat=True
        
            
    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        if self.options.build_with_qt6:
            self.requires("qt/6.4.2")
        else:
            self.requires("qt/5.15.9")
        self.requires("libsecret/0.20.5")

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

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_WITH_QT6"] = self.options.build_with_qt6
        tc.variables["BUILD_TRANSLATIONS"] = self.options.build_translation
        tc.variables["TRANSLATIONS_AS_RESOURCE"] = self.options.translation_as_resource
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        pc = PkgConfigDeps(self)
        pc.generate()
        
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
        rmdir(self, os.path.join(self.package_folder, "mkspecs"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        qt_version_major = "6" if self.options.build_with_qt6 else "5"
        self.cpp_info.libs = ["qt"+qt_version_major+"keychain"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "qt"+qt_version_major+"keychain")]

        self.cpp_info.set_property("cmake_file_name", "QtKeychain")
        self.cpp_info.set_property("cmake_target_name", "QtKeychain::QtKeychain")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "QTKEYCHAIN"
        self.cpp_info.filenames["cmake_find_package_multi"] = "qtkeychain"
        self.cpp_info.names["cmake_find_package"] = "QTKEYCHAIN"
        self.cpp_info.names["cmake_find_package_multi"] = "qtkeychain"
