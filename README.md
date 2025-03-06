# SigTempMini

Arduino pro mini based temperature sensor for the Sigfox network

Payload:
    - external temperature (from -60°C to 60°C)
    - internal temperature (from -60°C to 60°C)
    - battery voltage (from 0V to 15V)

`PAYLOAD=XXYYYZZZ` where XX is a HEX number, YYY and ZZZ too.

external temperature = hex2int(YYY)⨉120/0xFFF-60 (in °C)
internal temperature = hex2int(ZZZ)⨉120/0xFFF-60 (in °C)
battery voltage      = hex2int(XX)⨉15/0xFF

The external temperature sensor is an LM35DZ from TI (10mV/°C). The internal temperature sensor is a 1KΩ CTN(B=4887K; T0=25°C; rough calibration done in ./test_CTN).

Data can be accessed (once the Sigfox Backend is configured) from [https://backend.sigfox.com](https://backend.sigfox.com)

Any official module from the official Sigfox store should work (tested BRKWS01 and LSM100A).
- UART_RX pin (from module to arduino) is P10.
- UART_TX pin (from arduino to module) is P11.

To measure the battery voltage a 10K potentiometer is used as voltage divider with a 3.3V/15V ratio.

Schematics as follows:
