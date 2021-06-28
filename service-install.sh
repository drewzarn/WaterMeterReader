#!/bin/bash

ln -s /meterreading/service-config /lib/systemd/system/readmeter.service
systemctl daemon-reload

systemctl start readmeter.service
systemctl enable readmeter.service

systemctl status readmeter