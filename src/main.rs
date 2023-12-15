//

#![no_std]
#![no_main]

use cortex_m_rt as rt;
use panic_halt as _;
use stm32wb_hal as hal;

use cortex_m_rt::entry;

use stm32wb_hal::prelude::*;

use hal::delay::Delay;

const DELAY_DURATION_MS: u32 = 500;

#[entry]
fn main() -> ! {
    let cp = cortex_m::Peripherals::take().unwrap();
    let dp = hal::stm32::Peripherals::take().unwrap();

    // Use default clock frequency of 4 MHz running from MSI
    let mut rcc = dp.RCC.constrain();

    let mut gpioa = dp.GPIOA.split(&mut rcc);

    let mut led = gpioa
        .pa2
        .into_push_pull_output(&mut gpioa.moder, &mut gpioa.otyper);

    let mut timer = Delay::new(cp.SYST, hal::rcc::Clocks::default());

    loop {
        led.set_high().unwrap();
        timer.delay_ms(DELAY_DURATION_MS);
        led.set_low().unwrap();
        timer.delay_ms(DELAY_DURATION_MS);
    }
}

#[allow(non_snake_case)] // this flag is needed since the names of specific functions are important for exception handlers (🤦‍♂️🤷‍♂️ ~TG-Techie)
mod exception_handlers {
    use super::rt::{exception, ExceptionFrame};

    #[exception] // the name of the function specifies what kind of exceptio it handles
    fn HardFault(ef: &ExceptionFrame) -> ! {
        panic!("{:#?}", ef);
    }
}
