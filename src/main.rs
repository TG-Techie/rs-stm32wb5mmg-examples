//

#![no_std]
#![no_main]

use cortex_m_rt as rt; // "rt" stands for "runtime"
use panic_halt as _; // this provides a panic handler, this is required for rust
use stm32wb_hal as hal; // "hal" stands for "hardware abstraction layer"
                        // it is convention to use "hal" instead of the full package name

use cortex_m_rt::entry; // since we're using #![no_main] this defines where the program starts

use hal::delay::Delay;
use hal::prelude::*;

const DELAY_DURATION_MS: u32 = 500;

#[entry]
fn main() -> ! {
    let core_peripherals = cortex_m::Peripherals::take().unwrap();
    let device_peripherals = hal::stm32::Peripherals::take().unwrap();

    // This sets up the clock but only for a basic 4MHz HSI clock
    // "HSI"clock stands for "High Speed Internal" clock (non-standard abbreviation)
    // "rcc" stands for" Reset and Clock Control" (non-standard abbreviation)
    let mut rcc = device_peripherals.RCC.constrain();

    let mut gpioa = device_peripherals.GPIOA.split(&mut rcc);

    let mut led = gpioa
        .pa2 // the default pin for the LED on sparkfun's MicroMod STM32WB5MMG Processor board
        .into_push_pull_output(&mut gpioa.moder, &mut gpioa.otyper);

    let mut timer = Delay::new(core_peripherals.SYST, hal::rcc::Clocks::default());

    loop {
        led.set_high().unwrap();
        timer.delay_ms(DELAY_DURATION_MS);
        led.set_low().unwrap();
        timer.delay_ms(DELAY_DURATION_MS);
    }
}

#[allow(non_snake_case)]
// the non_snake_case flag is needed since the names of specific functions are important for exception handlers (🤦‍♂️🤷‍♂️ ~TG-Techie)
mod exception_handlers {
    use super::rt::{exception, ExceptionFrame};

    #[exception] // the name of the function specifies what kind of exceptio it handles
    fn HardFault(ef: &ExceptionFrame) -> ! {
        panic!("{:#?}", ef);
    }
}
