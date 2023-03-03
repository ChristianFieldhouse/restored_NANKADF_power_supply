# restored_NANKADF_power_supply
Code (+datasheets) used to restore a NANKADF power supply whose MCU I blew up

In trying to make my power supply programmable by generating rotary encoders, I somehow created a short via the MCU, killing it.
The power supply was just screeching. I removed the old MCU and replaced with a Pi Pico, gradually deducing how all the pins were used.

I used some python controlling my Rigol scope to callibrate the power supply.

The PCB in question:
![PXL_20230219_161521581](https://user-images.githubusercontent.com/48842799/221349943-d821627b-e95d-407b-93a6-d54e3ee1d454.jpg)

I 3d printed a place for it to live, and added a usb-b in the blank usb-b hole in the housing.
![PXL_20230225_092546042](https://user-images.githubusercontent.com/48842799/221349996-9eee7f29-c4fc-4afc-97b4-8a7150100380.jpg)
That just works as a micropython terminal.

I believe I've restored all functionality except Overcurrent Protection (which isn't difficult but I just haven't done it). I've also added
my own startup screen (+sound) since it's all really easy to reprogram now
![PXL_20230225_092518252](https://user-images.githubusercontent.com/48842799/221349628-57097e6c-088e-4c6b-b9ec-782283ec3361.jpg)
