# python-bluez-peripheral-example

### To enable the peripheral mode in gatt (server mode) you must enable the experimental features of the bluez stack

*  Edit the file ***/lib/systemd/system/bluetooth.service*** and at the ***ExecStart=/usr/local/libexec/bluetooth/bluetoothd*** add at the end ***--experimental***
*  Then do a ***sudo systemctl daemon-reload***
*  And then a ***sudo systemctl restart bluetooth***
