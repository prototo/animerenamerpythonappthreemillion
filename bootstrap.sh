#!/usr/bin/env bash

pacman -Sy --noconfirm python python-pip sqlite
pip install -r /vagrant/requirements.txt
