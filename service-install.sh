#!/bin/bash

cp /meterreading/service-config /etc/systemd/system/readmeter.service
systemctl daemon-reload

systemctl enable readmeter.service
service readmeter start

service readmeter status
