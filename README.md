# RS-STM32WB5MMG-Examples

This repo aims to provide a basic template/proof of viability for developing on (STM32WB5MMG)[https://www.st.com/en/product/stm32wb5mmg] based boards using Rust.

This repo was initially tested on (sparkfun's MicroMod STM32WB5MMG)[https://learn.sparkfun.com/tutorials/micromod-stm32wb5mmg-hookup-guide/introduction], thus the use of `pa2` as the default LED blink pin.


## Setup
Run the following to install the rust toolchain for the target architecture:
```bash
rustup target add thumbv7em-none-eabihf
```

If you would like to upload firmware via dfu (via USB), you will also need to install the STM32_Programmer tool/gui from ST Microelectronics in order to get access to the `STM32_Programmer_CLI` executable. 

If this repos has not been run or built on your host architecture before, you will/may need to update the `PLATFORM_STMPROG_DEFAULT_BIN_PATHS` to add the path to the `STM32_Programmer_CLI` executable. (see the `dfu-upload.py` file for more info)


## To Upload Firmware (with dfu)
With USB plugged into your stm32wb5mmg board:
- press and hold the boot button
- then click and release the reset button before releasing the boot button
- now run `cargo build`
- and run `py dfu-upload.py`

*(note: in the embedded space, "DFU" generally stands for "Device Firmware Updgrade"; the STM32 line of microcontrollers come with DFU capable bootloaders baked-in)*

## Of Note 
Helpful info and some differences in this repo from plain rust
- The `.cargo/config.toml` file is used to specify the target architecture and linker scripts necessary for the STM32WB5MMG, it *may* (?) require enableing other linker scripts depending on what crates you depend on
- The target architecture for the STM32WB5MMG is `thumbv7em-none-eabihf` which is a Cortex-M4F with hardware floating point support.
- The `STM32WB-hal` crate is what provides a lot of the support, the appropriate MEMORY.x file, several linker scripts, etc that enable rust for this device. (thank you (@eupn)[https://github.com/eupn])

## Notes Maintaining this repo
- Where possible, please:
  - inlcude a comment when noticed something where it is non-intuitive or you found you had to look it up.
  - use the latest stable version of rust
  - it is better for code/comments to be correct than to be concise
- PRs are welcome! please / always:
  - include a description of what you are changing and the **why**.
  - use rustfmt or `cargo fmt` to format your code before submitting a PR. 
    (To each their own, I like to integrate this into my editor's format on save functionality ~@TG-Techie)
- I've included the Cargo.lock file in this repo, this seems to be up for debate if this best practice in embedded rust projects, but it is helpful for others to be able to reproduce the same build environment. (fwiw, oxide computer company does it 😅 ~@TG-Techie)


## Copyright / Licensing
This repo is availbe under the (MIT license)[https://opensource.org/license/mit/], please see the LICENSE.MD file for more information.


## Not Yet Tested / Todos
- [ ] Setup the mcu to run at a higher (more "normal") clock speed
- [ ] Test this repo's with a jlink or st-link brand programmer/debugger
- [ ] Make this a workspace to...
  - [ ] use (xtask)[https://github.com/matklad/cargo-xtask] to replace the `dfu-upload.py` script with a rust implementation (b/c rust 😊), ideally using a rust-based dfu upload tool.
  - [ ] Add examples for bluetooth
  - [ ] Add examples for USB