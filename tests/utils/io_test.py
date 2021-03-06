import os
import unittest.mock as mock
from unittest import TestCase

from esrally.utils import io


def mock_debian(args, fallback=None):
    if args[0] == "update-alternatives":
        return [
            "/usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java",
            "/usr/lib/jvm/java-7-oracle/jre/bin/java",
            "/usr/lib/jvm/java-8-oracle/jre/bin/java"
        ]
    else:
        return fallback


def mock_red_hat(path):
    if path == "/etc/alternatives/java_sdk_1.8.0":
        return "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.91-5.b14.fc23.x86_64"
    else:
        return None


def runner(return_value):
    if return_value:
        return lambda args, fallback=None: [return_value]
    else:
        return lambda args, fallback=None: None


class IoTests(TestCase):
    def test_guess_java_home_on_mac_os_x(self):
        java_home = io.guess_java_home(major_version=8, runner=runner("/Library/Java/JavaVirtualMachines/jdk1.8.0_74.jdk/Contents/Home"))
        self.assertEqual("/Library/Java/JavaVirtualMachines/jdk1.8.0_74.jdk/Contents/Home", java_home)

        java_home = io.guess_java_home(major_version=9, runner=runner("/Library/Java/JavaVirtualMachines/jdk-9.jdk/Contents/Home"))
        self.assertEqual("/Library/Java/JavaVirtualMachines/jdk-9.jdk/Contents/Home", java_home)

    def test_guess_java_home_on_debian(self):
        self.assertEqual("/usr/lib/jvm/java-8-oracle", io.guess_java_home(major_version=8, runner=mock_debian))
        self.assertEqual("/usr/lib/jvm/java-7-openjdk-amd64", io.guess_java_home(major_version=7, runner=mock_debian))

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.islink")
    def test_guess_java_home_on_redhat(self, islink, isdir):
        islink.return_value = False
        isdir.return_value = True

        self.assertEqual("/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.91-5.b14.fc23.x86_64",
                         io.guess_java_home(major_version=8, runner=runner(None), read_symlink=mock_red_hat))
        # simulate not installed version
        self.assertIsNone(io.guess_java_home(major_version=7, runner=runner(None), read_symlink=mock_red_hat))

    def test_normalize_path(self):
        self.assertEqual("/already/a/normalized/path", io.normalize_path("/already/a/normalized/path"))
        self.assertEqual("/not/normalized", io.normalize_path("/not/normalized/path/../"))
        self.assertEqual(os.getenv("HOME"), io.normalize_path("~/Documents/.."))
