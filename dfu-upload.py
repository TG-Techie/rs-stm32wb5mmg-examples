#!/bin/python3

"""
Author: Jonah Y-M (@TG-Techie)
Copyright: This file is released under the MIT license, please see the LICENSE.md file for further details.

find the binary generated by cargo and upload it via dfu, 
where possible use python features that are cross-OS compatile.

In short, this script will:
- find the binary for the given build profile
- copy the binary to a temporary directory and add the `.elf` extension
- upload the binary with stm32_programmer_cli

USE TYPE-HINTS PLEASE! ~@TG-Techie

"""
from __future__ import annotations

import os
import sys
import time
import shutil
from pathlib import Path
from tempfile import mkdtemp


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import NoReturn, Final


def main():
    bin_path = copy_bin_and_add_extension(
        select_build_to_upload(),
        add_extension="elf",
    )
    print(f"uploading {bin_path.name=} ...")
    upload_file_via_stm32_programmer_cli(bin_path)


NAME_OF_THIS_UTIL = __file__.split("/")[-1]

PLATFORM_STMPROG_DEFAULT_BIN_PATHS = {
    # NOTE: the path to the stm32_programmer_cli binary is relative to the location of
    # the STM32CubeProgrammer.app bundle because *reasons* (it depends on files in the
    # bundle positioned relative to the binary, if not more)
    "darwin": "/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin/STM32_Programmer_CLI"
    # format = ` sys.platform : "path/to/stm32_programmer_cli/on/that/platform" `,
}

# see if the default path for the stm32_programmer_cli binary has been added for this platform
if PLATFORM_STMPROG_DEFAULT_BIN_PATHS.get(sys.platform) is not None:
    STM32_PROGRAMMER_CLI: Final = PLATFORM_STMPROG_DEFAULT_BIN_PATHS[sys.platform]
else:
    raise NotImplementedError(
        f"The default location for the  STM32_Programmer_CLI has not been added for this platform yet ({sys.platform=}), please add the path ti the stm32_programmer_cli binary (note )"
    )

# check that the toml binary exists
try:
    import toml  # toml-0.10.2
except Exception as import_err:
    raise RuntimeError("please pip install the `toml` package") from import_err


def get_cargo_build_target_triple() -> str:
    """
    get the target binary architecture from the cargo config file
    NOTE: a "triple" is the term used to describe common format that specifies a processor architecture, vendor, system, operating environment, etc. ex: thumbv7em-none-eabihf,
    read more here: https://clang.llvm.org/docs/CrossCompilation.html#target-triple
    """
    with open(".cargo/config.toml") as cargo_config:
        config = toml.load(cargo_config)

    triple = config["build"]["target"]

    assert isinstance(
        triple, str
    ), f"the build target in `.cargo/config.toml`target is not a string, found {type(triple)=}"

    return triple


def get_pacakge_name() -> str:
    """
    get the package name from the cargo config file
    """
    with open("Cargo.toml") as cargo_file:
        cargo = toml.load(cargo_file)

    package = cargo.get("package")
    assert isinstance(
        package, dict
    ), f"the package in `Cargo.toml` if missing or of the wrong type"

    name = package.get("name")

    if name is None:
        raise RuntimeError(
            "the package name in `Cargo.toml` is missing (why and/out how? ~TG-Techie)"
        )
    assert isinstance(
        name, str
    ), f"the package name in `Cargo.toml` is not a string, found {type(name)=}"

    return name


def get_build_outputs() -> dict[str, Path]:
    # cargo places teh build output in `./target/{triple}/{build_profile}/{binary_name}`
    triple = get_cargo_build_target_triple()
    package_name = get_pacakge_name()

    build_output_dir = Path(f"./target/{triple}/")
    assert (
        build_output_dir.is_dir()
    ), f"the build output directory for the {triple} build target does not exist"

    # for each build profile, get the binary by the name of the package
    build_outputs = {}
    for build_profile in build_output_dir.iterdir():
        if not build_profile.is_dir():
            continue

        binary_path = build_profile / package_name
        if not binary_path.exists() or not binary_path.is_file():
            continue

        build_outputs[build_profile.name] = binary_path

    return build_outputs


def get_arg_option(option_name: str, *, shortcut: str | None = None) -> tuple[str, ...]:
    """
    get the build profile from the command line arguments.
    searches for all arguments that start with `--{full_name}=` or `-short_name=` (if provided)
    """

    wrapped_full_name: Final = f"--{option_name}"
    # if the short name is not provided, then it is the same as the full name
    wrapped_short_name: Final = (
        wrapped_full_name if shortcut is None else f"-{shortcut}"
    )

    args = tuple(
        arg
        for arg in sys.argv
        if arg.startswith(wrapped_full_name) or arg.startswith(wrapped_short_name)
    )

    # remove the `--full_name` or `-short_name` from the start of the argument
    return tuple(arg.split("=", 1)[1] for arg in args)


def select_build_to_upload(builds: dict[str, Path] | None = None) -> Path:
    """
    main function
    """
    builds: Final = builds or get_build_outputs()

    profiles: Final = get_arg_option("profile", shortcut="p") or None

    if profiles is not None and len(profiles) > 1:
        error(
            (
                f"ERROR: multiple build profiles specified {profiles}"
                f"\n    please specify only one build profile when calling {NAME_OF_THIS_UTIL}"
            )
        )

    selected_profile = profiles[0] if profiles is not None else None

    if len(builds) == 0:
        error("no build outputs found, pleae `cargo build` before running")
    elif len(builds) == 1 and selected_profile is None:
        (selected_profile,) = builds.keys()
        print(f"uploading {selected_profile} build profile")
    elif len(builds) > 1 and selected_profile is None:
        error(
            (
                f"ERROR: multiple output profiles found: {set(builds.keys())}"
                f"\n    please specify a build profile when calling {NAME_OF_THIS_UTIL}"
                f"\n    example: `{NAME_OF_THIS_UTIL} --profile=release`"
            )
        )

    assert selected_profile is not None

    if selected_profile not in builds:
        error(
            (
                f"ERROR: the build profile `{selected_profile}` was not found"
                f"\n    please build the project with the profile you want to upload "
                f"\n    (did find {set(builds.keys())})"
            )
        )

    return builds[selected_profile]


def copy_and_rename_file_to_tempdir(file_path: Path) -> Path:
    raise NotImplementedError


def copy_bin_and_add_extension(
    bin_path: Path,
    *,
    add_extension: str | None,
) -> Path:
    """
    main function
    """

    destination = f"{mkdtemp()}/{bin_path.name}"
    if add_extension is not None:
        destination += f".{add_extension}"

    print(f"{destination=}")

    with bin_path.open("rb") as b:
        with open(destination, "wb") as d:
            shutil.copyfileobj(b, d)

    return Path(destination)


def upload_file_via_stm32_programmer_cli(file_path: Path) -> int:
    print(f"{str(file_path.absolute())=}")

    assert file_path.exists(), f"the file to upload does not exist {file_path=}"
    assert file_path.is_file(), f"the file to upload is not a file {file_path=}"
    print(file_path.name)

    return os.system(
        " ".join(
            (
                STM32_PROGRAMMER_CLI,
                # --- upload via dfu ---
                "--connect",
                "port=usb1",
                # --- the file to upload ---
                "--write",
                str(file_path.absolute()),
                # --- reset the board after upload ---
                "--start",
            )
        )
    )


def error(msg: str) -> NoReturn:
    print(msg)
    exit(1)


if __name__ == "__main__":
    main()
