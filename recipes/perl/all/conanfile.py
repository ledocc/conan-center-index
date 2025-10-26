from conan import ConanFile, conan_version
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0.0"


class XorgConan(ConanFile):
    name = "perl"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://www.perl.org/"
    description = "Perl is a highly capable, feature-rich programming language with over 37 years of development."
    settings = "os", "arch", "compiler", "build_type"
    topics = ("perl")
    options = {}
    default_options = {}


    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        yum = package_manager.Yum(self)
        yum.install_substitutes([
            "perl",
            "perl-open",
            "perl-Digest-SHA",
            "perl-File-Basename",
            "perl-File-Compare",
            "perl-Getopt-Std",
            "perl-FindBin",
            "perl-IPC-Cmd",
            "perl-PathTools",
            "perl-Scalar-List-Utils"
        ],
        [
            "perl",
            "perl-Digest-SHA",
            "perl-IPC-Cmd",
            "perl-PathTools",
            "perl-Scalar-List-Utils"
        ],
        [
            "perl",
            "perl-Digest-SHA",
            "perl-IPC-Cmd"
        ]
        , update=True, check=True)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

