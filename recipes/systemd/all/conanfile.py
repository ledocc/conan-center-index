from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.50.0"


class SystemdConan(ConanFile):
    name = "systemd"
    version = "system"
    description = "systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    topics = ("system")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://systemd.io/"
    license = "LGPL-2.1"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os not in ["Linux"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux.")

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["systemd-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["systemd-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libsystemd-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["systemd-libs"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["systemd"], update=True, check=True)

    def package_info(self):
        if self.settings.os in ["Linux"]:
            name = 'libsystemd'
            pkg_config = PkgConfig(self, name)
            pkg_config.fill_cpp_info(self.cpp_info.components[name])
