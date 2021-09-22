#!/bin/bash

cp /meterreading/service-config /etc/systemd/system/readmeter.service
cp /meterreading/service-lights-config /etc/systemd/system/meterlights.service
systemctl daemon-reload

systemctl enable readmeter.service
systemctl enable meterlights.service
service readmeter start
service meterlights start

service readmeter status
service meterlights status
